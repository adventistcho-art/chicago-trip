#!/usr/bin/env python3
"""Collect KAYAK Chicago ORD car rentals by drop-off date / car type / options."""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUT_FILE = ROOT / "car_rental_data.json"
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
TOP_PER_DATE = 16
CATEGORIES_PRIORITY = [
    "이코노미",
    "컴팩트",
    "중형",
    "스탠다드",
    "풀사이즈",
    "컴팩트 SUV",
    "중형 SUV",
    "풀사이즈 SUV",
    "미니밴",
    "밴",
]


def now_kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%dT%H:%M:%S+09:00")


def nights(a: str, b: str) -> int:
    return (datetime.strptime(b, "%Y-%m-%d") - datetime.strptime(a, "%Y-%m-%d")).days


def kayak_url(drop: str) -> str:
    return f"https://www.kayak.co.kr/cars/ORD/{PICKUP}/{drop}?sort=price_a"


def dismiss(page) -> None:
    page.evaluate(
        """() => {
      const b = [...document.querySelectorAll('button')].find(el =>
        /^(동의합니다|모두 동의|Accept all|Accept|Agree)$/i.test((el.innerText || '').trim())
      );
      if (b) b.click();
    }"""
    )


def parse_category(text: str) -> str:
    m = re.search(r"동급\s*\(([^)]+)\)|동급\s+([^\n]+)", text)
    if not m:
        return "기타"
    raw = (m.group(1) or m.group(2) or "").strip()
    return raw or "기타"


def extract_cars(page, drop: str) -> list[dict]:
    raw = page.evaluate(
        """() => {
      const text = document.body.innerText || '';
      const blocks = text.split('다음 검색 결과로 이동').slice(1);
      const out = [];
      for (const b of blocks) {
        if (b.includes('광고') && !/원/.test(b)) continue;
        const pm = b.match(/([\\d,]+)원/);
        if (!pm) continue;
        const lines = b.split('\\n').map(s => s.trim()).filter(Boolean);
        // skip promo blocks
        if (lines.some(l => /최대\\s*\\d+%\\s*할인|지금 바로 예약/.test(l)) && lines.length < 8) continue;
        const modelIdx = lines.findIndex(l =>
          /토요타|닛산|혼다|포드|쉐보레|지프|기아|현대|크라이슬러|닷지|폭스바겐|BMW|벤츠|아우디|테슬라|미쓰비시|스바루|마쓰다|링컨|캐딜락|람보르기니|볼보|타호|유콘|시에나|파일럿|오디세이|카니발|쏘렌토|싼타페|투싼|아반떼|쏘나타|캠리|코롤라|시빅|알티마|로그|야리스|베르사|스파크|크루즈|포커스|컴패스|익스플로러|이쿼녹스|말리부|엘란트라/i.test(l)
          || /또는 동급/.test(lines[lines.indexOf(l)+1] || '')
        );
        if (modelIdx < 0) continue;
        const model = lines[modelIdx];
        const gradeLine = lines[modelIdx + 1] || '';
        if (!/동급|이코노미|컴팩트|중형|스탠다드|풀사이즈|SUV|미니밴|밴/.test(gradeLine + b)) continue;
        const nums = [];
        for (let i = modelIdx + 2; i < Math.min(modelIdx + 8, lines.length); i++) {
          if (/^\\d+$/.test(lines[i])) nums.push(parseInt(lines[i], 10));
        }
        const loc = lines.find(l => /ORD|오헤어|공항|셔틀|터미널|시내/.test(l)) || '';
        const sites = (b.match(/(\\d+)개\\s*사이트/) || [])[1] || '';
        out.push({
          model,
          grade_line: gradeLine,
          nums,
          location: loc,
          sites: sites ? parseInt(sites, 10) : null,
          price: parseInt(pm[1].replace(/,/g, ''), 10),
          price_raw: pm[1] + '원',
          block: b.slice(0, 400),
        });
      }
      return out;
    }"""
    )
    cars: list[dict] = []
    seen: set[tuple] = set()
    for item in raw or []:
        category = parse_category(item.get("grade_line") or item.get("block") or "")
        model = (item.get("model") or "").strip()
        price = item.get("price")
        if not model or not price:
            continue
        key = (model, category, price, item.get("location") or "")
        if key in seen:
            continue
        seen.add(key)
        nums = item.get("nums") or []
        seats = nums[0] if len(nums) > 0 else None
        bags = nums[1] if len(nums) > 1 else None
        doors = nums[2] if len(nums) > 2 else None
        loc = item.get("location") or ""
        options = []
        if "터미널" in loc:
            options.append("공항 터미널 인수")
        if "셔틀" in loc:
            options.append("셔틀 이동")
        if item.get("sites"):
            options.append(f"비교 {item['sites']}개 사이트")
        if seats and seats >= 5:
            options.append("5인 이상")
        if bags and bags >= 3:
            options.append("짐칸 여유")

        cars.append(
            {
                "id": f"car:{drop}:{category}:{model}:{price}",
                "model": model,
                "category": category,
                "price": price,
                "price_text": f"₩{price:,}",
                "seats": seats,
                "bags": bags,
                "doors": doors,
                "location": loc,
                "options": options,
                "seller_url": kayak_url(drop),
                "synced_at": now_kst(),
            }
        )
    cars.sort(key=lambda c: c["price"])
    return cars[:TOP_PER_DATE]


def wait_cars(page, timeout_s: float = 55) -> list[dict]:
    deadline = time.time() + timeout_s
    best: list[dict] = []
    while time.time() < deadline:
        dismiss(page)
        body = page.inner_text("body")
        if "원" in body and ("동급" in body or "이코노미" in body):
            # allow a bit more load
            page.wait_for_timeout(1500)
            return extract_cars(page, "")  # drop filled by caller
        time.sleep(0.8)
    return best


def main() -> int:
    results: list[dict] = []
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            viewport={"width": 430, "height": 920},
            locale="ko-KR",
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.pages[0] if context.pages else context.new_page()

        for drop in DROPOFF_DATES:
            url = kayak_url(drop)
            print(f"\n=== cars ORD {PICKUP} -> {drop} ===")
            print(url)
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
            except PlaywrightTimeout:
                print("nav timeout")
            page.wait_for_timeout(2500)
            dismiss(page)

            deadline = time.time() + 55
            cars: list[dict] = []
            while time.time() < deadline:
                dismiss(page)
                body = page.inner_text("body")
                if "원" in body and "동급" in body:
                    page.wait_for_timeout(2000)
                    cars = extract_cars(page, drop)
                    if cars:
                        break
                time.sleep(0.8)

            # rewrite ids with drop
            for c in cars:
                c["id"] = f"car:{drop}:{c['category']}:{c['model']}:{c['price']}"
                c["seller_url"] = url

            print(f"  found {len(cars)}")
            for c in cars[:5]:
                print(f"  - {c['price_text']} | {c['category']} | {c['model']}")

            results.append(
                {
                    "pickup_date": PICKUP,
                    "dropoff_date": drop,
                    "pickup_location": "ORD",
                    "dropoff_location": "ORD",
                    "nights": nights(PICKUP, drop),
                    "cars": cars,
                    "synced_at": now_kst(),
                }
            )

        context.close()

    OUT_FILE.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT_FILE.name}")
    return 0 if any(d.get("cars") for d in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
