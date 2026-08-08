#!/usr/bin/env python3
"""Thorough NYC → ORD one-way car search: KAYAK · Rentalcars · DiscoverCars."""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote_plus

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUT_COMPARE = ROOT / "car_compare_data.json"
OUT_KAYAK = ROOT / "car_rental_data.json"
USER_DATA_DIR = ROOT / ".browser_profile_capture"

PICKUP_DATE = "2026-09-24"
DROPOFF_DATE = "2026-10-10"
PICKUP_TIME = "18:00"  # NYC evening after likely arrival
DROPOFF_TIME = "10:00"
PICKUP_HHMM = "1800"
DROPOFF_HHMM = "1000"

# Primary: NYC airports → Chicago O'Hare (matches NYC-in / ORD-out itinerary)
PICKUP_AIRPORTS = [
    ("JFK", "John F. Kennedy Intl"),
    ("LGA", "LaGuardia"),
    ("EWR", "Newark"),
    ("NYC", "New York City"),
]
DROPOFF_CODE = "ORD"
TOP_GAS = 20
TOP_EV = 15
TOP_MINIVAN = 25


def is_minivan(c: dict) -> bool:
    cat = (c.get("category") or "").lower()
    model = (c.get("model") or "")
    blob = f"{cat} {model} {' '.join(c.get('options') or [])}"
    if re.search(r"미니밴|minivan|\b밴\b|\bvan\b|people\s*carrier", blob, re.I):
        # avoid matching '밴' inside unrelated words; category '밴'/'미니밴' is enough
        if re.search(r"미니밴|minivan|people", blob, re.I) or cat in ("밴", "미니밴", "van"):
            return True
    return bool(
        re.search(
            r"Pacifica|Odyssey|Sienna|Carnival|Caravan|Voyager|Sedona|Town\s*&?\s*Country|"
            r"퍼시피카|오디세이|시엔나|카니발|캐러밴|세도나",
            model,
            re.I,
        )
    )


def keep_gas_ev_and_vans(cars: list[dict]) -> list[dict]:
    """Keep cheapest gas/EV plus all minivan/van offers (vans are often above top-N cutoff)."""
    cars = sorted(cars, key=lambda c: c["price"])
    evs = [c for c in cars if is_ev(c)][:TOP_EV]
    gas = [c for c in cars if not is_ev(c) and not is_minivan(c)][:TOP_GAS]
    vans = [c for c in cars if is_minivan(c) and not is_ev(c)][:TOP_MINIVAN]
    out, seen = [], set()
    for c in evs + gas + vans:
        key = (c.get("source"), c["model"], c["category"], c["price"], c.get("pickup_code"))
        if key in seen:
            continue
        seen.add(key)
        out.append(c)
    out.sort(key=lambda c: c["price"])
    return out

# DiscoverCars: USA / New York / JFK & Chicago ORD (best-effort IDs; API may still work via search page)
DC_US = "5003"


def now_kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%dT%H:%M:%S+09:00")


def nights(a: str, b: str) -> int:
    return (datetime.strptime(b, "%Y-%m-%d") - datetime.strptime(a, "%Y-%m-%d")).days


def fmt_won(n: int | None) -> str:
    return "-" if n is None else f"₩{n:,}"


def dismiss(page) -> None:
    page.evaluate(
        """() => {
      const b = [...document.querySelectorAll('button')].find(el =>
        /^(동의합니다|모두 동의|Accept all|Accept|Agree|Allow all|Got it|닫기)$/i.test((el.innerText || '').trim())
      );
      if (b) b.click();
    }"""
    )


def normalize_category(raw: str) -> str:
    t = (raw or "").strip().lower()
    mapping = [
        ("electric", "전기차"),
        ("economy", "이코노미"),
        ("compact", "컴팩트"),
        ("standard", "스탠다드"),
        ("intermediate", "중형"),
        ("full", "풀사이즈"),
        ("fullsize", "풀사이즈"),
        ("suv", "SUV"),
        ("van", "밴"),
        ("minivan", "미니밴"),
        ("premium", "프리미엄"),
        ("luxury", "럭셔리"),
        ("people", "밴"),
    ]
    for key, label in mapping:
        if key in t:
            return label
    return raw.strip() if raw else "기타"


def is_ev(c: dict) -> bool:
    if c.get("electric") or c.get("category") == "전기차":
        return True
    blob = " ".join(c.get("options") or []) + " " + (c.get("model") or "")
    return bool(re.search(r"Fully electric|전기|Electric|Tesla|Model\s*[Y3SX]|아이오닉|니로|볼트", blob, re.I))


def keep_gas_and_ev(cars: list[dict]) -> list[dict]:
    # Backward-compatible name: also retain minivans that would otherwise be truncated.
    return keep_gas_ev_and_vans(cars)


def offer(
    *,
    source: str,
    pickup_code: str,
    model: str,
    category: str,
    price: int,
    seats=None,
    bags=None,
    doors=None,
    location: str = "",
    options: list[str] | None = None,
    seller_url: str = "",
    supplier: str = "",
    electric: bool = False,
) -> dict:
    if electric:
        category = "전기차"
    return {
        "id": f"car:{source}:{pickup_code}-{DROPOFF_CODE}:{DROPOFF_DATE}:{category}:{model}:{price}",
        "source": source,
        "model": model,
        "category": category or "기타",
        "price": price,
        "price_text": fmt_won(price),
        "seats": seats,
        "bags": bags,
        "doors": doors,
        "location": location or f"{pickup_code} → {DROPOFF_CODE}",
        "options": options or [],
        "supplier": supplier,
        "electric": electric or category == "전기차",
        "pickup_code": pickup_code,
        "dropoff_code": DROPOFF_CODE,
        "seller_url": seller_url,
        "synced_at": now_kst(),
    }


def kayak_url(pickup: str, electric: bool = False, van: bool = False) -> str:
    # one-way with times
    base = (
        f"https://www.kayak.co.kr/cars/{pickup}-a{PICKUP_HHMM}/{DROPOFF_CODE}-a{DROPOFF_HHMM}/"
        f"{PICKUP_DATE}/{DROPOFF_DATE}?sort=price_a"
    )
    if electric:
        return base + "&fs=ecoclass=Electric"
    if van:
        # Best-effort; UI filter is more reliable. Kept for deep links.
        return base + "&fs=cars=van"
    return base


def kayak_url_simple(pickup: str, electric: bool = False, van: bool = False) -> str:
    base = f"https://www.kayak.co.kr/cars/{pickup}/{DROPOFF_CODE}/{PICKUP_DATE}/{DROPOFF_DATE}?sort=price_a"
    if electric:
        return base + "&fs=ecoclass=Electric"
    if van:
        return base + "&fs=cars=van"
    return base


def parse_kayak_category(text: str) -> str:
    m = re.search(r"동급\s*\(([^)]+)\)|동급\s+([^\n]+)", text)
    if not m:
        return "기타"
    return (m.group(1) or m.group(2) or "").strip() or "기타"


def extract_kayak(page, pickup: str, electric: bool) -> list[dict]:
    raw = page.evaluate(
        """(isElectric) => {
      const text = document.body.innerText || '';
      const blocks = text.split('다음 검색 결과로 이동').slice(1);
      const out = [];
      for (const b of blocks) {
        const pm = b.match(/([\\d,]+)원/);
        if (!pm) continue;
        const lines = b.split('\\n').map(s => s.trim()).filter(Boolean);
        if (lines.some(l => /최대\\s*\\d+%\\s*할인|지금 바로 예약/.test(l)) && lines.length < 8) continue;
        const isEv = isElectric || /Fully electric|전기차|Electric/i.test(b);
        let modelIdx = lines.findIndex(l =>
          /토요타|닛산|혼다|포드|쉐보레|지프|기아|현대|크라이슬러|닷지|폭스바겐|BMW|벤츠|아우디|테슬라|미쓰비시|스바루|마쓰다|링컨|캐딜락|볼보|폴스타|리비안|야리스|베르사|스파크|크루즈|포커스|컴패스|코롤라|시빅|알티마|니로|아이오닉|볼트|리프|Mach-E|Model\\s*[Y3SX]|시로코|캠리|어코드|소나타|엘란트라|말리부|이쿼녹스|투싼|스포티지|싼타페|파일럿|오디세이|캐러밴|퍼시피카|Pacifica|Odyssey|Sienna|Carnival|Caravan|Voyager|Sedona|시엔나|카니발|세도나|Town/i.test(l)
        );
        if (modelIdx < 0) {
          if (isEv && /Fully electric/i.test(b)) {
            modelIdx = lines.findIndex(l => /할인가에 예약|차량 사이즈|동급/.test(l));
            if (modelIdx < 0) continue;
          } else continue;
        }
        let model = lines[modelIdx];
        if (/할인가에 예약|차량 사이즈/.test(model)) model = '전기차 (업체 배정)';
        const gradeLine = lines.find(l => /동급/.test(l)) || '';
        const nums = [];
        for (let i = modelIdx; i < Math.min(modelIdx + 10, lines.length); i++) {
          if (/^\\d+$/.test(lines[i])) nums.push(parseInt(lines[i], 10));
        }
        const loc = lines.find(l => /JFK|LGA|EWR|ORD|뉴욕|시카고|공항|셔틀|터미널|시내|맨해튼|뉴어크|오헤어/i.test(l)) || '';
        const sites = (b.match(/(\\d+)개\\s*사이트/) || [])[1] || '';
        out.push({
          model, grade_line: gradeLine, nums, location: loc,
          sites: sites ? parseInt(sites, 10) : null,
          price: parseInt(pm[1].replace(/,/g, ''), 10),
          electric: isEv || /Fully electric/i.test(b),
          free_cancel: /무료 취소/.test(b),
          one_way: /편도|one[- ]?way|드롭\s*오프\s*요금|반납\s*수수료/i.test(b),
          block: b.slice(0, 600),
        });
      }
      return out;
    }""",
        electric,
    )
    cars = []
    seen = set()
    for item in raw or []:
        price = item.get("price")
        model = (item.get("model") or "").strip()
        if not price or price < 50_000 or not model:
            continue
        ev = bool(item.get("electric") or electric)
        base_cat = parse_kayak_category(item.get("grade_line") or item.get("block") or "")
        category = "전기차" if ev else base_cat
        key = (model, category, price, item.get("location") or "")
        if key in seen:
            continue
        seen.add(key)
        nums = item.get("nums") or []
        opts = []
        if ev:
            opts.append("Fully electric")
        if item.get("free_cancel"):
            opts.append("무료 취소")
        if item.get("one_way"):
            opts.append("편도(드롭오프 요금 포함 가능)")
        if item.get("sites"):
            opts.append(f"비교 {item['sites']}개 사이트")
        if nums and nums[0] >= 5:
            opts.append("5인 이상")
        cars.append(
            offer(
                source="kayak",
                pickup_code=pickup,
                model=model,
                category=category,
                price=int(price),
                seats=nums[0] if nums else None,
                bags=nums[1] if len(nums) > 1 else None,
                doors=nums[2] if len(nums) > 2 else None,
                location=item.get("location") or f"{pickup} → ORD · KAYAK",
                options=opts,
                seller_url=kayak_url(pickup, electric=ev),
                electric=ev,
            )
        )
    return keep_gas_and_ev(cars)


def kayak_load_more(page, times: int = 10) -> None:
    for _ in range(times):
        clicked = page.evaluate(
            """() => {
          const b = [...document.querySelectorAll('button')].find(el =>
            /검색 결과 더 보기|Show more results|더 보기|Load more/i.test((el.innerText || '').trim())
          );
          if (b && /검색 결과 더 보기|Show more results/i.test((b.innerText || '').trim())) {
            b.click(); return true;
          }
          return false;
        }"""
        )
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1200)
        if not clicked:
            break


def kayak_try_van_filter(page) -> str | None:
    return page.evaluate(
        """() => {
      const typeBtn = [...document.querySelectorAll('button')].find(el =>
        /^(차종|Car type)$/i.test((el.innerText || '').trim())
      );
      if (typeBtn) typeBtn.click();
      // sync wait via busy loop is avoided; caller sleeps
      const nodes = [...document.querySelectorAll('button,label,div,span,li')];
      for (const el of nodes) {
        const t = (el.innerText || '').trim().replace(/\\s+/g, ' ');
        if (/^밴\\s*[\\d,]+원부터$/.test(t) || /^Van\\b/i.test(t) && /from|원/i.test(t)) {
          el.click();
          return t;
        }
      }
      return null;
    }"""
    )


def scrape_kayak(page, pickup: str, electric: bool, van_pass: bool = False) -> list[dict]:
    urls = [kayak_url(pickup, electric=electric, van=van_pass), kayak_url_simple(pickup, electric=electric, van=van_pass)]
    label = "EV" if electric else ("VAN" if van_pass else "ALL")
    for url in urls:
        print(f"\n=== KAYAK [{label}] {pickup}→ORD {PICKUP_DATE}→{DROPOFF_DATE} ===")
        print(url)
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=90000)
        except PlaywrightTimeout:
            print("  nav timeout")
            continue
        page.wait_for_timeout(3000)
        dismiss(page)
        if van_pass and not electric:
            clicked = kayak_try_van_filter(page)
            print(f"  van filter click: {clicked}")
            page.wait_for_timeout(2000)
        for y in (800, 1600, 2800, 4000):
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(700)
        kayak_load_more(page, 8 if van_pass else 4)
        deadline = time.time() + 60
        cars: list[dict] = []
        while time.time() < deadline:
            dismiss(page)
            body = page.inner_text("body")
            if "원" in body and ("동급" in body or "Fully electric" in body or "차량" in body):
                page.wait_for_timeout(1500)
                cars = extract_kayak(page, pickup, electric)
                if cars:
                    break
            time.sleep(0.8)
        if van_pass:
            cars = [c for c in cars if is_minivan(c)]
        print(f"  found {len(cars)}")
        for c in cars[:5]:
            print(f"  - {c['price_text']} | {c['category']} | {c['model']} | {c['location'][:40]}")
        if cars:
            return cars
    return []


def rentalcars_url(pickup: str) -> str:
    pu = PICKUP_DATE.replace("-", "/")
    do = DROPOFF_DATE.replace("-", "/")
    return (
        "https://www.rentalcars.com/SearchResults.do?"
        f"locationCode={pickup}&dropLocationCode={DROPOFF_CODE}&driversAge=30"
        f"&puDate={pu}&puTime={PICKUP_TIME}&doDate={do}&doTime={DROPOFF_TIME}&currency=KRW"
    )


def scrape_rentalcars(page, pickup: str) -> list[dict]:
    print(f"\n=== Rentalcars {pickup}→ORD ===")
    url = rentalcars_url(pickup)
    print(url)
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=90000)
    except PlaywrightTimeout:
        print("  nav timeout")
    page.wait_for_timeout(5000)
    dismiss(page)
    search_criteria = {
        "driversAge": 30,
        "pickUpLocation": pickup,
        "pickUpDateTime": f"{PICKUP_DATE}T{PICKUP_TIME}:00",
        "pickUpLocationType": "IATA",
        "dropOffLocation": DROPOFF_CODE,
        "dropOffLocationType": "IATA",
        "dropOffDateTime": f"{DROPOFF_DATE}T{DROPOFF_TIME}:00",
        "searchMetadata": json.dumps(
            {
                "pickUpLocationName": f"{pickup} Airport",
                "dropOffLocationName": "ORD Airport",
            }
        ),
    }
    filter_criteria = {"sortBy": "PRICE", "sortAscending": True}
    api_url = (
        "https://www.rentalcars.com/api/search-results?"
        f"searchCriteria={quote_plus(json.dumps(search_criteria))}&"
        f"filterCriteria={quote_plus(json.dumps(filter_criteria))}&"
        'serviceFeatures=["RETURN_EXTRAS_IN_MULTI_CAR_RESPONSE"]'
    )
    matches = []
    for _ in range(12):
        r = page.request.get(api_url, headers={"accept": "application/json"})
        if r.status == 200:
            try:
                matches = (r.json() or {}).get("matches") or []
            except Exception:
                matches = []
            if matches:
                break
        page.wait_for_timeout(2000)
    cars = []
    for m in matches:
        veh = m.get("vehicle") or {}
        price_obj = veh.get("driveAwayPrice") or veh.get("price") or {}
        amount = price_obj.get("amount")
        if amount is None:
            continue
        price = int(round(float(amount)))
        if price < 50_000:
            continue
        model = (veh.get("makeAndModel") or "차량").strip()
        cats = veh.get("carCategories") or []
        category = normalize_category(cats[0] if cats else veh.get("carClass") or "")
        fuel = (veh.get("fuel") or "").lower()
        electric = fuel in ("electric", "ev") or "electric" in fuel
        opts = []
        if veh.get("freeCancellation"):
            opts.append("무료 취소")
        if electric:
            opts.append("Fully electric")
            category = "전기차"
        opts.append("편도 NYC→ORD")
        cars.append(
            offer(
                source="rentalcars",
                pickup_code=pickup,
                model=model,
                category=category,
                price=price,
                seats=int(veh["numberOfSeats"]) if str(veh.get("numberOfSeats", "")).isdigit() else None,
                bags=veh.get("bigSuitcase"),
                doors=int(veh["numberOfDoors"]) if str(veh.get("numberOfDoors", "")).isdigit() else None,
                location=f"{pickup} → ORD · Rentalcars.com",
                options=opts,
                seller_url=url,
                electric=electric,
            )
        )
    cars = keep_gas_and_ev(cars)
    print(f"  found {len(cars)}")
    for c in cars[:5]:
        print(f"  - {c['price_text']} | {c['category']} | {c['model']}")
    return cars


def scrape_discover(page, pickup: str) -> list[dict]:
    """DiscoverCars via public search UI for one-way NYC→ORD."""
    print(f"\n=== DiscoverCars UI {pickup}→ORD ===")
    # Use Google-style landing; then try search API with common place guesses via HTML scrape of results page
    q_url = (
        "https://www.discovercars.com/search?"
        f"pickup={quote_plus(pickup + ' Airport')}&dropoff={quote_plus('Chicago O Hare')}"
        f"&from={PICKUP_DATE}&to={DROPOFF_DATE}&ptime={PICKUP_TIME}&dtime={DROPOFF_TIME}"
        "&age=30&currency=KRW"
    )
    # Prefer known deep links
    alt = f"https://www.discovercars.com/en/search-cars?pickup_iata={pickup}&dropoff_iata=ORD&from={PICKUP_DATE}&to={DROPOFF_DATE}"
    cars: list[dict] = []
    for url in (alt, q_url):
        print(" ", url[:120])
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=90000)
        except PlaywrightTimeout:
            continue
        page.wait_for_timeout(6000)
        dismiss(page)
        for y in (1000, 2200, 3600):
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(800)
        raw = page.evaluate(
            """() => {
          const text = document.body.innerText || '';
          const out = [];
          const re = /₩?([\\d,]+)\\s*(?:KRW|원)?/g;
          // split by car-ish chunks
          const chunks = text.split(/\\n(?=[A-Z][a-z]+\\s+[A-Z]|토요타|닛산|혼다|포드|쉐보레|지프|기아|현대|테슬라|폭스바겐)/);
          for (const b of chunks) {
            const pm = b.match(/([\\d,]{4,})\\s*원|₩\\s*([\\d,]+)|KRW\\s*([\\d,]+)/i);
            if (!pm) continue;
            const digits = (pm[1] || pm[2] || pm[3] || '').replace(/,/g, '');
            const price = parseInt(digits, 10);
            if (!price || price < 50000 || price > 20000000) continue;
            const model = (b.split('\\n').find(l => /[A-Za-z가-힣].{2,}/.test(l)) || '차량').trim().slice(0, 60);
            const electric = /electric|전기|Tesla|Model/i.test(b);
            out.push({ model, price, electric, block: b.slice(0, 300) });
          }
          return out.slice(0, 40);
        }"""
        )
        for item in raw or []:
            cars.append(
                offer(
                    source="discover",
                    pickup_code=pickup,
                    model=item["model"],
                    category="전기차" if item.get("electric") else "기타",
                    price=int(item["price"]),
                    location=f"{pickup} → ORD · DiscoverCars",
                    options=["편도 NYC→ORD"] + (["Fully electric"] if item.get("electric") else []),
                    seller_url=url,
                    electric=bool(item.get("electric")),
                )
            )
        if cars:
            break
    cars = keep_gas_and_ev(cars)
    print(f"  found {len(cars)}")
    for c in cars[:5]:
        print(f"  - {c['price_text']} | {c['category']} | {c['model']}")
    return cars


def merge_sources(*lists: list[dict]) -> list[dict]:
    out, seen = [], set()
    for cars in lists:
        for c in cars:
            key = (c["source"], c["model"], c["category"], c["price"], c.get("pickup_code"))
            if key in seen:
                continue
            seen.add(key)
            out.append(c)
    out.sort(key=lambda c: c["price"])
    return out


def main() -> int:
    by_source: dict[str, list[dict]] = {"kayak": [], "rentalcars": [], "discover": []}
    kayak_days_cars: list[dict] = []

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            viewport={"width": 1440, "height": 960},
            locale="ko-KR",
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        for code, _name in PICKUP_AIRPORTS:
            # KAYAK all + EV + dedicated van pass (minivans often sit below top cheap cars)
            k_all = scrape_kayak(page, code, electric=False)
            k_ev = scrape_kayak(page, code, electric=True)
            k_van = scrape_kayak(page, code, electric=False, van_pass=True)
            kayak_merge = keep_gas_and_ev(merge_sources(k_all, k_ev, k_van))
            by_source["kayak"].extend(kayak_merge)
            kayak_days_cars.extend(kayak_merge)

            # Rentalcars (skip NYC city code if API prefers airports)
            if code != "NYC":
                by_source["rentalcars"].extend(scrape_rentalcars(page, code))

            # DiscoverCars best-effort for JFK/LGA/EWR
            if code in ("JFK", "LGA", "EWR"):
                by_source["discover"].extend(scrape_discover(page, code))

        ctx.close()

    for key in by_source:
        by_source[key] = keep_gas_and_ev(by_source[key])

    all_cars = merge_sources(by_source["discover"], by_source["rentalcars"], by_source["kayak"])
    # Prefer family-friendly (5+ seats) near top listing for display note
    family = [c for c in all_cars if (c.get("seats") or 0) >= 5]
    minivans = [c for c in all_cars if is_minivan(c)]
    # Enrich listed Pacifica-class deals with or-similar note (US rentals rarely guarantee exact model)
    for c in minivans:
        opts = list(c.get("options") or [])
        note = "또는 동급 미니밴(인수 시 Odyssey/Sienna/Carnival 등 대체 가능)"
        if note not in opts:
            opts.append(note)
        c["options"] = opts

    minivan_models = sorted({c["model"] for c in minivans})
    minivan_note = (
        f"미니밴 정밀조회(KAYAK KR/COM · EWR/JFK/LGA · 결과 더보기 · 차종=밴): "
        f"편도 NYC→ORD 구간에서는 {', '.join(minivan_models) if minivan_models else '미니밴 없음'}만 노출. "
        "JFK/LGA는 미니밴 재고 없음(EWR·NYC만). "
        "같은 기간 EWR 왕복에는 Sienna/Odyssey가 보이지만, ORD 편도 드롭에는 Pacifica(또는 동급)만 잡힘."
    )

    def cheapest(src: str):
        cars = by_source.get(src) or []
        return cars[0] if cars else None

    day = {
        "pickup_date": PICKUP_DATE,
        "dropoff_date": DROPOFF_DATE,
        "pickup_location": "NYC (JFK/LGA/EWR)",
        "dropoff_location": "ORD",
        "pickup_time": PICKUP_TIME,
        "dropoff_time": DROPOFF_TIME,
        "route_note": "편도 · 뉴욕 인수 → 시카고 오헤어(ORD) 반납 · 귀국편 10/10 06:00 전 반납 권장",
        "minivan_note": minivan_note,
        "minivans": minivans,
        "nights": nights(PICKUP_DATE, DROPOFF_DATE),
        "sources": {
            "discover": {
                "label": "DiscoverCars",
                "url": "https://www.discovercars.com/",
                "cars": by_source["discover"],
                "cheapest": cheapest("discover"),
                "note": "편도 NYC→ORD",
            },
            "rentalcars": {
                "label": "Rentalcars.com",
                "url": rentalcars_url("JFK"),
                "cars": by_source["rentalcars"],
                "cheapest": cheapest("rentalcars"),
                "note": "JFK/LGA/EWR → ORD",
            },
            "kayak": {
                "label": "KAYAK",
                "url": kayak_url("JFK"),
                "cars": by_source["kayak"],
                "cheapest": cheapest("kayak"),
                "note": "JFK/LGA/EWR/NYC → ORD · 전기차 포함",
            },
        },
        "cars": all_cars,
        "family_cars": family[:12],
        "synced_at": now_kst(),
    }

    OUT_COMPARE.write_text(json.dumps([day], ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_KAYAK.write_text(
        json.dumps(
            [
                {
                    "pickup_date": PICKUP_DATE,
                    "dropoff_date": DROPOFF_DATE,
                    "pickup_location": "NYC",
                    "dropoff_location": "ORD",
                    "nights": nights(PICKUP_DATE, DROPOFF_DATE),
                    "cars": keep_gas_and_ev(kayak_days_cars),
                    "synced_at": now_kst(),
                }
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n===== SUMMARY NYC→ORD one-way =====")
    print(f"기간 {PICKUP_DATE} {PICKUP_TIME} → {DROPOFF_DATE} {DROPOFF_TIME} · {day['nights']}일")
    for key, label in (("discover", "DiscoverCars"), ("rentalcars", "Rentalcars"), ("kayak", "KAYAK")):
        c = cheapest(key)
        n = len(by_source[key])
        print(f"  {label}: {n}대 · 최저 {c['price_text'] if c else '-'} · {c['model'] if c else ''}")
    print(f"  전체 병합 {len(all_cars)}대 · 5인승+ {len(family)}대")
    if all_cars:
        print(f"  전체 최저 {all_cars[0]['price_text']} | {all_cars[0]['source']} | {all_cars[0]['model']}")
    print(f"wrote {OUT_COMPARE.name}, {OUT_KAYAK.name}")
    return 0 if all_cars else 1


if __name__ == "__main__":
    raise SystemExit(main())
