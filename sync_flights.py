#!/usr/bin/env python3
"""Skyscanner flight sync: Seoul -> Chicago ORD, generates flights.html."""

from __future__ import annotations

import json
import re
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

ROOT = Path(__file__).resolve().parent
OUTPUT_HTML = ROOT / "flights.html"
STATE_FILE = ROOT / "flight_data.json"
USER_DATA_DIR = ROOT / ".browser_profile"

# Search config
ORIGIN = "sela"  # Seoul (all airports)
DESTINATION = "ord"  # Chicago O'Hare
OUTBOUND_DATE = "2026-09-24"
# Same departure, multiple return dates (10/8 ~ 10/13)
RETURN_DATES = [
    "2026-10-08",
    "2026-10-09",
    "2026-10-10",
    "2026-10-11",
    "2026-10-12",
    "2026-10-13",
]
# First run: visible browser so you can pass "press and hold" CAPTCHA once.
HEADLESS = False
ADULTS = 2
CHILD_AGES = [7, 8]
LOCALE = "ko-KR"
MARKET = "KR"
CURRENCY = "KRW"


@dataclass
class FlightOffer:
    outbound_date: str
    return_date: str
    price: int | None
    price_text: str
    duration_text: str
    stops_text: str
    carrier_text: str
    seller_url: str
    skyscanner_url: str
    synced_at: str


def yymmdd(iso_date: str) -> str:
    d = datetime.strptime(iso_date, "%Y-%m-%d")
    return d.strftime("%y%m%d")


def build_search_pairs() -> list[tuple[str, str]]:
    """Fixed outbound, multiple return dates. Bump return year if before outbound."""
    out_dt = datetime.strptime(OUTBOUND_DATE, "%Y-%m-%d")
    pairs: list[tuple[str, str]] = []
    for ret in RETURN_DATES:
        ret_dt = datetime.strptime(ret, "%Y-%m-%d")
        while ret_dt <= out_dt:
            ret_dt = ret_dt.replace(year=ret_dt.year + 1)
        pairs.append((OUTBOUND_DATE, ret_dt.strftime("%Y-%m-%d")))
    return pairs


def is_captcha_page(page) -> bool:
    url = (page.url or "").lower()
    title = page.title() or ""
    return "captcha" in url or "로봇" in title or "사람" in title


def wait_for_human_captcha(page, first_run: bool) -> None:
    if not is_captcha_page(page):
        return
    if first_run:
        print("\n" + "=" * 60)
        print("  브라우저에서 '길게 누르기' CAPTCHA를 통과해 주세요.")
        print("  통과하면 자동으로 검색을 계속합니다.")
        print("=" * 60 + "\n")
    deadline = time.time() + 300
    while time.time() < deadline and is_captcha_page(page):
        page.wait_for_timeout(1000)
    if is_captcha_page(page):
        raise RuntimeError("CAPTCHA를 5분 안에 통과하지 못했습니다.")


def build_search_url(outbound: str, inbound: str) -> str:
    params = {
        "adultsv2": str(ADULTS),
        "childrenv2": "|".join(str(a) for a in CHILD_AGES),
        "cabinclass": "economy",
        "rtn": "1",
        "preferdirects": "false",
        "outboundaltsenabled": "false",
        "inboundaltsenabled": "false",
    }
    path = (
        f"https://www.skyscanner.co.kr/transport/flights/"
        f"{ORIGIN}/{DESTINATION}/{yymmdd(outbound)}/{yymmdd(inbound)}/"
    )
    return f"{path}?{urlencode(params)}"


def parse_price(text: str) -> int | None:
    digits = re.sub(r"[^\d]", "", text or "")
    return int(digits) if digits else None


def extract_from_unified_response(payload: dict[str, Any], outbound: str, inbound: str) -> FlightOffer | None:
    """Parse Skyscanner unified-search JSON response."""
    synced_at = datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds")

    context = payload.get("context") or {}
    stats = payload.get("itineraries") or {}
    buckets = stats.get("buckets") or []
    if not buckets:
        return None

    # Cheapest bucket first when sorted by price
    items = buckets[0].get("items") or []
    if not items:
        return None

    best = items[0]
    price_obj = best.get("price") or {}
    raw_price = price_obj.get("raw") or price_obj.get("amount")
    price_text = price_obj.get("formatted") or str(raw_price or "")

    legs = best.get("legs") or []
    durations = []
    carriers = []
    stops = []
    for leg in legs:
        dur = leg.get("durationInMinutes")
        if dur:
            h, m = divmod(int(dur), 60)
            durations.append(f"{h}시간 {m}분")
        for seg in leg.get("segments") or []:
            marketing = (seg.get("marketingCarrier") or {}).get("name")
            if marketing:
                carriers.append(marketing)
        stop_count = max(0, len(leg.get("segments") or []) - 1)
        stops.append("직항" if stop_count == 0 else f"경유 {stop_count}회")

    duration_text = " / ".join(durations) if durations else "정보 없음"
    carrier_text = ", ".join(dict.fromkeys(carriers)) or "정보 없음"
    stops_text = " / ".join(stops) if stops else "정보 없음"

    deeplink = best.get("deeplinkUrl") or ""
    itinerary_id = best.get("id") or ""
    seller_url = deeplink or build_search_url(outbound, inbound)

    skyscanner_url = build_search_url(outbound, inbound)

    return FlightOffer(
        outbound_date=outbound,
        return_date=inbound,
        price=int(raw_price) if raw_price is not None else parse_price(price_text),
        price_text=price_text or "가격 정보 없음",
        duration_text=duration_text,
        stops_text=stops_text,
        carrier_text=carrier_text,
        seller_url=seller_url,
        skyscanner_url=skyscanner_url,
        synced_at=synced_at,
    )


def scrape_pair_on_page(page, outbound: str, inbound: str, captured: list[dict[str, Any]]) -> FlightOffer | None:
    if outbound >= inbound:
        return None

    url = build_search_url(outbound, inbound)
    captured.clear()

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=90000)
        wait_for_human_captcha(page, first_run=False)
        page.wait_for_timeout(6000)

        deadline = time.time() + 45
        while time.time() < deadline and not captured:
            page.wait_for_timeout(1500)

        if not captured:
            return scrape_from_dom(page, outbound, inbound)

        for payload in reversed(captured):
            if payload.get("itineraries"):
                offer = extract_from_unified_response(payload, outbound, inbound)
                if offer:
                    return offer
        return None
    except PlaywrightTimeout:
        return None
    except Exception as exc:
        print(f"Error scraping {outbound}/{inbound}: {exc}", file=sys.stderr)
        return None


def sync_skyscanner_on_page(page, captured: list[dict[str, Any]], *, first_captcha: bool) -> list[FlightOffer]:
    pairs = build_search_pairs()
    offers: list[FlightOffer] = []

    first_url = build_search_url(pairs[0][0], pairs[0][1])
    page.goto(first_url, wait_until="domcontentloaded", timeout=90000)
    wait_for_human_captcha(page, first_run=first_captcha)

    for outbound, inbound in pairs:
        print(f"[Skyscanner] 출발 {outbound} / 귀국 {inbound} ...")
        offer = scrape_pair_on_page(page, outbound, inbound, captured)
        if offer:
            offers.append(offer)
            print(f"  Found: {offer.price_text} ({offer.duration_text})")

    offers.sort(key=lambda o: (o.price is None, o.price or 10**12))
    return offers


def collect_offers_with_browser() -> list[FlightOffer]:
    captured: list[dict[str, Any]] = []

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            USER_DATA_DIR.as_posix(),
            headless=HEADLESS,
            locale=LOCALE,
            viewport={"width": 1440, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
        )
        page = context.pages[0] if context.pages else context.new_page()

        def on_response(response):
            if "web-unified-search" in response.url and response.request.method == "POST":
                try:
                    captured.append(response.json())
                except Exception:
                    pass

        page.on("response", on_response)
        offers = sync_skyscanner_on_page(page, captured, first_captcha=True)
        context.close()

    return offers


def scrape_from_dom(page, outbound: str, inbound: str) -> FlightOffer | None:
    synced_at = datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds")

    # Captcha / block detection
    title = page.title()
    if "로봇" in title or "captcha" in page.url.lower():
        return None

    price_locators = [
        "[data-testid='price']",
        "[class*='Price']",
        "span:has-text('₩')",
    ]
    price_text = ""
    for sel in price_locators:
        loc = page.locator(sel).first
        if loc.count() and loc.is_visible():
            price_text = loc.inner_text(timeout=3000).strip()
            if "₩" in price_text:
                break

    duration_text = "정보 없음"
    dur_loc = page.locator("[data-testid='duration']").first
    if dur_loc.count():
        duration_text = dur_loc.inner_text(timeout=2000).strip()

    seller_url = build_search_url(outbound, inbound)
    book = page.locator("a:has-text('선택'), button:has-text('선택')").first
    if book.count():
        href = book.get_attribute("href")
        if href:
            seller_url = href if href.startswith("http") else f"https://www.skyscanner.co.kr{href}"

    if not price_text:
        return None

    return FlightOffer(
        outbound_date=outbound,
        return_date=inbound,
        price=parse_price(price_text),
        price_text=price_text,
        duration_text=duration_text,
        stops_text="DOM 파싱",
        carrier_text="DOM 파싱",
        seller_url=seller_url,
        skyscanner_url=build_search_url(outbound, inbound),
        synced_at=synced_at,
    )


def collect_offers() -> list[FlightOffer]:
    return collect_offers_with_browser()


def render_html(offers: list[FlightOffer], error: str | None = None) -> str:
    now_kst = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S KST")
    best = offers[0] if offers else None

    rows = ""
    for i, o in enumerate(offers[:10]):
        badge = "최저가" if i == 0 else ""
        rows += f"""
        <tr class="{'best' if i == 0 else ''}">
          <td>{badge}</td>
          <td>{o.outbound_date}</td>
          <td>{o.return_date}</td>
          <td class="price">{o.price_text}</td>
          <td>{o.duration_text}</td>
          <td>{o.stops_text}</td>
          <td>{o.carrier_text}</td>
          <td>
            <a class="cta-link" href="{o.seller_url}" target="_blank" rel="noopener noreferrer">
              <button type="button" class="BpkButton_bpk-button__NzMyO bpk-button--primary BpkButton_bpk-button--full-width__MjI1O" data-backpack-ds-component="Button">
                선택하기
                <span class="CtaButton_icon__ZDdkZ">
                  <span style="line-height: 1rem; display: inline-block; margin-top: 0.25rem; vertical-align: top;">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true" width="1rem" height="1rem" class="BpkIcon_bpk-icon--rtl-support__ZTc0N" fill="white" data-testid="white-arrow">
                      <path d="M3 12a1.5 1.5 0 0 0 1.5 1.5h11.379l-4.94 4.94a1.5 1.5 0 0 0 2.122 2.12l7.5-7.5a1.5 1.5 0 0 0 0-2.12l-7.5-7.5a1.5 1.5 0 0 0-2.122 2.12l4.94 4.94H4.5A1.5 1.5 0 0 0 3 12" clip-rule="evenodd"></path>
                    </svg>
                  </span>
                </span>
              </button>
            </a>
          </td>
        </tr>"""

    error_block = f'<div class="error">{error}</div>' if error else ""
    best_summary = ""
    if best:
        best_summary = f"""
        <section class="hero">
          <h2>현재 최저가</h2>
          <p class="hero-price">{best.price_text}</p>
          <p>출발 {best.outbound_date} · 귀국 {best.return_date}</p>
          <p>비행시간: {best.duration_text}</p>
          <a class="cta-link" href="{best.seller_url}" target="_blank" rel="noopener noreferrer">
            <button type="button" class="BpkButton_bpk-button__NzMyO bpk-button--primary BpkButton_bpk-button--full-width__MjI1O" data-backpack-ds-component="Button">
              판매자 사이트 가기 (선택하기)
              <span class="CtaButton_icon__ZDdkZ">
                <span style="line-height: 1rem; display: inline-block; margin-top: 0.25rem; vertical-align: top;">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true" width="1rem" height="1rem" fill="white">
                    <path d="M3 12a1.5 1.5 0 0 0 1.5 1.5h11.379l-4.94 4.94a1.5 1.5 0 0 0 2.122 2.12l7.5-7.5a1.5 1.5 0 0 0 0-2.12l-7.5-7.5a1.5 1.5 0 0 0-2.122 2.12l4.94 4.94H4.5A1.5 1.5 0 0 0 3 12" clip-rule="evenodd"></path>
                  </svg>
                </span>
              </span>
            </button>
          </a>
        </section>"""

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="refresh" content="21600">
  <title>서울 → 시카고(ORD) 항공권 | Skyscanner 동기화</title>
  <style>
    :root {{
      --brand: #0770e3;
      --bg: #f1f2f8;
      --card: #fff;
      --text: #161616;
      --muted: #626971;
      --best: #e8f4fd;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", "Noto Sans KR", sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }}
    .wrap {{ max-width: 1100px; margin: 0 auto; padding: 24px; }}
    header {{ margin-bottom: 24px; }}
    h1 {{ margin: 0 0 8px; font-size: 1.75rem; }}
    .meta {{ color: var(--muted); font-size: 0.95rem; }}
    .card {{
      background: var(--card);
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 2px 8px rgba(0,0,0,.06);
      margin-bottom: 20px;
    }}
    .hero {{ text-align: center; }}
    .hero-price {{ font-size: 2.2rem; font-weight: 700; color: var(--brand); margin: 8px 0; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 12px 10px; border-bottom: 1px solid #e0e4ea; text-align: left; vertical-align: middle; }}
    th {{ background: #fafbfc; font-size: 0.85rem; color: var(--muted); }}
    tr.best {{ background: var(--best); }}
    .price {{ font-weight: 700; color: var(--brand); }}
    .cta-link {{ text-decoration: none; }}
    .BpkButton_bpk-button__NzMyO {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      background: var(--brand);
      color: #fff;
      border: none;
      border-radius: 999px;
      padding: 10px 18px;
      font-size: 0.95rem;
      font-weight: 600;
      cursor: pointer;
      white-space: nowrap;
    }}
    .BpkButton_bpk-button--full-width__MjI1O {{ min-width: 140px; }}
    .error {{
      background: #fff3f3;
      border: 1px solid #ffbdbd;
      color: #a40000;
      padding: 12px 16px;
      border-radius: 8px;
      margin-bottom: 16px;
    }}
    .note {{ font-size: 0.85rem; color: var(--muted); }}
    footer {{ margin-top: 24px; text-align: center; color: var(--muted); font-size: 0.85rem; }}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>서울 → 시카고 오헤어(ORD) 항공권</h1>
      <p class="meta">
        성인 {ADULTS}명 · 유소아 {len(CHILD_AGES)}명 (만 {CHILD_AGES[0]}세, 만 {CHILD_AGES[1]}세) · 이코노미<br>
        가는편: 2026-09-24 (고정) · 오는편 후보: 10/8, 10/9, 10/10, 10/11, 10/12, 10/13<br>
        마지막 동기화: {now_kst} · 6시간마다 자동 갱신
      </p>
    </header>

    {error_block}
    {best_summary}

    <section class="card">
      <h2>검색 결과 TOP {min(len(offers), 10)}</h2>
      <table>
        <thead>
          <tr>
            <th></th>
            <th>가는편</th>
            <th>오는편</th>
            <th>최저가</th>
            <th>비행시간</th>
            <th>경유</th>
            <th>항공사</th>
            <th>예약</th>
          </tr>
        </thead>
        <tbody>
          {rows if rows else '<tr><td colspan="8">검색 결과가 없습니다. sync_flights.py를 실행해 주세요.</td></tr>'}
        </tbody>
      </table>
      <p class="note" style="margin-top:12px;">
        ※ 출발 9/24 오전 · 귀국 10/8~10/13 조합으로 각각 검색한 결과입니다.
      </p>
    </section>

    <footer>
      데이터 출처: <a href="https://www.skyscanner.co.kr/" target="_blank">Skyscanner</a>
    </footer>
  </div>
</body>
</html>"""


def main() -> int:
    error = None
    offers: list[FlightOffer] = []

    try:
        offers = collect_offers()
        if not offers:
            error = (
                "Skyscanner에서 결과를 가져오지 못했습니다. "
                "CAPTCHA 차단 시 .browser_profile 폴더를 삭제 후 "
                "sync_once.bat을 수동 실행해 주세요."
            )
            if STATE_FILE.exists():
                offers = [FlightOffer(**o) for o in json.loads(STATE_FILE.read_text(encoding="utf-8"))]
    except Exception as exc:
        error = str(exc)
        if STATE_FILE.exists():
            offers = [FlightOffer(**o) for o in json.loads(STATE_FILE.read_text(encoding="utf-8"))]

    if offers:
        STATE_FILE.write_text(
            json.dumps([asdict(o) for o in offers], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    if error:
        print(f"Warning: {error}", file=sys.stderr)

    import build_html

    build_html.main()
    return 0 if offers else 1


if __name__ == "__main__":
    raise SystemExit(main())
