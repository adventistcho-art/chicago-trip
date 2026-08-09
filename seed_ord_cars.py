#!/usr/bin/env python3
"""Seed ORD local car_compare_data for pickup 2026-09-27 (until sync_car_compare finishes)."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "car_compare_data.json"
PICKUP = "2026-09-27"
DROPOFFS = [
    "2026-10-08",
    "2026-10-09",
    "2026-10-10",
    "2026-10-11",
    "2026-10-12",
    "2026-10-13",
]


def now_kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%dT%H:%M:%S+09:00")


def nights(a: str, b: str) -> int:
    return (datetime.strptime(b, "%Y-%m-%d") - datetime.strptime(a, "%Y-%m-%d")).days


def kayak_url(drop: str) -> str:
    return f"https://www.kayak.co.kr/cars/ORD/{PICKUP}/{drop}?sort=price_a"


def rentalcars_url(drop: str) -> str:
    return (
        "https://www.rentalcars.com/SearchResults.do?"
        f"locationCode=ORD&driversAge=30&puDate={PICKUP.replace('-', '/')}&puTime=14:00"
        f"&doDate={drop.replace('-', '/')}&doTime=10:00&currency=KRW"
    )


def main() -> None:
    # Indicative ORD local totals by length (sync will overwrite with live quotes)
    base_by_nights = {
        11: 720_000,
        12: 760_000,
        13: 800_000,
        14: 850_000,
        15: 900_000,
        16: 950_000,
    }
    results = []
    for drop in DROPOFFS:
        n = nights(PICKUP, drop)
        price = base_by_nights.get(n, 800_000 + max(0, n - 13) * 40_000)
        ky_url = kayak_url(drop)
        rc_url = rentalcars_url(drop)
        cheap = {
            "id": f"car:kayak:ORD:{drop}:중형:Toyota Corolla:{price}",
            "source": "kayak",
            "model": "Toyota Corolla 동급",
            "category": "중형",
            "price": price,
            "price_text": f"₩{price:,}",
            "seats": 5,
            "bags": 2,
            "doors": 4,
            "location": "ORD · 시카고 오헤어",
            "options": ["자동", "에어컨"],
            "electric": False,
            "pickup_code": "ORD",
            "dropoff_code": "ORD",
            "seller_url": ky_url,
            "synced_at": now_kst(),
            "estimate": True,
        }
        results.append(
            {
                "pickup_date": PICKUP,
                "dropoff_date": drop,
                "pickup_location": "ORD",
                "dropoff_location": "ORD",
                "pickup_time": "14:00",
                "dropoff_time": "10:00",
                "route_note": "시카고 ORD 공항 인수·반납 · 뉴욕 체류 중 렌트 없음",
                "nights": n,
                "sources": {
                    "discover": {
                        "label": "DiscoverCars",
                        "url": "https://www.discovercars.com/usa-illinois/chicago/ord",
                        "cars": [],
                        "cheapest": None,
                        "note": "sync_car_compare.py 실행 후 갱신",
                    },
                    "rentalcars": {
                        "label": "Rentalcars.com",
                        "url": rc_url,
                        "cars": [],
                        "cheapest": None,
                        "note": "사이트에서 확인",
                    },
                    "kayak": {
                        "label": "KAYAK",
                        "url": ky_url,
                        "cars": [cheap],
                        "cheapest": cheap,
                        "note": "시드 추정가 · sync로 교체 권장",
                    },
                },
                "cars": [cheap],
                "synced_at": now_kst(),
            }
        )
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} · {len(results)} drop-off days · pickup {PICKUP}")


if __name__ == "__main__":
    main()
