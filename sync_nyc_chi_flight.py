#!/usr/bin/env python3
"""Scrape KAYAK one-way NYC → ORD (domestic) for family trip bridge days."""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUT_FILE = ROOT / "route_nyc_to_chi.json"
USER_DATA_DIR = ROOT / ".browser_profile_capture"

DEPART_DATES = ["2026-09-26", "2026-09-27"]
GUESTS = 4  # 1인 요금 × 4
ROUTE = "nyc_chi"
ROUTE_LABEL = "뉴욕 → 시카고"


def now_kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%dT%H:%M:%S+09:00")


def kayak_url(depart: str, sort: str) -> str:
    return f"https://www.kayak.co.kr/flights/NYC-ORD/{depart}/1adults?sort={sort}"


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


def extract_results(page, limit: int = 40) -> list[dict]:
    return page.evaluate(
        """(limit) => {
      const carrierRe = /항공|Air|United|Delta|American|Spirit|Frontier|JetBlue|Southwest|알래스카|델타|아메리칸|유나이티드|제트블루/i;
      const text = document.body.innerText || '';
      const blocks = text.split(/결과 카드|결과로 이동|다음 결과/).length > 1
        ? text.split(/결과로 이동|다음 결과/)
        : text.split('\\n\\n');
      const out = [];
      const seen = new Set();
      for (const b of blocks) {
        const pm = b.match(/([\\d,]+)원/);
        if (!pm) continue;
        const price = parseInt(pm[1].replace(/,/g, ''), 10);
        // Domestic one-way per person: typically 80k–800k KRW
        if (!price || price < 50000 || price > 3000000) continue;
        const lines = b.split('\\n').map(s => s.trim()).filter(Boolean);
        const carrier = lines.find(l => carrierRe.test(l)) || '';
        const durs = b.match(/(\\d+시간\\s*\\d+분|\\d+분)/g) || [];
        if (!durs.length && !/직항|경유/.test(b)) continue;
        const stops = (b.match(/(\\d+회\\s*경유|직항)/g) || []).slice(0, 1);
        const key = price + '|' + (durs[0] || '') + '|' + carrier;
        if (seen.has(key)) continue;
        seen.add(key);
        out.push({
          price_per_person: price,
          duration_text: durs[0] || '',
          stops_text: stops[0] || '',
          carrier_text: carrier,
        });
        if (out.length >= limit) break;
      }
      return out;
    }""",
        limit,
    )


def enrich(row: dict, url: str, kind: str) -> dict:
    pp = int(row["price_per_person"])
    total = pp * GUESTS
    mins = None
    m = re.search(r"(\d+)\s*시간\s*(\d+)\s*분", row.get("duration_text") or "")
    if m:
        mins = int(m.group(1)) * 60 + int(m.group(2))
    else:
        m2 = re.search(r"(\d+)\s*분", row.get("duration_text") or "")
        if m2:
            mins = int(m2.group(1))
    return {
        "kind": kind,
        "price_per_person": pp,
        "price_per_person_text": f"₩{pp:,}",
        "price": total,
        "price_text": f"₩{total:,}",
        "duration_text": row.get("duration_text") or "",
        "duration_minutes": mins,
        "stops_text": row.get("stops_text") or "",
        "carrier_text": row.get("carrier_text") or "",
        "self_transfer": False,
        "seller_url": url,
        "synced_at": now_kst(),
        "source": "KAYAK",
    }


def scrape_day(page, depart: str) -> dict:
    cheap_url = kayak_url(depart, "price_a")
    short_url = kayak_url(depart, "duration_a")
    print(f"\n== NYC→ORD {depart}")
    print(cheap_url)
    try:
        page.goto(cheap_url, wait_until="domcontentloaded", timeout=90000)
    except PlaywrightTimeout:
        print("  nav timeout (cheap)")
    time.sleep(5)
    dismiss(page)
    rows = []
    for _ in range(10):
        rows = extract_results(page)
        if rows:
            break
        time.sleep(2)
        dismiss(page)
    cheapest = enrich(rows[0], cheap_url, "cheapest") if rows else None
    if cheapest:
        print(f"  cheapest {cheapest['price_per_person_text']} · {cheapest['duration_text']}")

    try:
        page.goto(short_url, wait_until="domcontentloaded", timeout=90000)
    except PlaywrightTimeout:
        print("  nav timeout (short)")
    time.sleep(4)
    dismiss(page)
    short_rows = []
    for _ in range(8):
        short_rows = extract_results(page)
        if short_rows:
            break
        time.sleep(2)
    # Prefer shortest duration among top results
    shortest = None
    if short_rows:
        with_mins = []
        for r in short_rows[:15]:
            e = enrich(r, short_url, "shortest")
            with_mins.append(e)
        with_mins.sort(key=lambda x: (x.get("duration_minutes") or 10**9, x["price"]))
        shortest = with_mins[0]
        print(f"  shortest {shortest['price_per_person_text']} · {shortest['duration_text']}")

    return {
        "depart_date": depart,
        "route": ROUTE,
        "route_label": ROUTE_LABEL,
        "cheapest": cheapest,
        "shortest": shortest,
        "seller_urls": {"cheapest": cheap_url, "shortest": short_url},
        "synced_at": now_kst(),
    }


def seed_day(depart: str) -> dict:
    """Fallback when scrape is blocked — keep deep links + indicative estimate."""
    # ~USD 220 pp × 4 ≈ ₩1.2M family one-way (indicative)
    estimate_pp = 300_000
    total = estimate_pp * GUESTS
    cheap_url = kayak_url(depart, "price_a")
    short_url = kayak_url(depart, "duration_a")
    base = {
        "kind": "cheapest",
        "price_per_person": estimate_pp,
        "price_per_person_text": f"₩{estimate_pp:,}",
        "price": total,
        "price_text": f"₩{total:,}",
        "duration_text": "약 2시간 30분",
        "duration_minutes": 150,
        "stops_text": "직항 후보",
        "carrier_text": "KAYAK 검색 확인",
        "self_transfer": False,
        "seller_url": cheap_url,
        "synced_at": now_kst(),
        "source": "KAYAK",
        "estimate": True,
    }
    short = dict(base)
    short.update({"kind": "shortest", "seller_url": short_url})
    return {
        "depart_date": depart,
        "route": ROUTE,
        "route_label": ROUTE_LABEL,
        "cheapest": base,
        "shortest": short,
        "seller_urls": {"cheapest": cheap_url, "shortest": short_url},
        "synced_at": now_kst(),
        "note": "스크래핑 실패 시 추정가 · KAYAK에서 확정",
    }


def main() -> int:
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=True,
            locale="ko-KR",
            viewport={"width": 1400, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        for depart in DEPART_DATES:
            try:
                day = scrape_day(page, depart)
                if not day.get("cheapest"):
                    print("  fallback seed")
                    day = seed_day(depart)
            except Exception as exc:
                print(f"  error {exc} · seed")
                day = seed_day(depart)
            results.append(day)
            time.sleep(1.5)
        ctx.close()

    OUT_FILE.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT_FILE}")
    return 0 if any(d.get("cheapest") for d in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
