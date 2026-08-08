#!/usr/bin/env python3
"""Scrape KAYAK hotel totals for curated NYC picks + city lodging budget samples."""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import quote_plus

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUT_FILE = ROOT / "nyc_hotel_prices.json"
USER_DATA_DIR = ROOT / ".browser_profile_capture"

CHECKIN = "2026-09-23"
CHECKOUT = "2026-09-25"
NIGHTS = 2
GUESTS = "2adults/children-7-8"
SOURCE = "KAYAK"

# Same curated list as itinerary_plans.NYC_HOTEL_RECS (id + query)
HOTELS = [
    ("broadwayts", "Broadway at Times Square Hotel"),
    ("rownyc", "Row NYC Times Square"),
    ("fairfield", "Fairfield Inn Suites New York Manhattan Times Square"),
    ("edison", "Hotel Edison Times Square"),
    ("hiexpress", "Holiday Inn Express New York City Times Square"),
    ("newyorker", "The New Yorker A Wyndham Hotel"),
    ("parkcentral", "Park Central Hotel New York"),
    ("msocial", "M Social Hotel New York Times Square"),
    ("homewood", "Homewood Suites Midtown Manhattan Times Square South"),
    ("westin", "The Westin New York at Times Square"),
]

CITY_SEARCHES = [
    ("nyc", "Manhattan Midtown New York", "Times Square · Midtown"),
    ("dc", "Washington DC Downtown", "National Mall · Downtown DC"),
    ("bos", "Boston Back Bay", "Downtown · Back Bay"),
]


def now_kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%dT%H:%M:%S+09:00")


def kayak_url(query: str) -> str:
    return (
        f"https://www.kayak.co.kr/hotels/{quote_plus(query)}/"
        f"{CHECKIN}/{CHECKOUT}/{GUESTS}?sort=price_a"
    )


def dismiss(page) -> None:
    page.evaluate(
        """() => {
      const b = [...document.querySelectorAll('button')].find(el =>
        /^(동의합니다|모두 동의|Accept all|Accept|Agree|I agree)$/i.test((el.innerText || '').trim())
      );
      if (b) b.click();
    }"""
    )


def extract_prices(page) -> list[int]:
    """Return KRW totals found on the results page (lowest first)."""
    raw = page.evaluate(
        """() => {
      const text = document.body.innerText || '';
      const out = [];
      const re = /([\\d,]+)\\s*원/g;
      let m;
      while ((m = re.exec(text)) !== null) {
        const n = parseInt(m[1].replace(/,/g, ''), 10);
        if (n >= 200000 && n <= 20000000) out.push(n);
      }
      // Prefer prices near hotel result blocks
      const blocks = text.split(/\\n+/);
      const near = [];
      for (let i = 0; i < blocks.length; i++) {
        const line = blocks[i];
        const pm = line.match(/([\\d,]+)\\s*원/);
        if (!pm) continue;
        const n = parseInt(pm[1].replace(/,/g, ''), 10);
        if (n < 200000 || n > 20000000) continue;
        const ctx = blocks.slice(Math.max(0, i - 3), i + 2).join(' ');
        if (/세금|수수료|총액|박|숙박|무료 취소|평점|리뷰|★|성급/.test(ctx) || /원/.test(line)) {
          near.push(n);
        }
      }
      return { all: out, near };
    }"""
    )
    near = raw.get("near") or []
    allp = raw.get("all") or []
    prices = near if near else allp
    # Dedupe preserving order, then sort
    seen = set()
    uniq = []
    for p in prices:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return sorted(uniq)


def scrape_one(page, query: str) -> dict:
    url = kayak_url(query)
    print(f"\n== {query}")
    print(url)
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=90000)
    except PlaywrightTimeout:
        print("  nav timeout")
    time.sleep(4)
    dismiss(page)
    time.sleep(2)
    # Wait for won prices
    for _ in range(12):
        prices = extract_prices(page)
        if prices:
            break
        time.sleep(2)
        dismiss(page)
    prices = extract_prices(page)
    if not prices:
        title = page.title()
        print(f"  NO PRICE | title={title[:80]}")
        return {"query": query, "url": url, "price": None, "prices": [], "source": SOURCE}
    low = prices[0]
    print(f"  lowest ₩{low:,}  (sample {prices[:5]})")
    return {
        "query": query,
        "url": url,
        "price": low,
        "prices": prices[:8],
        "source": SOURCE,
        "checked_at": now_kst(),
    }


def main() -> None:
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    hotels_out = []
    cities_out = []
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=True,
            locale="ko-KR",
            viewport={"width": 1400, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        for hid, query in HOTELS:
            row = scrape_one(page, query)
            row["id"] = hid
            hotels_out.append(row)
            time.sleep(1.5)
        for key, query, area in CITY_SEARCHES:
            row = scrape_one(page, query)
            row["city"] = key
            row["area"] = area
            cities_out.append(row)
            time.sleep(1.5)
        ctx.close()

    payload = {
        "checked_at": now_kst(),
        "checkin": CHECKIN,
        "checkout": CHECKOUT,
        "nights": NIGHTS,
        "guests": "2 adults + children 7,8",
        "source": SOURCE,
        "hotels": hotels_out,
        "cities": cities_out,
    }
    OUT_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT_FILE}")
    ok = sum(1 for h in hotels_out if h.get("price"))
    print(f"Hotels with price: {ok}/{len(hotels_out)}")
    okc = sum(1 for c in cities_out if c.get("price"))
    print(f"Cities with price: {okc}/{len(cities_out)}")


if __name__ == "__main__":
    main()
