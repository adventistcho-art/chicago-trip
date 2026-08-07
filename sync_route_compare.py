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


def parse_duration_minutes(text: str) -> int | None:
    parts = re.findall(r"(\d+)\s*시간\s*(\d+)\s*분", text or "")
    if not parts:
        return None
    return sum(int(h) * 60 + int(m) for h, m in parts)


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


def extract_top(page) -> dict | None:
    return page.evaluate(
        """() => {
      const text = document.body.innerText || '';
      const blocks = text.split('다음 검색 결과로 이동').slice(1);
      for (const b of blocks) {
        const pm = b.match(/([\\d,]+)원/);
        if (!pm) continue;
        const lines = b.split('\\n').map(s => s.trim()).filter(Boolean);
        const carrier = lines.find(l =>
          /항공|Air|United|Delta|Korean|Asiana|에어|알래스카|델타|대한|아시아나|에바|아메리칸|터키|캐세이|프론티어|캐나다|제트블루|ANA|JAL/i.test(l)
        ) || '';
        const durs = b.match(/(\\d+시간\\s*\\d+분)/g) || [];
        const stops = (b.match(/(\\d+회\\s*경유|직항)/g) || []).slice(0, 2);
        return {
          price_per_person: parseInt(pm[1].replace(/,/g, ''), 10),
          price_text_pp: pm[1] + '원',
          duration_text: durs.slice(0, 2).join(' / ') || '',
          stops_text: stops.join(' / ') || '',
          carrier_text: carrier,
          self_transfer: b.includes('자가 환승'),
        };
      }
      return null;
    }"""
    )


def wait_top(page, timeout_s: float = 50) -> dict | None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        dismiss(page)
        info = extract_top(page)
        body = page.inner_text("body")
        if info and ("결과" in body or "완료" in body):
            return info
        time.sleep(0.7)
    return extract_top(page)


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
                for kind, sort in SORTS.items():
                    url = route["url"](ret, sort)
                    print(f"\n=== {route['short']} | {ret} | {kind} ===")
                    print(url)
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    except PlaywrightTimeout:
                        print("nav timeout")
                    page.wait_for_timeout(2000)
                    dismiss(page)
                    info = wait_top(page)
                    if not info:
                        print("FAILED")
                        by_date[ret][kind] = None
                        continue
                    row = enrich(info, url, kind)
                    by_date[ret][kind] = row
                    print(
                        f"  {row['price_per_person']:,} KRW | {row['duration_text']} | {row['carrier_text']}"
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
