#!/usr/bin/env python3
"""Compare ORD car rentals: DiscoverCars · Rentalcars.com · Expedia (+ KAYAK merge)."""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote, quote_plus

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUT_FILE = ROOT / "car_compare_data.json"
KAYAK_FILE = ROOT / "car_rental_data.json"
USER_DATA_DIR = ROOT / ".browser_profile_capture"

PICKUP = "2026-09-23"
DROPOFF_DATES = [
    "2026-10-08",
    "2026-10-09",
    "2026-10-10",
    "2026-10-11",
    "2026-10-12",
    "2026-10-13",
]
TOP_PER_SOURCE = 8

# DiscoverCars Chicago O'Hare (ORD)
DC_COUNTRY_ID = "5003"
DC_CITY_ID = "4737"
DC_PLACE_ID = "4739"

# CarTrawler client IDs to try for Expedia white-label (first working wins).
# Expedia.com itself is usually bot-gated from automation.
EXPEDIA_CT_CLIENTS: list[str] = []


def now_kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%dT%H:%M:%S+09:00")


def nights(a: str, b: str) -> int:
    return (datetime.strptime(b, "%Y-%m-%d") - datetime.strptime(a, "%Y-%m-%d")).days


def fmt_won(amount: int | None) -> str:
    if amount is None:
        return "-"
    return f"₩{amount:,}"


def kayak_url(drop: str) -> str:
    return f"https://www.kayak.co.kr/cars/ORD/{PICKUP}/{drop}?sort=price_a"


def discover_url(guid: str, sq: str) -> str:
    return f"https://www.discovercars.com/en/search/{guid}?sq={sq}&currency=KRW"


def rentalcars_url(drop: str) -> str:
    return (
        "https://www.rentalcars.com/SearchResults.do?"
        f"locationCode=ORD&driversAge=30&puDate={PICKUP.replace('-', '/')}&puTime=12:00"
        f"&doDate={drop.replace('-', '/')}&doTime=12:00&currency=KRW"
    )


def expedia_url(drop: str) -> str:
    # US-format deep link (may hit bot check; still useful as booking link)
    pu = datetime.strptime(PICKUP, "%Y-%m-%d")
    do = datetime.strptime(drop, "%Y-%m-%d")
    return (
        "https://www.expedia.com/carsearch?"
        f"locn=ORD&date1={pu.month}/{pu.day}/{pu.year}&date2={do.month}/{do.day}/{do.year}"
        "&time1=1200PM&time2=1200PM"
    )


def expedia_ct_url(drop: str, client_id: str) -> str:
    return (
        f"https://cars.cartrawler.com/expedia/en/book?clientId={client_id}"
        f"&pickupIATACode=ORD&pickupDateTime={PICKUP}T12:00"
        f"&returnDateTime={drop}T12:00&residenceID=KR&currency=KRW&age=30#/vehicles"
    )


def dismiss(page) -> None:
    page.evaluate(
        """() => {
      const b = [...document.querySelectorAll('button')].find(el =>
        /^(동의합니다|모두 동의|Accept all|Accept|Agree|Allow all|Got it)$/i.test((el.innerText || '').trim())
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
        ("full_size", "풀사이즈"),
        ("suv", "SUV"),
        ("van", "밴"),
        ("minivan", "미니밴"),
        ("carrier", "밴"),
        ("premium", "프리미엄"),
        ("luxury", "럭셔리"),
        ("people", "밴"),
    ]
    for key, label in mapping:
        if key in t:
            return label
    return raw.strip() if raw else "기타"


def offer_row(
    *,
    source: str,
    drop: str,
    model: str,
    category: str,
    price: int,
    seats=None,
    bags=None,
    doors=None,
    location: str = "ORD",
    options: list[str] | None = None,
    seller_url: str = "",
    supplier: str = "",
) -> dict:
    return {
        "id": f"car:{source}:{drop}:{category}:{model}:{price}",
        "source": source,
        "model": model,
        "category": category or "기타",
        "price": price,
        "price_text": fmt_won(price),
        "seats": seats,
        "bags": bags,
        "doors": doors,
        "location": location,
        "options": options or [],
        "supplier": supplier,
        "seller_url": seller_url,
        "synced_at": now_kst(),
    }


# ---------- DiscoverCars ----------
def discover_create(page, drop: str) -> tuple[str | None, str | None]:
    form = {
        "is_drop_off": "0",
        "pick_up_country_id": DC_COUNTRY_ID,
        "pick_up_city_id": DC_CITY_ID,
        "pick_up_location_id": DC_PLACE_ID,
        "drop_off_country_id": DC_COUNTRY_ID,
        "drop_off_city_id": DC_CITY_ID,
        "drop_off_location_id": DC_PLACE_ID,
        "pickup_id": DC_PLACE_ID,
        "dropoff_id": DC_PLACE_ID,
        "pickup_from": f"{PICKUP} 12:00",
        "pickup_to": f"{drop} 12:00",
        "pick_time": "12:00",
        "drop_time": "12:00",
        "partner_id": "0",
        "exclude_locations": "0",
        "luxOnly": "0",
        "driver_age": "30",
        "residence_country": "KR",
        "abtest": "",
        "token": "",
        "recent_search": "0",
    }
    resp = page.request.post(
        "https://www.discovercars.com/en/search/create-search",
        form=form,
        headers={"accept": "application/json", "x-requested-with": "XMLHttpRequest"},
    )
    if resp.status != 200:
        print("  DC create status", resp.status)
        return None, None
    data = resp.json()
    payload = data.get("data") or data
    return payload.get("guid"), payload.get("sq")


def scrape_discover(page, drop: str) -> list[dict]:
    print(f"\n=== DiscoverCars ORD {PICKUP} -> {drop} ===")
    page.goto("https://www.discovercars.com/", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(1500)
    dismiss(page)
    guid, sq = discover_create(page, drop)
    if not guid:
        return []
    api = f"https://www.discovercars.com/api/v2/search/{guid}?sq={sq}&searchVersion=2"
    offers = []
    for i in range(20):
        page.wait_for_timeout(1500 if i else 500)
        r = page.request.get(api, headers={"accept": "application/json"})
        if r.status != 200:
            continue
        try:
            data = r.json()
        except Exception:
            continue
        offers = (data.get("data") or {}).get("offers") or []
        if offers:
            break
    url = discover_url(guid, sq)
    cars: list[dict] = []
    for o in offers:
        price_obj = o.get("price") or {}
        raw = price_obj.get("raw")
        if raw is None:
            continue
        price = int(round(float(raw)))
        if price < 10_000:
            continue
        veh = o.get("vehicle") or {}
        spec = veh.get("specifications") or {}
        seats = (spec.get("seats") or {}).get("number")
        bags = (spec.get("bags") or {}).get("number")
        doors = (spec.get("doors") or {}).get("number")
        model = (veh.get("carName") or "차량").strip()
        category = normalize_category(veh.get("sippGroup") or "")
        supplier = ((o.get("supplier") or {}).get("name") or "").strip()
        opts = []
        if o.get("isFreeCancellation"):
            opts.append("무료 취소")
        fuel = (spec.get("fuelType") or "") if isinstance(spec.get("fuelType"), str) else ""
        if fuel and "electric" in fuel.lower():
            category = "전기차"
            opts.append("Fully electric")
        badges = o.get("badges") or {}
        if badges.get("zero_emission"):
            category = "전기차"
            opts.append("Fully electric")
        book = o.get("bookUrl") or url
        if book.startswith("/"):
            book = "https://www.discovercars.com" + book
        cars.append(
            offer_row(
                source="discover",
                drop=drop,
                model=model,
                category=category,
                price=price,
                seats=seats,
                bags=bags,
                doors=doors,
                location="ORD · DiscoverCars",
                options=opts,
                seller_url=book,
                supplier=supplier,
            )
        )
    # Dedupe identical model/category/price
    deduped: list[dict] = []
    seen: set[tuple] = set()
    for c in sorted(cars, key=lambda x: x["price"]):
        key = (c["model"], c["category"], c["price"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(c)
    cars = deduped[:TOP_PER_SOURCE]
    print(f"  found {len(cars)}")
    for c in cars[:3]:
        print(f"  - {c['price_text']} | {c['category']} | {c['model']}")
    return cars


# ---------- Rentalcars ----------
def scrape_rentalcars(page, drop: str) -> list[dict]:
    print(f"\n=== Rentalcars ORD {PICKUP} -> {drop} ===")
    page.goto(rentalcars_url(drop), wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4000)
    dismiss(page)
    search_criteria = {
        "driversAge": 30,
        "pickUpLocation": "ORD",
        "pickUpDateTime": f"{PICKUP}T12:00:00",
        "pickUpLocationType": "IATA",
        "dropOffLocation": "ORD",
        "dropOffLocationType": "IATA",
        "dropOffDateTime": f"{drop}T12:00:00",
        "searchMetadata": json.dumps(
            {"pickUpLocationName": "ORD Airport", "dropOffLocationName": "ORD Airport"}
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
    for i in range(8):
        r = page.request.get(api_url, headers={"accept": "application/json"})
        if r.status == 200:
            try:
                matches = (r.json() or {}).get("matches") or []
            except Exception:
                matches = []
            if matches:
                break
        page.wait_for_timeout(2000)
    url = rentalcars_url(drop)
    cars: list[dict] = []
    for m in matches:
        veh = m.get("vehicle") or {}
        price_obj = veh.get("driveAwayPrice") or veh.get("price") or {}
        amount = price_obj.get("amount")
        if amount is None:
            continue
        price = int(round(float(amount)))
        if price < 10_000:
            continue
        model = (veh.get("makeAndModel") or "차량").strip()
        cats = veh.get("carCategories") or []
        category = normalize_category(cats[0] if cats else veh.get("carClass") or "")
        opts = []
        if veh.get("freeCancellation"):
            opts.append("무료 취소")
        if (veh.get("fuel") or "").lower() in ("electric", "ev"):
            category = "전기차"
            opts.append("Fully electric")
        cars.append(
            offer_row(
                source="rentalcars",
                drop=drop,
                model=model,
                category=category,
                price=price,
                seats=int(veh["numberOfSeats"]) if str(veh.get("numberOfSeats", "")).isdigit() else None,
                bags=veh.get("bigSuitcase"),
                doors=int(veh["numberOfDoors"]) if str(veh.get("numberOfDoors", "")).isdigit() else None,
                location="ORD · Rentalcars.com",
                options=opts,
                seller_url=url,
                supplier="",
            )
        )
    cars.sort(key=lambda c: c["price"])
    cars = cars[:TOP_PER_SOURCE]
    print(f"  found {len(cars)}")
    for c in cars[:3]:
        print(f"  - {c['price_text']} | {c['category']} | {c['model']}")
    return cars


# ---------- Expedia via CarTrawler UI ----------
def scrape_expedia_ct(page, drop: str, client_id: str) -> list[dict]:
    print(f"\n=== Expedia/CT({client_id}) ORD {PICKUP} -> {drop} ===")
    url = expedia_ct_url(drop, client_id)
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
    except PlaywrightTimeout:
        print("  nav timeout")
    page.wait_for_timeout(8000)
    dismiss(page)
    # Fill pickup if empty
    try:
        loc = page.locator("#pickupLocation")
        if loc.count() and not (loc.input_value() or "").strip():
            loc.click()
            loc.fill("ORD")
            page.wait_for_timeout(1500)
            page.keyboard.press("ArrowDown")
            page.keyboard.press("Enter")
            page.wait_for_timeout(800)
            page.evaluate(
                """() => {
              const b = [...document.querySelectorAll('button')].find(el =>
                /search cars|search|find cars/i.test((el.innerText||'').trim())
              );
              if (b) b.click();
            }"""
            )
            page.wait_for_timeout(12000)
    except Exception as e:
        print("  fill err", e)

    deadline = time.time() + 45
    cars: list[dict] = []
    while time.time() < deadline:
        text = page.inner_text("body")
        if re.search(r"₩[\d,]+|\$[\d,]+", text) and ("or similar" in text.lower() or "seat" in text.lower() or "동급" in text):
            cars = parse_expedia_dom(page, drop, url)
            if cars:
                break
        page.wait_for_timeout(1500)
    print(f"  found {len(cars)}")
    for c in cars[:3]:
        print(f"  - {c['price_text']} | {c['category']} | {c['model']}")
    return cars


def parse_expedia_dom(page, drop: str, url: str) -> list[dict]:
    raw = page.evaluate(
        """() => {
      const text = document.body.innerText || '';
      const blocks = text.split(/\\n(?=[A-Z][a-z]+\\s+[A-Z])/);
      // Fallback: line-scan for price + model patterns
      const lines = text.split('\\n').map(s => s.trim()).filter(Boolean);
      const out = [];
      for (let i = 0; i < lines.length; i++) {
        const pm = lines[i].match(/^(₩[\\d,]+|\\$[\\d,.]+)$/) || lines[i].match(/(₩[\\d,]+)/);
        if (!pm) continue;
        // look back for model-ish line
        let model = '';
        let cat = '';
        for (let j = i - 1; j >= Math.max(0, i - 8); j--) {
          if (/or similar|Economy|Compact|Standard|Intermediate|Full|SUV|Van|Premium|Luxury/i.test(lines[j])) {
            if (/or similar/i.test(lines[j])) model = lines[j].replace(/\\s*or similar.*/i, '').trim();
            else if (!cat) cat = lines[j];
          }
          if (/^[A-Z][A-Za-z0-9\\-\\s]{2,40}$/.test(lines[j]) && !/Search|Filter|Options|Pick-up|Return|Korea|Currency/i.test(lines[j])) {
            if (!model) model = lines[j];
          }
        }
        if (!model) continue;
        out.push({ model, category: cat, price_raw: pm[1] || pm[0], nearby: lines.slice(Math.max(0,i-6), i+3) });
      }
      return out.slice(0, 40);
    }"""
    )
    cars: list[dict] = []
    seen: set[tuple] = set()
    for item in raw or []:
        pr = item.get("price_raw") or ""
        if pr.startswith("₩"):
            price = int(pr.replace("₩", "").replace(",", ""))
        elif pr.startswith("$"):
            # rough USD->KRW if needed (prefer KRW page)
            price = int(round(float(pr.replace("$", "").replace(",", "")) * 1380))
        else:
            continue
        model = (item.get("model") or "").strip()
        category = normalize_category(item.get("category") or "")
        key = (model, price)
        if not model or key in seen:
            continue
        seen.add(key)
        cars.append(
            offer_row(
                source="expedia",
                drop=drop,
                model=model,
                category=category,
                price=price,
                location="ORD · Expedia",
                options=[],
                seller_url=url,
            )
        )
    cars.sort(key=lambda c: c["price"])
    return cars[:TOP_PER_SOURCE]


def pick_expedia_client(page) -> str | None:
    for cid in EXPEDIA_CT_CLIENTS:
        url = expedia_ct_url(DROPOFF_DATES[0], cid)
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
        except PlaywrightTimeout:
            continue
        page.wait_for_timeout(8000)
        # Look at network-ish errors in body / try parse
        text = page.inner_text("body")
        if "Invalid POS" in text:
            continue
        prices = re.findall(r"₩[\d,]+|\$[\d,]+", text)
        if prices:
            print(f"Expedia CT client OK: {cid}")
            return cid
        # Try fill+search once
        cars = scrape_expedia_ct(page, DROPOFF_DATES[0], cid)
        if cars:
            print(f"Expedia CT client OK: {cid}")
            return cid
    return None


def load_kayak_cheapest() -> dict[str, list[dict]]:
    if not KAYAK_FILE.exists():
        return {}
    rows = json.loads(KAYAK_FILE.read_text(encoding="utf-8"))
    out: dict[str, list[dict]] = {}
    for day in rows:
        drop = day.get("dropoff_date")
        cars = []
        for c in (day.get("cars") or [])[:TOP_PER_SOURCE]:
            if c.get("price") is None:
                continue
            cars.append(
                offer_row(
                    source="kayak",
                    drop=drop,
                    model=c.get("model") or "차량",
                    category=c.get("category") or "기타",
                    price=int(c["price"]),
                    seats=c.get("seats"),
                    bags=c.get("bags"),
                    doors=c.get("doors"),
                    location=c.get("location") or "ORD · KAYAK",
                    options=c.get("options") or [],
                    seller_url=c.get("seller_url") or kayak_url(drop),
                )
            )
        cars.sort(key=lambda x: x["price"])
        out[drop] = cars
    return out


def main() -> int:
    kayak_by_drop = load_kayak_cheapest()
    results: list[dict] = []

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            viewport={"width": 1400, "height": 900},
            locale="ko-KR",
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.pages[0] if context.pages else context.new_page()

        # Warm DiscoverCars + Rentalcars
        page.goto("https://www.discovercars.com/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2000)
        dismiss(page)

        # Expedia.com/Travelocity family is bot-gated; try CarTrawler once, else link-only.
        exp_client = None
        try:
            exp_client = pick_expedia_client(page)
        except Exception as e:
            print("Expedia client probe failed:", e)
        if not exp_client:
            print("Expedia live scrape unavailable (bot/POS). Will store search links only.")

        for drop in DROPOFF_DATES:
            discover = scrape_discover(page, drop)
            rentalcars = scrape_rentalcars(page, drop)
            expedia: list[dict] = []
            if exp_client:
                expedia = scrape_expedia_ct(page, drop, exp_client)
            kayak = kayak_by_drop.get(drop) or []

            sources = {
                "discover": discover,
                "rentalcars": rentalcars,
                "expedia": expedia,
                "kayak": kayak,
            }
            cheapest_by_source = {}
            for key, cars in sources.items():
                cheapest_by_source[key] = cars[0] if cars else None

            # Flat list for dashboard picks (tag source in id already)
            all_cars = []
            for key in ("discover", "rentalcars", "expedia", "kayak"):
                all_cars.extend(sources[key])
            all_cars.sort(key=lambda c: c["price"])

            results.append(
                {
                    "pickup_date": PICKUP,
                    "dropoff_date": drop,
                    "pickup_location": "ORD",
                    "dropoff_location": "ORD",
                    "nights": nights(PICKUP, drop),
                    "sources": {
                        "discover": {
                            "label": "DiscoverCars",
                            "url": discover[0]["seller_url"] if discover else f"https://www.discovercars.com/usa-illinois/chicago/ord",
                            "cars": discover,
                            "cheapest": cheapest_by_source["discover"],
                        },
                        "rentalcars": {
                            "label": "Rentalcars.com",
                            "url": rentalcars_url(drop),
                            "cars": rentalcars,
                            "cheapest": cheapest_by_source["rentalcars"],
                        },
                        "expedia": {
                            "label": "Expedia",
                            "url": expedia_url(drop),
                            "cars": expedia,
                            "cheapest": cheapest_by_source["expedia"],
                            "note": None if expedia else "사이트 봇 차단으로 실시간 수집 불가 · 링크에서 직접 확인",
                        },
                        "kayak": {
                            "label": "KAYAK",
                            "url": kayak_url(drop),
                            "cars": kayak,
                            "cheapest": cheapest_by_source["kayak"],
                        },
                    },
                    "cars": all_cars,
                    "synced_at": now_kst(),
                }
            )

        context.close()

    OUT_FILE.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT_FILE.name}")
    for day in results:
        bits = []
        for key, label in (
            ("discover", "DC"),
            ("rentalcars", "RC"),
            ("expedia", "EX"),
            ("kayak", "KY"),
        ):
            c = (day["sources"][key].get("cheapest") or {})
            bits.append(f"{label}:{c.get('price_text', '-')}")
        print(day["dropoff_date"], " · ".join(bits))
    ok = any(
        (d["sources"]["discover"]["cars"] or d["sources"]["rentalcars"]["cars"])
        for d in results
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
