#!/usr/bin/env python3
"""Sync Skyscanner, KAYAK, Google Flights, Airbnb and rebuild flights.html."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import traceback
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import quote

from playwright.sync_api import sync_playwright

import build_html
from sync_flights import (
    HEADLESS,
    LOCALE,
    OUTBOUND_DATE,
    RETURN_DATES,
    USER_DATA_DIR,
    FlightOffer,
    asdict,
    parse_price,
    sync_skyscanner_on_page,
)

ROOT = Path(__file__).resolve().parent
SKY_FILE = ROOT / "flight_data.json"
KAYAK_FILE = ROOT / "kayak_flight_data.json"
GOOGLE_FILE = ROOT / "google_flight_data.json"
AIRBNB_FILE = ROOT / "airbnb_lodging_data.json"
LOG_FILE = ROOT / "sync.log"

CHECKIN = build_html.CHECKIN
ADULTS = 2
CHILD_COUNT = 2


def now_kst_iso() -> str:
    return datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds")


def log(msg: str) -> None:
    line = f"[{now_kst_iso()}] {msg}"
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode("utf-8", errors="replace").decode("utf-8"))
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def load_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: list[dict[str, Any]]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def headless_mode() -> bool:
    if os.environ.get("SYNC_HEADLESS", "").lower() in ("1", "true", "yes"):
        return True
    return HEADLESS


def kayak_url(return_date: str) -> str:
    return (
        f"https://www.kayak.co.kr/flights/SEL-ORD/{OUTBOUND_DATE}/{return_date}/"
        f"{ADULTS}adults/children-7-8?sort=price_a"
    )


def google_url(return_date: str) -> str:
    query = (
        f"Seoul to Chicago O'Hare {OUTBOUND_DATE} return {return_date} "
        f"adults {ADULTS} children {CHILD_COUNT}"
    )
    return f"https://www.google.com/travel/flights/search?q={quote(query)}&hl=ko"


def lowest_won_price(text: str, *, min_price: int = 500_000) -> tuple[int | None, str]:
    matches = re.findall(r"₩[\d,]+", text)
    parsed: list[tuple[int, str]] = []
    for raw in matches:
        value = parse_price(raw)
        if value and value >= min_price:
            parsed.append((value, raw))
    if not parsed:
        return None, ""
    best = min(parsed, key=lambda item: item[0])
    return best


def scrape_kayak(page, return_date: str, previous: dict[str, Any] | None) -> dict[str, Any]:
    url = kayak_url(return_date)
    base = dict(previous or {})
    base.update(
        {
            "outbound_date": OUTBOUND_DATE,
            "return_date": return_date,
            "seller_url": url,
        }
    )
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(8000)
        price, price_text = lowest_won_price(page.inner_text("body"))
        if price:
            base["price"] = price
            base["price_text"] = price_text
            base["synced_at"] = now_kst_iso()
            log(f"  KAYAK {return_date}: {price_text}")
        else:
            log(f"  KAYAK {return_date}: 가격 파싱 실패 (기존 데이터 유지)")
    except Exception as exc:
        log(f"  KAYAK {return_date}: 오류 {exc}")
    return base


def scrape_google(page, return_date: str, previous: dict[str, Any] | None) -> dict[str, Any]:
    url = google_url(return_date)
    base = dict(previous or {})
    base.update(
        {
            "outbound_date": OUTBOUND_DATE,
            "return_date": return_date,
            "seller_url": url,
        }
    )
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(8000)
        price, price_text = lowest_won_price(page.inner_text("body"))
        if price:
            base["price"] = price
            base["price_text"] = price_text
            base["synced_at"] = now_kst_iso()
            log(f"  Google {return_date}: {price_text}")
        else:
            log(f"  Google {return_date}: 가격 파싱 실패 (기존 데이터 유지)")
    except Exception as exc:
        log(f"  Google {return_date}: 오류 {exc}")
    return base


def scrape_airbnb(page, entry: dict[str, Any]) -> dict[str, Any]:
    updated = dict(entry)
    url = entry.get("seller_url") or ""
    checkout = entry.get("checkout_date", "?")
    if not url:
        return updated
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(6000)
        price, price_text = lowest_won_price(page.inner_text("body"), min_price=100_000)
        if price:
            updated["price"] = price
            updated["price_text"] = price_text
            updated["synced_at"] = now_kst_iso()
            log(f"  Airbnb {checkout}: {price_text}")
        else:
            log(f"  Airbnb {checkout}: 가격 파싱 실패 (기존 데이터 유지)")
    except Exception as exc:
        log(f"  Airbnb {checkout}: 오류 {exc}")
    return updated


def deploy_to_github() -> None:
    git_dir = ROOT / ".git"
    if not git_dir.exists():
        return
    docs_index = ROOT / "docs" / "index.html"
    if not docs_index.exists():
        return
    try:
        subprocess.run(["git", "add", "docs/index.html"], cwd=ROOT, check=True, capture_output=True)
        diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT, capture_output=True)
        if diff.returncode == 0:
            log("GitHub Pages: 변경 없음")
            return
        subprocess.run(
            ["git", "commit", "-m", "Update travel comparison page"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
        push = subprocess.run(["git", "push"], cwd=ROOT, capture_output=True, text=True)
        if push.returncode == 0:
            log("GitHub Pages 배포 완료: https://adventistcho-art.github.io/chicago-trip/")
        else:
            log(f"GitHub push 실패: {push.stderr.strip()}")
    except Exception as exc:
        log(f"GitHub 배포 스킵: {exc}")


def run_sync() -> int:
    log("=== 동기화 시작 ===")
    errors: list[str] = []

    kayak_prev = {row["return_date"]: row for row in load_json_list(KAYAK_FILE)}
    google_prev = {row["return_date"]: row for row in load_json_list(GOOGLE_FILE)}
    airbnb_prev = load_json_list(AIRBNB_FILE)

    captured: list[dict[str, Any]] = []
    sky_offers: list[FlightOffer] = []
    kayak_rows: list[dict[str, Any]] = []
    google_rows: list[dict[str, Any]] = []
    airbnb_rows: list[dict[str, Any]] = []

    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                USER_DATA_DIR.as_posix(),
                headless=headless_mode(),
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

            log("[Skyscanner]")
            try:
                sky_offers = sync_skyscanner_on_page(page, captured, first_captcha=True)
            except Exception as exc:
                errors.append(f"Skyscanner: {exc}")
                log(f"Skyscanner 실패: {exc}")

            log("[KAYAK]")
            kayak_rows = [
                scrape_kayak(page, ret, kayak_prev.get(ret))
                for ret in RETURN_DATES
            ]

            log("[Google Flights]")
            google_rows = [
                scrape_google(page, ret, google_prev.get(ret))
                for ret in RETURN_DATES
            ]

            log("[Airbnb — 검색 최저가]")
            from airbnb_search import CHECKOUT_DATES as AIRBNB_CHECKOUTS, find_cheapest

            airbnb_rows = []
            for checkout in AIRBNB_CHECKOUTS:
                row = find_cheapest(page, CHECKIN, checkout)
                if row:
                    airbnb_rows.append(row)
                    log(f"  {checkout}: {row['price_text']} · {row['title'][:40]}")

            context.close()
    except Exception as exc:
        errors.append(str(exc))
        log(f"브라우저 세션 오류: {exc}\n{traceback.format_exc()}")

    if sky_offers:
        save_json(SKY_FILE, [asdict(o) for o in sky_offers])
        log(f"Skyscanner {len(sky_offers)}건 저장")
    elif SKY_FILE.exists():
        log("Skyscanner: 기존 flight_data.json 유지")

    if kayak_rows:
        save_json(KAYAK_FILE, kayak_rows)
    if google_rows:
        save_json(GOOGLE_FILE, google_rows)
    if airbnb_rows:
        save_json(AIRBNB_FILE, airbnb_rows)

    build_html.main()
    log("flights.html 재생성 완료")
    deploy_to_github()

    if errors:
        log("경고: " + "; ".join(errors))
        return 1

    log("=== 동기화 완료 ===")
    return 0


def main() -> int:
    return run_sync()


if __name__ == "__main__":
    raise SystemExit(main())
