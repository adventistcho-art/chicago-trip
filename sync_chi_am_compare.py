#!/usr/bin/env python3
"""ICN/SEL→ORD 9/24 · ORD→SEL 10/9 · 양쪽 오전 · 편도 17h 이하 최저가.

KAYAK · Skyscanner · Google Flights 실검색 → chi_am_compare.json
"""

from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUT_FILE = ROOT / "chi_am_compare.json"
USER_DATA_DIR = ROOT / ".browser_profile_capture"

OUTBOUND = "2026-09-24"
RETURN = "2026-10-09"
ADULTS = 2
CHILD_AGES = [7, 8]
GUESTS = 4
MAX_LEG_MIN = 17 * 60  # 1020
MIN_LEG_MIN = 10 * 60  # SEL↔ORD 편도는 최소 ~10시간 (경유/지상시간 오인 방지)
MORNING_END_MIN = 12 * 60  # takeoff before noon


def now_kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%dT%H:%M:%S+09:00")


def headless() -> bool:
    return os.environ.get("SYNC_HEADLESS", "").lower() in ("1", "true", "yes")


def fmt_won(n: int) -> str:
    return f"₩{n:,}"


def kayak_url() -> str:
    # takeoff/retakeoff: minutes from midnight · legdur max 17h
    fs = f"legdur=-{MAX_LEG_MIN};takeoff=0,{MORNING_END_MIN};retakeoff=0,{MORNING_END_MIN}"
    return (
        f"https://www.kayak.co.kr/flights/SEL-ORD/{OUTBOUND}/{RETURN}/"
        f"{ADULTS}adults/children-7-8?sort=price_a&fs={fs}"
    )


def skyscanner_url() -> str:
    out = datetime.strptime(OUTBOUND, "%Y-%m-%d").strftime("%y%m%d")
    ret = datetime.strptime(RETURN, "%Y-%m-%d").strftime("%y%m%d")
    kids = "|".join(str(a) for a in CHILD_AGES)
    return (
        f"https://www.skyscanner.co.kr/transport/flights/sela/ord/{out}/{ret}/"
        f"?adultsv2={ADULTS}&childrenv2={quote(kids)}"
        f"&cabinclass=economy&rtn=1&preferdirects=false"
    )


def google_url() -> str:
    q = (
        f"Seoul to Chicago O'Hare {OUTBOUND} return {RETURN} "
        f"adults {ADULTS} children {len(CHILD_AGES)} morning"
    )
    return f"https://www.google.com/travel/flights/search?q={quote(q)}&hl=ko"


def dismiss(page) -> None:
    page.evaluate(
        """() => {
      const buttons = [...document.querySelectorAll('button, [role="button"]')];
      const target = buttons.find(el => {
        const t = (el.innerText || '').replace(/\\s+/g, ' ').trim();
        return /^(동의합니다|모두 동의|Accept all|Accept|I agree|Agree)$/i.test(t);
      });
      if (target) target.click();
    }"""
    )


def parse_duration_legs(text: str) -> list[int]:
    return [int(h) * 60 + int(m) for h, m in re.findall(r"(\d+)\s*시간\s*(\d+)\s*분", text or "")]


def valid_intl_legs(duration_text: str) -> bool:
    """Both outbound/return must look like SEL↔ORD legs (10h–17h)."""
    legs = parse_duration_legs(duration_text)
    return len(legs) >= 2 and all(MIN_LEG_MIN <= m <= MAX_LEG_MIN for m in legs[:2])


def within_17h(duration_text: str) -> bool:
    return valid_intl_legs(duration_text)


def parse_hhmm_to_min(text: str) -> int | None:
    m = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", text or "")
    if not m:
        return None
    return int(m.group(1)) * 60 + int(m.group(2))


def is_morning_hhmm(text: str) -> bool:
    mins = parse_hhmm_to_min(text)
    if mins is None:
        return False
    return mins < MORNING_END_MIN


def enrich(
    *,
    source: str,
    label: str,
    price_total: int,
    duration_text: str,
    stops_text: str,
    carrier_text: str,
    seller_url: str,
    depart_out: str = "",
    depart_ret: str = "",
    note: str = "",
    morning_filter: str = "applied",
) -> dict:
    pp = round(price_total / GUESTS)
    return {
        "source": source,
        "source_label": label,
        "outbound_date": OUTBOUND,
        "return_date": RETURN,
        "route": "chi_round",
        "route_label": "시카고 인 · 시카고 아웃",
        "price": price_total,
        "price_text": fmt_won(price_total),
        "price_per_person": pp,
        "price_per_person_text": fmt_won(pp),
        "duration_text": duration_text,
        "duration_minutes": sum(parse_duration_legs(duration_text)) or None,
        "stops_text": stops_text,
        "carrier_text": carrier_text,
        "depart_outbound": depart_out,
        "depart_return": depart_ret,
        "morning": True,
        "under_17h": valid_intl_legs(duration_text),
        "morning_filter": morning_filter,
        "note": note,
        "seller_url": seller_url,
        "synced_at": now_kst(),
    }


def extract_kayak(page) -> list[dict]:
    return page.evaluate(
        """() => {
      const carrierRe = /항공|Air|United|Delta|Korean|Asiana|에어|대한|아시아나|에바|아메리칸|터키|캐세이|캐나다|ANA|JAL|카타르|에티하드|핀에어|루프트한자/i;
      const parseBlock = (b) => {
        const pm = b.match(/([\\d,]+)원/);
        if (!pm) return null;
        const price = parseInt(pm[1].replace(/,/g, ''), 10);
        // family-of-4 total on KAYAK KR is often 4~12M; also accept 1인×표시
        if (!price || price < 400000) return null;
        const lines = b.split('\\n').map(s => s.trim()).filter(Boolean);
        const carrier = lines.find(l => carrierRe.test(l)) || '';
        const durs = b.match(/(\\d+시간\\s*\\d+분)/g) || [];
        // Prefer long-haul pair (ignore short layover like 1h50)
        const parsed = durs.map(d => {
          const m = d.match(/(\\d+)\\s*시간\\s*(\\d+)\\s*분/);
          return m ? { t: d, min: (+m[1])*60 + (+m[2]) } : null;
        }).filter(Boolean);
        const long = parsed.filter(x => x.min >= 600 && x.min <= 1020);
        if (long.length < 2) return null;
        const duration_text = long.slice(0, 2).map(x => x.t).join(' / ');
        const stops = (b.match(/(\\d+회\\s*경유|직항)/g) || []).slice(0, 2);
        const times = b.match(/\\b([01]?\\d|2[0-3]):([0-5]\\d)\\b/g) || [];
        return {
          price,
          duration_text,
          stops_text: stops.join(' / '),
          carrier_text: carrier,
          times,
        };
      };
      const out = [];
      const seen = new Set();
      const text = document.body.innerText || '';
      const blocks = text.split('다음 검색 결과로 이동').slice(1);
      const push = (row) => {
        if (!row) return;
        const key = row.price + '|' + row.duration_text + '|' + row.carrier_text;
        if (seen.has(key)) return;
        seen.add(key);
        out.push(row);
      };
      for (const b of blocks) {
        push(parseBlock(b));
        if (out.length >= 25) break;
      }
      if (!out.length) {
        const priceRe = /([\\d,]+)원/g;
        let m;
        while ((m = priceRe.exec(text)) !== null) {
          push(parseBlock(text.slice(Math.max(0, m.index - 60), m.index + 500)));
          if (out.length >= 25) break;
        }
      }
      return out;
    }"""
    )


def normalize_kayak_price(price: int) -> int:
    """KAYAK sometimes shows per-adult; family total if looks like 1인 요금."""
    if price < 3_500_000:
        return price * GUESTS
    return price


def _kayak_collect(page, url: str) -> list[dict]:
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=90000)
    except PlaywrightTimeout:
        print("  nav timeout")
    page.wait_for_timeout(3000)
    dismiss(page)
    best_rows: list[dict] = []
    deadline = time.time() + 50
    while time.time() < deadline:
        dismiss(page)
        for y in (800, 1600, 2800, 4000):
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(500)
        rows = extract_kayak(page)
        if len(rows) > len(best_rows):
            best_rows = rows
        if len(best_rows) >= 8:
            break
        time.sleep(0.7)
    return best_rows


def scrape_kayak(page) -> dict | None:
    urls = [
        kayak_url(),
        # fallback: duration only, morning filtered in code
        (
            f"https://www.kayak.co.kr/flights/SEL-ORD/{OUTBOUND}/{RETURN}/"
            f"{ADULTS}adults/children-7-8?sort=price_a&fs=legdur=-{MAX_LEG_MIN}"
        ),
    ]
    print(f"\n=== KAYAK ===\n{urls[0]}")
    for url in urls:
        rows = _kayak_collect(page, url)
        print(f"  rows={len(rows)} from {url[:88]}...")
        for row in rows:
            dur = row.get("duration_text") or ""
            if not within_17h(dur):
                continue
            times = row.get("times") or []
            # KAYAK card times usually: outDep outArr retDep retArr
            out_dep = str(times[0]) if times else ""
            ret_dep = str(times[2]) if len(times) >= 3 else ""
            if out_dep and not is_morning_hhmm(out_dep):
                continue
            if ret_dep and not is_morning_hhmm(ret_dep):
                continue
            # Require at least one parsed morning time (avoid accepting empty)
            if not (is_morning_hhmm(out_dep) or is_morning_hhmm(ret_dep)):
                continue
            if out_dep and ret_dep and not (
                is_morning_hhmm(out_dep) and is_morning_hhmm(ret_dep)
            ):
                continue
            total = normalize_kayak_price(int(row["price"]))
            offer = enrich(
                source="kayak",
                label="KAYAK",
                price_total=total,
                duration_text=dur,
                stops_text=row.get("stops_text") or "",
                carrier_text=row.get("carrier_text") or "",
                seller_url=url,
                depart_out=out_dep or "오전",
                depart_ret=ret_dep or "오전",
                note="시각 검증: 출국·귀국 이륙 00:00–12:00 · 편도 10–17시간",
                morning_filter="time",
            )
            print(f"  OK {offer['price']:,} | {dur} | {offer['carrier_text']}")
            return offer
    print("  FAILED - no morning <=17h row")
    return None


def parse_skyscanner_payloads(payloads: list[dict]) -> dict | None:
    candidates: list[dict] = []
    for payload in payloads:
        itineraries = payload.get("itineraries") or {}
        buckets = itineraries.get("buckets") or []
        for bucket in buckets:
            for item in bucket.get("items") or []:
                legs = item.get("legs") or []
                if len(legs) < 2:
                    continue
                durs = [int(leg.get("durationInMinutes") or 0) for leg in legs[:2]]
                if not durs or any(d < MIN_LEG_MIN or d > MAX_LEG_MIN for d in durs):
                    continue
                # morning: first segment departure hour < 12
                morning_ok = True
                dep_texts = []
                for leg in legs[:2]:
                    segs = leg.get("segments") or []
                    if not segs:
                        morning_ok = False
                        break
                    dep = segs[0].get("departure") or segs[0].get("departureTime") or ""
                    # ISO or "2026-09-24T08:30:00"
                    hm = re.search(r"T(\d{2}):(\d{2})", str(dep))
                    if hm:
                        mins = int(hm.group(1)) * 60 + int(hm.group(2))
                        dep_texts.append(f"{hm.group(1)}:{hm.group(2)}")
                        if mins >= MORNING_END_MIN:
                            morning_ok = False
                    else:
                        # if unknown time, keep as candidate but mark filter soft
                        dep_texts.append("")
                if not morning_ok:
                    continue
                price_obj = item.get("price") or {}
                raw = price_obj.get("raw") or price_obj.get("amount")
                if raw is None:
                    continue
                price = int(raw)
                # Skyscanner KR often returns total for party
                if price < 400_000:
                    continue
                if price < 3_500_000:
                    price *= GUESTS
                carriers = []
                stops = []
                dur_texts = []
                for leg in legs[:2]:
                    d = int(leg.get("durationInMinutes") or 0)
                    h, m = divmod(d, 60)
                    dur_texts.append(f"{h}시간 {m}분")
                    segs = leg.get("segments") or []
                    stop_count = max(0, len(segs) - 1)
                    stops.append("직항" if stop_count == 0 else f"{stop_count}회 경유")
                    for seg in segs:
                        name = (seg.get("marketingCarrier") or {}).get("name")
                        if name:
                            carriers.append(name)
                candidates.append(
                    {
                        "price": price,
                        "duration_text": " / ".join(dur_texts),
                        "stops_text": " / ".join(stops),
                        "carrier_text": ", ".join(dict.fromkeys(carriers)) or "",
                        "depart_out": dep_texts[0] if dep_texts else "",
                        "depart_ret": dep_texts[1] if len(dep_texts) > 1 else "",
                        "deeplink": item.get("deeplinkUrl") or "",
                    }
                )
    if not candidates:
        return None
    candidates.sort(key=lambda x: x["price"])
    best = candidates[0]
    return enrich(
        source="skyscanner",
        label="스카이스캐너",
        price_total=best["price"],
        duration_text=best["duration_text"],
        stops_text=best["stops_text"],
        carrier_text=best["carrier_text"],
        seller_url=best["deeplink"] or skyscanner_url(),
        depart_out=best["depart_out"] or "오전",
        depart_ret=best["depart_ret"] or "오전",
        note="API 결과 중 편도≤17h · 출발 시각 오전 필터",
        morning_filter="api",
    )


def scrape_skyscanner(page) -> dict | None:
    url = skyscanner_url()
    print(f"\n=== Skyscanner ===\n{url}")
    captured: list[dict] = []

    def on_response(response):
        if "web-unified-search" in response.url and response.request.method == "POST":
            try:
                captured.append(response.json())
            except Exception:
                pass

    page.on("response", on_response)
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=90000)
    except PlaywrightTimeout:
        print("  nav timeout")
    for _ in range(90):
        title = page.title() or ""
        if "captcha" not in (page.url or "").lower() and "로봇" not in title and "사람" not in title:
            break
        print("  waiting captcha...")
        page.wait_for_timeout(2000)

    # Wait until results finish loading (buckets populate on later polls)
    deadline = time.time() + 75
    best_payloads: list[dict] = []
    while time.time() < deadline:
        dismiss(page)
        page.wait_for_timeout(2000)
        body = page.inner_text("body")
        filled = [p for p in captured if (p.get("itineraries") or {}).get("buckets")]
        if filled:
            best_payloads = filled
        if "확인 완료" in body and filled:
            # give one more poll cycle
            page.wait_for_timeout(3000)
            filled = [p for p in captured if (p.get("itineraries") or {}).get("buckets")]
            if filled:
                best_payloads = filled
            break

    # Try UI morning filters (가는날/오는편 출발)
    try:
        page.get_by_text("출발 시간대", exact=False).first.click(timeout=2500)
        page.wait_for_timeout(800)
    except Exception:
        pass

    offer = parse_skyscanner_payloads(best_payloads or captured)
    if offer:
        print(f"  OK {offer['price']:,} | {offer['duration_text']} | {offer['carrier_text']}")
        return offer

    # Relaxed API: under 17h only (morning soft)
    soft_candidates: list[dict] = []
    for payload in best_payloads or captured:
        for bucket in (payload.get("itineraries") or {}).get("buckets") or []:
            for item in bucket.get("items") or []:
                legs = item.get("legs") or []
                if len(legs) < 2:
                    continue
                durs = [int(leg.get("durationInMinutes") or 0) for leg in legs[:2]]
                if any(d < MIN_LEG_MIN or d > MAX_LEG_MIN for d in durs):
                    continue
                price_obj = item.get("price") or {}
                raw = price_obj.get("raw") or price_obj.get("amount")
                if raw is None:
                    continue
                price = int(raw)
                if price < 400_000:
                    continue
                if price < 3_500_000:
                    price *= GUESTS
                dur_texts = []
                for d in durs:
                    h, m = divmod(d, 60)
                    dur_texts.append(f"{h}시간 {m}분")
                soft_candidates.append(
                    {
                        "price": price,
                        "duration_text": " / ".join(dur_texts),
                        "deeplink": item.get("deeplinkUrl") or url,
                    }
                )
    if soft_candidates:
        soft_candidates.sort(key=lambda x: x["price"])
        best = soft_candidates[0]
        offer = enrich(
            source="skyscanner",
            label="스카이스캐너",
            price_total=best["price"],
            duration_text=best["duration_text"],
            stops_text="",
            carrier_text="",
            seller_url=best["deeplink"],
            depart_out="확인 필요",
            depart_ret="확인 필요",
            note="편도 10–17시간 최저가(오전 필터는 사이트에서 재확인)",
            morning_filter="soft",
        )
        print(f"  OK(soft) {offer['price']:,} | {offer['duration_text']}")
        return offer

    # DOM fallback — Skyscanner KR often shows 1인 요금
    text = page.inner_text("body")
    # Prefer result cards with two long durations
    card_bits = re.split(r"\n{2,}", text)
    dom_rows = []
    for bit in card_bits:
        durs = re.findall(r"(\d+)\s*시간\s*(\d+)\s*분", bit)
        long = [(int(h), int(mi)) for h, mi in durs if MIN_LEG_MIN <= int(h) * 60 + int(mi) <= MAX_LEG_MIN]
        if len(long) < 2:
            continue
        prices = [int(x.replace(",", "")) for x in re.findall(r"₩([\d,]+)", bit)]
        prices = [p for p in prices if p >= 500_000]
        if not prices:
            continue
        raw = min(prices)
        total = raw if raw >= 3_500_000 else raw * GUESTS
        dur = " / ".join(f"{h}시간 {mi}분" for h, mi in long[:2])
        dom_rows.append((total, dur, bit[:80]))
    if dom_rows:
        dom_rows.sort(key=lambda x: x[0])
        total, dur, _ = dom_rows[0]
        offer = enrich(
            source="skyscanner",
            label="스카이스캐너",
            price_total=total,
            duration_text=dur,
            stops_text="",
            carrier_text="",
            seller_url=url,
            note="DOM 파싱 · 편도 10–17시간 · 오전은 사이트 필터로 재확인",
            morning_filter="soft",
        )
        print(f"  OK(dom) {offer['price']:,} | {dur}")
        return offer
    print("  FAILED")
    return None


def scrape_google(page) -> dict | None:
    url = google_url()
    print(f"\n=== Google Flights ===\n{url}")
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=90000)
    except PlaywrightTimeout:
        print("  nav timeout")
    page.wait_for_timeout(10000)
    dismiss(page)

    # Try open filters / morning if UI present (best-effort)
    for label in ("출발 시간", "Times", "이륙", "Take-off"):
        try:
            loc = page.get_by_text(label, exact=False).first
            if loc.count():
                loc.click(timeout=2000)
                page.wait_for_timeout(800)
        except Exception:
            pass

    text = page.inner_text("body")
    # Google often shows per-adult; family total = ×4 if small
    matches = []
    for m in re.finditer(r"₩([\d,]+)", text):
        price = int(m.group(1).replace(",", ""))
        if price < 500_000:
            continue
        chunk = text[max(0, m.start() - 80) : m.start() + 420]
        durs = re.findall(r"(\d+)\s*시간\s*(\d+)\s*분", chunk)
        if len(durs) < 2:
            continue
        # pick two long-haul durations from chunk
        long_pairs = [(int(h), int(mi)) for h, mi in durs if MIN_LEG_MIN <= int(h) * 60 + int(mi) <= MAX_LEG_MIN]
        if len(long_pairs) < 2:
            continue
        legs = [h * 60 + mi for h, mi in long_pairs[:2]]
        dur_text = " / ".join(f"{h}시간 {mi}분" for h, mi in long_pairs[:2])
        times = re.findall(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", chunk)
        # prefer morning if times present
        morning_score = 0
        dep_out = dep_ret = ""
        if len(times) >= 2:
            t0 = int(times[0][0]) * 60 + int(times[0][1])
            # find return leg start roughly later times
            t_ret = None
            for hh, mm in times[2:]:
                mins = int(hh) * 60 + int(mm)
                if mins < MORNING_END_MIN:
                    t_ret = mins
                    dep_ret = f"{int(hh):02d}:{mm}"
                    break
            if t0 < MORNING_END_MIN:
                morning_score += 1
                dep_out = f"{int(times[0][0]):02d}:{times[0][1]}"
            if t_ret is not None:
                morning_score += 1
        total = price if price >= 3_500_000 else price * GUESTS
        carriers = ""
        for c in ("대한항공", "아시아나", "델타", "유나이티드", "에어캐나다", "에바", "ANA", "JAL", "카타르"):
            if c in chunk:
                carriers = c
                break
        matches.append(
            {
                "price": total,
                "duration_text": dur_text,
                "morning_score": morning_score,
                "depart_out": dep_out,
                "depart_ret": dep_ret,
                "carrier": carriers,
                "stops": ("직항" if "직항" in chunk else "경유"),
            }
        )

    if not matches:
        print("  FAILED")
        return None
    # Prefer both legs morning when times known
    strict = [
        m
        for m in matches
        if m["morning_score"] >= 2
        or (
            is_morning_hhmm(m.get("depart_out") or "")
            and is_morning_hhmm(m.get("depart_ret") or "")
        )
    ]
    pool = strict or [m for m in matches if m["morning_score"] >= 1] or matches
    pool.sort(key=lambda x: (-x["morning_score"], x["price"]))
    best = pool[0]
    offer = enrich(
        source="google",
        label="구글 항공권",
        price_total=best["price"],
        duration_text=best["duration_text"],
        stops_text=best["stops"],
        carrier_text=best["carrier"],
        seller_url=url,
        depart_out=best["depart_out"] or "오전 선호",
        depart_ret=best["depart_ret"] or "오전 선호",
        note="편도 10–17h · 오전 출발 우선",
        morning_filter="scored",
    )
    print(f"  OK {offer['price']:,} | {offer['duration_text']} | score={best['morning_score']}")
    return offer


def main() -> int:
    sources: dict[str, Any] = {}
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=headless(),
            viewport={"width": 1440, "height": 900},
            locale="ko-KR",
            args=["--disable-blink-features=AutomationControlled"],
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
        )
        page = context.pages[0] if context.pages else context.new_page()

        kayak = scrape_kayak(page)
        if kayak:
            sources["kayak"] = kayak

        sky = scrape_skyscanner(page)
        if sky:
            sources["skyscanner"] = sky

        google = scrape_google(page)
        if google:
            sources["google"] = google

        context.close()

    offers = [sources[k] for k in ("kayak", "skyscanner", "google") if k in sources]
    offers.sort(key=lambda x: x["price"])
    # Keep empty slots so UI always lists 3 OTAs
    for key, label, url in (
        ("kayak", "KAYAK", kayak_url()),
        ("skyscanner", "스카이스캐너", skyscanner_url()),
        ("google", "구글 항공권", google_url()),
    ):
        if key not in sources:
            sources[key] = {
                "source": key,
                "source_label": label,
                "outbound_date": OUTBOUND,
                "return_date": RETURN,
                "route": "chi_round",
                "route_label": "시카고 인 · 시카고 아웃",
                "price": None,
                "price_text": "조건 맞는 결과 없음",
                "price_per_person": None,
                "price_per_person_text": "-",
                "duration_text": "-",
                "stops_text": "-",
                "carrier_text": "-",
                "depart_outbound": "",
                "depart_return": "",
                "morning": True,
                "under_17h": False,
                "morning_filter": "none",
                "note": "오전·편도≤17시간 조건에서 자동추출 실패 · 아래 링크로 직접 확인",
                "seller_url": url,
                "synced_at": now_kst(),
                "empty": True,
            }
    payload = {
        "route": "chi_round",
        "route_label": "시카고 인 · 시카고 아웃",
        "outbound_date": OUTBOUND,
        "return_date": RETURN,
        "filters": {
            "morning_both": True,
            "max_leg_minutes": MAX_LEG_MIN,
            "min_leg_minutes": MIN_LEG_MIN,
            "guests": GUESTS,
            "adults": ADULTS,
            "child_ages": CHILD_AGES,
        },
        "urls": {
            "kayak": kayak_url(),
            "skyscanner": skyscanner_url(),
            "google": google_url(),
        },
        "sources": sources,
        "offers": offers,
        "best": offers[0] if offers else None,
        "synced_at": now_kst(),
    }
    OUT_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT_FILE.name} · {len(offers)} sources")
    if offers:
        print(f"BEST {offers[0]['source_label']} {offers[0]['price']:,}")
    return 0 if offers else 1


if __name__ == "__main__":
    raise SystemExit(main())
