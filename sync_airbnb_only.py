#!/usr/bin/env python3
"""Scrape Airbnb lodging only (after check-in / listing URL changes)."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

import build_html
from sync_all import (
    AIRBNB_FILE,
    LOCALE,
    USER_DATA_DIR,
    deploy_to_github,
    headless_mode,
    load_json_list,
    log,
    save_json,
    scrape_airbnb,
)

ROOT = Path(__file__).resolve().parent
LISTINGS_FILE = ROOT / "lodging_listings.json"


def nights(checkin: str, checkout: str) -> int:
    a = datetime.strptime(checkin, "%Y-%m-%d")
    b = datetime.strptime(checkout, "%Y-%m-%d")
    return (b - a).days


def build_lodging_rows(checkin: str) -> list[dict]:
    prev = {row["checkout_date"]: row for row in load_json_list(AIRBNB_FILE)}
    templates = json.loads(LISTINGS_FILE.read_text(encoding="utf-8"))
    rows = []
    for tpl in templates:
        checkout = tpl["checkout_date"]
        url = (
            f"https://www.airbnb.co.kr/rooms/{tpl['room_id']}"
            f"?adults=2&check_in={checkin}&check_out={checkout}&children=2"
        )
        base = prev.get(checkout, {})
        rows.append(
            {
                "checkin": checkin,
                "checkout_date": checkout,
                "nights": nights(checkin, checkout),
                "price": base.get("price"),
                "price_text": base.get("price_text", "-"),
                "title": tpl["title"],
                "location_text": tpl["location_text"],
                "distance_text": tpl["distance_text"],
                "distance_km": tpl.get("distance_km"),
                "amenities_text": tpl["amenities_text"],
                "seller_url": url,
                "synced_at": base.get("synced_at"),
            }
        )
    return rows


def main() -> int:
    checkin = build_html.CHECKIN
    log(f"=== Airbnb only · 체크인 {checkin} ===")
    rows = build_lodging_rows(checkin)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            USER_DATA_DIR.as_posix(),
            headless=headless_mode(),
            locale=LOCALE,
            viewport={"width": 1440, "height": 900},
        )
        page = context.pages[0] if context.pages else context.new_page()
        rows = [scrape_airbnb(page, entry) for entry in rows]
        context.close()

    save_json(AIRBNB_FILE, rows)
    build_html.main()
    deploy_to_github()
    log("=== Airbnb 동기화 완료 ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
