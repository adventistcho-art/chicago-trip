#!/usr/bin/env python3
"""Scrape live KAYAK one-way NYC → ORD prices (no estimates)."""

from __future__ import annotations

import json
import os
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
GUESTS = 4  # 1인 × 4
ROUTE = "nyc_chi"
ROUTE_LABEL = "뉴욕 → 시카고"


def now_kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%dT%H:%M:%S+09:00")


def kayak_url(depart: str, sort: str) -> str:
    # Family of 4; KAYAK shows per-adult KRW for domestic often as adult fare
    return (
        f"https://www.kayak.co.kr/flights/NYC-ORD/{depart}/"
        "2adults/children-7-8?sort=" + sort
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


def extract_results(page, limit: int = 60) -> list[dict]:
    """Same block parser style as sync_route_compare (proven on KAYAK KR)."""
    return page.evaluate(
        """(limit) => {
      const carrierRe = /항공|Air|United|Delta|American|Spirit|Frontier|JetBlue|Southwest|알래스카|델타|아메리칸|유나이티드|제트블루|프론티어/i;
      const parseBlock = (b) => {
        const pm = b.match(/([\\d,]+)원/);
        if (!pm) return null;
        const price = parseInt(pm[1].replace(/,/g, ''), 10);
        // Domestic one-way per person (KRW)
        if (!price || price < 40000 || price > 2500000) return null;
        const lines = b.split('\\n').map(s => s.trim()).filter(Boolean);
        const carrier = lines.find(l => carrierRe.test(l)) || '';
        const durs = b.match(/(\\d+시간\\s*\\d+분)/g) || [];
        const dursMin = b.match(/(\\d+분)/g) || [];
        const duration_text = (durs[0] || dursMin[0] || '');
        if (!duration_text && !/직항|경유/.test(b)) return null;
        const stops = (b.match(/(\\d+회\\s*경유|직항)/g) || []).slice(0, 1);
        return {
          price_per_person: price,
          duration_text,
          stops_text: stops[0] || '',
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
    for y in (700, 1400, 2200, 3200, 4500):
        page.evaluate(f"window.scrollTo(0, {y})")
        page.wait_for_timeout(600)


def wait_results(page, timeout_s: float = 55) -> list[dict]:
    deadline = time.time() + timeout_s
    best: list[dict] = []
    while time.time() < deadline:
        dismiss(page)
        scroll_results(page)
        rows = extract_results(page, limit=60)
        if len(rows) > len(best):
            best = rows
        title = page.title() or ""
        if "verify" in title.lower() or "로봇" in title:
            print("  bot challenge page — waiting for pass...")
            time.sleep(3)
            continue
        body = page.inner_text("body")
        if len(best) >= 5 and ("결과" in body or "완료" in body or "원" in body):
            return best
        time.sleep(0.8)
    scroll_results(page)
    return extract_results(page, limit=60) or best


def parse_duration_minutes(text: str) -> int | None:
    m = re.search(r"(\d+)\s*시간\s*(\d+)\s*분", text or "")
    if m:
        return int(m.group(1)) * 60 + int(m.group(2))
    m2 = re.search(r"(\d+)\s*분", text or "")
    if m2:
        return int(m2.group(1))
    return None


def enrich(row: dict, url: str, kind: str) -> dict:
    pp = int(row["price_per_person"])
    total = pp * GUESTS
    return {
        "kind": kind,
        "price_per_person": pp,
        "price_per_person_text": f"₩{pp:,}",
        "price": total,
        "price_text": f"₩{total:,}",
        "duration_text": row.get("duration_text") or "",
        "duration_minutes": parse_duration_minutes(row.get("duration_text") or ""),
        "stops_text": row.get("stops_text") or "",
        "carrier_text": row.get("carrier_text") or "",
        "self_transfer": bool(row.get("self_transfer")),
        "seller_url": url,
        "synced_at": now_kst(),
        "source": "KAYAK",
        "estimate": False,
    }


def scrape_day(page, depart: str) -> dict:
    cheap_url = kayak_url(depart, "price_a")
    short_url = kayak_url(depart, "duration_a")
    print(f"\n== NYC->ORD {depart}")
    print(cheap_url)
    try:
        page.goto(cheap_url, wait_until="domcontentloaded", timeout=90000)
    except PlaywrightTimeout:
        print("  nav timeout (cheap)")
    page.wait_for_timeout(2500)
    dismiss(page)
    price_rows = wait_results(page)
    cheapest = enrich(price_rows[0], cheap_url, "cheapest") if price_rows else None
    if cheapest:
        print(f"  cheapest {cheapest['price_per_person']:,} KRW | {cheapest['duration_text']}")
    else:
        print("  cheapest FAILED")

    print(short_url)
    try:
        page.goto(short_url, wait_until="domcontentloaded", timeout=90000)
    except PlaywrightTimeout:
        print("  nav timeout (short)")
    page.wait_for_timeout(2000)
    dismiss(page)
    short_rows = wait_results(page, timeout_s=50)
    shortest = None
    if short_rows:
        ranked = [enrich(r, short_url, "shortest") for r in short_rows[:20]]
        ranked.sort(key=lambda x: (x.get("duration_minutes") or 10**9, x["price"]))
        shortest = ranked[0]
        print(f"  shortest {shortest['price_per_person']:,} KRW | {shortest['duration_text']}")
    else:
        print("  shortest FAILED")

    return {
        "depart_date": depart,
        "route": ROUTE,
        "route_label": ROUTE_LABEL,
        "cheapest": cheapest,
        "shortest": shortest,
        "seller_urls": {"cheapest": cheap_url, "shortest": short_url},
        "synced_at": now_kst(),
    }


def load_previous() -> dict[str, dict]:
    if not OUT_FILE.exists():
        return {}
    try:
        rows = json.loads(OUT_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return {r["depart_date"]: r for r in rows if r.get("depart_date")}


def merge_keep_real(new_day: dict, prev: dict | None) -> dict:
    """Never invent estimates. Keep prior live quote if this scrape failed."""
    if new_day.get("cheapest") and not new_day["cheapest"].get("estimate"):
        return new_day
    if prev and prev.get("cheapest") and not prev["cheapest"].get("estimate"):
        print(f"  keep previous live quote for {new_day['depart_date']}")
        kept = dict(prev)
        kept["seller_urls"] = new_day.get("seller_urls") or prev.get("seller_urls")
        kept["note"] = "이번 수집 실패 · 직전 실검색가 유지"
        kept["synced_at"] = prev.get("synced_at")
        return kept
    # No prior live data — store links only (no fake price)
    return {
        "depart_date": new_day["depart_date"],
        "route": ROUTE,
        "route_label": ROUTE_LABEL,
        "cheapest": None,
        "shortest": None,
        "seller_urls": new_day.get("seller_urls") or {},
        "synced_at": now_kst(),
        "note": "실검색 실패 · KAYAK 링크만 제공",
    }


def headless_mode() -> bool:
    return os.environ.get("SYNC_HEADLESS", "").lower() in ("1", "true", "yes")


def main() -> int:
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    prev_by_date = load_previous()
    results = []
    # Prefer headed like route_compare — fewer bot blocks
    headless = headless_mode()
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=headless,
            locale="ko-KR",
            viewport={"width": 1400, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        for depart in DEPART_DATES:
            try:
                day = scrape_day(page, depart)
            except Exception as exc:
                print(f"  error {exc}")
                day = {
                    "depart_date": depart,
                    "route": ROUTE,
                    "route_label": ROUTE_LABEL,
                    "cheapest": None,
                    "shortest": None,
                    "seller_urls": {
                        "cheapest": kayak_url(depart, "price_a"),
                        "shortest": kayak_url(depart, "duration_a"),
                    },
                    "synced_at": now_kst(),
                }
            results.append(merge_keep_real(day, prev_by_date.get(depart)))
            time.sleep(1.2)
        ctx.close()

    OUT_FILE.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT_FILE}")
    ok = sum(1 for d in results if d.get("cheapest") and not d["cheapest"].get("estimate"))
    print(f"Live quotes: {ok}/{len(results)}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
