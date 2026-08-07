#!/usr/bin/env python3
"""Collect KAYAK 1-adult cheapest + shortest for CHI roundtrip and NYC-in/CHI-out."""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
USER_DATA_DIR = ROOT / ".browser_profile_capture"
OUTBOUND = "2026-09-23"
RETURN_DATES = [
    "2026-10-08",
    "2026-10-09",
    "2026-10-10",
    "2026-10-11",
    "2026-10-12",
    "2026-10-13",
]
GUESTS = 4  # dashboard total = 1인 × 4
MAX_CHEAP_UNDER_17H = 5
MAX_LEG_MINUTES = 17 * 60

ROUTES = {
    "chi_round": {
        "label": "시카고 인 · 시카고 아웃",
        "short": "시카고왕복",
        "file": ROOT / "route_chi_roundtrip.json",
        "url": lambda ret, sort: (
            f"https://www.kayak.co.kr/flights/SEL-ORD/{OUTBOUND}/{ret}/1adults?sort={sort}"
        ),
    },
    "nyc_in": {
        "label": "뉴욕 인 · 시카고 아웃",
        "short": "뉴욕인·시카고아웃",
        "file": ROOT / "route_nyc_in_chi_out.json",
        "url": lambda ret, sort: (
            f"https://www.kayak.co.kr/flights/SEL-NYC/{OUTBOUND}/ORD-SEL/{ret}/1adults?sort={sort}"
        ),
    },
}

SORTS = {
    "cheapest": "price_a",
    "shortest": "duration_a",
}


def now_kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%dT%H:%M:%S+09:00")


def leg_minutes(duration_text: str) -> list[int]:
    return [int(h) * 60 + int(m) for h, m in re.findall(r"(\d+)\s*시간\s*(\d+)\s*분", duration_text or "")]


def within_17h(duration_text: str) -> bool:
    legs = leg_minutes(duration_text)
    return bool(legs) and all(m <= MAX_LEG_MINUTES for m in legs)


def flight_fingerprint(row: dict) -> tuple:
    return (
        row.get("price_per_person"),
        row.get("duration_text"),
        row.get("carrier_text"),
    )


def dismiss(page) -> None:
    page.evaluate(
        """() => {
      const buttons = [...document.querySelectorAll('button, [role="button"]')];
      const target = buttons.find(el => {
        const t = (el.innerText || '').replace(/\\s+/g, ' ').trim();
        return /^(동의합니다|모두 동의|Accept all|Accept|Agree)$/i.test(t);
      });
      if (target) target.click();
    }"""
    )


def parse_duration_minutes(text: str) -> int | None:
    legs = leg_minutes(text)
    if not legs:
        return None
    return sum(legs)


def extract_top(page) -> dict | None:
    rows = extract_results(page, limit=1)
    return rows[0] if rows else None


def extract_results(page, limit: int = 60) -> list[dict]:
    return page.evaluate(
        """(limit) => {
      const carrierRe = /항공|Air|United|Delta|Korean|Asiana|에어|알래스카|델타|대한|아시아나|에바|아메리칸|터키|캐세이|프론티어|캐나다|제트블루|ANA|JAL/i;
      const parseBlock = (b) => {
        const pm = b.match(/([\\d,]+)원/);
        if (!pm) return null;
        const price = parseInt(pm[1].replace(/,/g, ''), 10);
        if (!price || price < 200000) return null;
        const lines = b.split('\\n').map(s => s.trim()).filter(Boolean);
        const carrier = lines.find(l => carrierRe.test(l)) || '';
        const durs = b.match(/(\\d+시간\\s*\\d+분)/g) || [];
        if (!durs.length) return null;
        const stops = (b.match(/(\\d+회\\s*경유|직항)/g) || []).slice(0, 2);
        return {
          price_per_person: price,
          price_text_pp: pm[1] + '원',
          duration_text: durs.slice(0, 2).join(' / ') || '',
          stops_text: stops.join(' / ') || '',
          carrier_text: carrier,
          self_transfer: b.includes('자가 환승'),
        };
      };
      const out = [];
      const seen = new Set();
      const push = (row) => {
        if (!row) return;
        const key = row.price_per_person + '|' + row.duration_text + '|' + row.carrier_text;
        if (seen.has(key)) return;
        seen.add(key);
        out.push(row);
      };
      const text = document.body.innerText || '';
      for (const b of text.split('다음 검색 결과로 이동').slice(1)) {
        push(parseBlock(b));
        if (out.length >= limit) return out;
      }
      const priceRe = /([\\d,]+)원/g;
      let m;
      while ((m = priceRe.exec(text)) !== null) {
        push(parseBlock(text.slice(Math.max(0, m.index - 40), m.index + 420)));
        if (out.length >= limit) break;
      }
      return out;
    }""",
        limit,
    )


def scroll_results(page) -> None:
    for y in (700, 1400, 2200, 3200, 4500, 6000):
        page.evaluate(f"window.scrollTo(0, {y})")
        page.wait_for_timeout(700)


def wait_results(page, timeout_s: float = 50) -> list[dict]:
    deadline = time.time() + timeout_s
    best: list[dict] = []
    while time.time() < deadline:
        dismiss(page)
        scroll_results(page)
        rows = extract_results(page, limit=60)
        if len(rows) > len(best):
            best = rows
        body = page.inner_text("body")
        if len(best) >= 8 and ("결과" in body or "완료" in body):
            return best
        time.sleep(0.7)
    scroll_results(page)
    return extract_results(page, limit=60) or best


def pick_cheap_under_17h(
    price_rows: list[dict], url: str, skip: set[tuple]
) -> list[dict]:
    picked: list[dict] = []
    for info in price_rows:
        if not within_17h(info.get("duration_text") or ""):
            continue
        row = enrich(info, url, "cheap17")
        fp = flight_fingerprint(row)
        if fp in skip:
            continue
        skip.add(fp)
        picked.append(row)
        if len(picked) >= MAX_CHEAP_UNDER_17H:
            break
    return picked


def enrich(info: dict, url: str, kind: str) -> dict:
    pp = info["price_per_person"]
    total = pp * GUESTS
    return {
        "kind": kind,
        "price_per_person": pp,
        "price_per_person_text": f"₩{pp:,}",
        "price": total,
        "price_text": f"₩{total:,}",
        "duration_text": info.get("duration_text") or "-",
        "duration_minutes": parse_duration_minutes(info.get("duration_text") or ""),
        "stops_text": info.get("stops_text") or "-",
        "carrier_text": info.get("carrier_text") or "-",
        "self_transfer": bool(info.get("self_transfer")),
        "seller_url": url,
        "synced_at": now_kst(),
    }


def main() -> int:
    results: dict[str, list[dict]] = {k: [] for k in ROUTES}

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            viewport={"width": 430, "height": 920},
            locale="ko-KR",
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.pages[0] if context.pages else context.new_page()

        for route_key, route in ROUTES.items():
            by_date: dict[str, dict] = {}
            for ret in RETURN_DATES:
                by_date[ret] = {
                    "outbound_date": OUTBOUND,
                    "return_date": ret,
                    "route": route_key,
                    "route_label": route["label"],
                }
                price_url = route["url"](ret, SORTS["cheapest"])
                print(f"\n=== {route['short']} | {ret} | cheapest + 17h ===")
                print(price_url)
                try:
                    page.goto(price_url, wait_until="domcontentloaded", timeout=60000)
                except PlaywrightTimeout:
                    print("nav timeout (price)")
                page.wait_for_timeout(2000)
                dismiss(page)
                price_rows = wait_results(page)
                if price_rows:
                    cheap_row = enrich(price_rows[0], price_url, "cheapest")
                    by_date[ret]["cheapest"] = cheap_row
                    print(
                        f"  cheapest {cheap_row['price_per_person']:,} | {cheap_row['duration_text']}"
                    )
                else:
                    by_date[ret]["cheapest"] = None
                    print("  cheapest FAILED")

                skip: set[tuple] = set()
                if by_date[ret].get("cheapest"):
                    skip.add(flight_fingerprint(by_date[ret]["cheapest"]))

                short_url = route["url"](ret, SORTS["shortest"])
                print(f"=== {route['short']} | {ret} | shortest ===")
                print(short_url)
                try:
                    page.goto(short_url, wait_until="domcontentloaded", timeout=60000)
                except PlaywrightTimeout:
                    print("nav timeout (shortest)")
                page.wait_for_timeout(2000)
                dismiss(page)
                short_rows = wait_results(page, timeout_s=50)
                if short_rows:
                    short_row = enrich(short_rows[0], short_url, "shortest")
                    by_date[ret]["shortest"] = short_row
                    skip.add(flight_fingerprint(short_row))
                    print(
                        f"  shortest {short_row['price_per_person']:,} | {short_row['duration_text']}"
                    )
                else:
                    by_date[ret]["shortest"] = None
                    print("  shortest FAILED")

                under_17 = pick_cheap_under_17h(price_rows or [], price_url, skip)
                by_date[ret]["cheap_under_17h"] = under_17
                print(f"  17h under {len(under_17)} options")
                for i, row in enumerate(under_17, 1):
                    print(
                        f"    {i}. {row['price_per_person']:,} | {row['duration_text']} | {row['carrier_text']}"
                    )
            results[route_key] = [by_date[d] for d in RETURN_DATES]

        context.close()

    for route_key, route in ROUTES.items():
        path = route["file"]
        path.write_text(
            json.dumps(results[route_key], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"wrote {path.name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
