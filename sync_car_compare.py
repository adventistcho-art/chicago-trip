#!/usr/bin/env python3
"""Compare ORD car rentals: DiscoverCars · Rentalcars.com · KAYAK (incl. EVs)."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote_plus

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUT_FILE = ROOT / "car_compare_data.json"
KAYAK_FILE = ROOT / "car_rental_data.json"
USER_DATA_DIR = ROOT / ".browser_profile_capture"

PICKUP = "2026-09-27"
DROPOFF_DATES = [
    "2026-10-08",
    "2026-10-09",
    "2026-10-10",
    "2026-10-11",
    "2026-10-12",
    "2026-10-13",
]
TOP_PER_SOURCE = 8
TOP_EV_PER_SOURCE = 10

# DiscoverCars Chicago O'Hare (ORD)
DC_COUNTRY_ID = "5003"
DC_CITY_ID = "4737"
DC_PLACE_ID = "4739"


def now_kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%dT%H:%M:%S+09:00")


def nights(a: str, b: str) -> int:
    return (datetime.strptime(b, "%Y-%m-%d") - datetime.strptime(a, "%Y-%m-%d")).days


def fmt_won(amount: int | None) -> str:
    if amount is None:
        return "-"
    return f"₩{amount:,}"


def kayak_url(drop: str, electric: bool = False) -> str:
    base = f"https://www.kayak.co.kr/cars/ORD/{PICKUP}/{drop}?sort=price_a"
    return base + "&fs=ecoclass=Electric" if electric else base


def discover_url(guid: str, sq: str) -> str:
    return f"https://www.discovercars.com/en/search/{guid}?sq={sq}&currency=KRW"


def rentalcars_url(drop: str) -> str:
    return (
        "https://www.rentalcars.com/SearchResults.do?"
        f"locationCode=ORD&driversAge=30&puDate={PICKUP.replace('-', '/')}&puTime=12:00"
        f"&doDate={drop.replace('-', '/')}&doTime=12:00&currency=KRW"
    )


def dismiss(page) -> None:
    page.evaluate(
        """() => {
      const b = [...document.querySelectorAll('button')].find(el =>
        /^(동의합니다|모두 동의|Accept all|Accept|Agree|Allow all|Got it)$/i.test((el.innerText || '').trim())
      );
      if (b) b.click();
    }"""
    )


def normalize_category(raw: str) -> str:
    t = (raw or "").strip().lower()
    mapping = [
        ("electric", "전기차"),
        ("economy", "이코노미"),
        ("compact", "컴팩트"),
        ("standard", "스탠다드"),
        ("intermediate", "중형"),
        ("full", "풀사이즈"),
        ("fullsize", "풀사이즈"),
        ("full_size", "풀사이즈"),
        ("suv", "SUV"),
        ("van", "밴"),
        ("minivan", "미니밴"),
        ("carrier", "밴"),
        ("premium", "프리미엄"),
        ("luxury", "럭셔리"),
        ("people", "밴"),
    ]
    for key, label in mapping:
        if key in t:
            return label
    return raw.strip() if raw else "기타"


def is_ev_car(c: dict) -> bool:
    if c.get("electric") or c.get("category") == "전기차":
        return True
    opts = " ".join(c.get("options") or [])
    return "Fully electric" in opts or "전기" in opts


def keep_gas_and_ev(cars: list[dict]) -> list[dict]:
    """Keep cheapest gas cars + EV cars (so EVs are not cut by price top-N)."""
    cars = sorted(cars, key=lambda c: c["price"])
    evs = [c for c in cars if is_ev_car(c)][:TOP_EV_PER_SOURCE]
    gas = [c for c in cars if not is_ev_car(c)][:TOP_PER_SOURCE]
    merged: list[dict] = []
    seen: set[tuple] = set()
    for c in evs + gas:
        key = (c["model"], c["category"], c["price"], c.get("source"))
        if key in seen:
            continue
        seen.add(key)
        merged.append(c)
    # Overall price order (cheapest[0] must be true site minimum, not EV-first)
    merged.sort(key=lambda c: c["price"])
    return merged


def offer_row(
    *,
    source: str,
    drop: str,
    model: str,
    category: str,
    price: int,
    seats=None,
    bags=None,
    doors=None,
    location: str = "ORD",
    options: list[str] | None = None,
    seller_url: str = "",
    supplier: str = "",
    electric: bool = False,
) -> dict:
    if electric and category != "전기차":
        category = "전기차"
    return {
        "id": f"car:{source}:{drop}:{category}:{model}:{price}",
        "source": source,
        "model": model,
        "category": category or "기타",
        "price": price,
        "price_text": fmt_won(price),
        "seats": seats,
        "bags": bags,
        "doors": doors,
        "location": location,
        "options": options or [],
        "supplier": supplier,
        "electric": electric or category == "전기차",
        "seller_url": seller_url,
        "synced_at": now_kst(),
    }


# ---------- DiscoverCars ----------
def discover_create(page, drop: str) -> tuple[str | None, str | None]:
    form = {
        "is_drop_off": "0",
        "pick_up_country_id": DC_COUNTRY_ID,
        "pick_up_city_id": DC_CITY_ID,
        "pick_up_location_id": DC_PLACE_ID,
        "drop_off_country_id": DC_COUNTRY_ID,
        "drop_off_city_id": DC_CITY_ID,
        "drop_off_location_id": DC_PLACE_ID,
        "pickup_id": DC_PLACE_ID,
        "dropoff_id": DC_PLACE_ID,
        "pickup_from": f"{PICKUP} 12:00",
        "pickup_to": f"{drop} 12:00",
        "pick_time": "12:00",
        "drop_time": "12:00",
        "partner_id": "0",
        "exclude_locations": "0",
        "luxOnly": "0",
        "driver_age": "30",
        "residence_country": "KR",
        "abtest": "",
        "token": "",
        "recent_search": "0",
    }
    resp = page.request.post(
        "https://www.discovercars.com/en/search/create-search",
        form=form,
        headers={"accept": "application/json", "x-requested-with": "XMLHttpRequest"},
    )
    if resp.status != 200:
        print("  DC create status", resp.status)
        return None, None
    data = resp.json()
    payload = data.get("data") or data
    return payload.get("guid"), payload.get("sq")


def scrape_discover(page, drop: str) -> list[dict]:
    print(f"\n=== DiscoverCars ORD {PICKUP} -> {drop} ===")
    page.goto("https://www.discovercars.com/", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(1500)
    dismiss(page)
    guid, sq = discover_create(page, drop)
    if not guid:
        return []
    api = f"https://www.discovercars.com/api/v2/search/{guid}?sq={sq}&searchVersion=2"
    offers = []
    for i in range(20):
        page.wait_for_timeout(1500 if i else 500)
        r = page.request.get(api, headers={"accept": "application/json"})
        if r.status != 200:
            continue
        try:
            data = r.json()
        except Exception:
            continue
        offers = (data.get("data") or {}).get("offers") or []
        if offers:
            break
    url = discover_url(guid, sq)
    cars: list[dict] = []
    for o in offers:
        price_obj = o.get("price") or {}
        raw = price_obj.get("raw")
        if raw is None:
            continue
        price = int(round(float(raw)))
        if price < 10_000:
            continue
        veh = o.get("vehicle") or {}
        spec = veh.get("specifications") or {}
        seats = (spec.get("seats") or {}).get("number")
        bags = (spec.get("bags") or {}).get("number")
        doors = (spec.get("doors") or {}).get("number")
        model = (veh.get("carName") or "차량").strip()
        category = normalize_category(veh.get("sippGroup") or "")
        supplier = ((o.get("supplier") or {}).get("name") or "").strip()
        opts: list[str] = []
        if o.get("isFreeCancellation"):
            opts.append("무료 취소")
        fuel = spec.get("fuelType")
        fuel_s = fuel if isinstance(fuel, str) else ""
        badges = o.get("badges") or {}
        electric = bool(badges.get("zero_emission")) or ("electric" in fuel_s.lower())
        if electric:
            category = "전기차"
            opts.append("Fully electric")
        book = o.get("bookUrl") or url
        if book.startswith("/"):
            book = "https://www.discovercars.com" + book
        cars.append(
            offer_row(
                source="discover",
                drop=drop,
                model=model,
                category=category,
                price=price,
                seats=seats,
                bags=bags,
                doors=doors,
                location="ORD · DiscoverCars",
                options=opts,
                seller_url=book,
                supplier=supplier,
                electric=electric,
            )
        )
    cars = keep_gas_and_ev(cars)
    print(f"  found {len(cars)} (ev={sum(1 for c in cars if c.get('electric'))})")
    for c in cars[:3]:
        print(f"  - {c.get('price'):,} KRW | {c['category']} | {c['model']}")
    return cars


# ---------- Rentalcars ----------
def scrape_rentalcars(page, drop: str) -> list[dict]:
    print(f"\n=== Rentalcars ORD {PICKUP} -> {drop} ===")
    page.goto(rentalcars_url(drop), wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4000)
    dismiss(page)
    search_criteria = {
        "driversAge": 30,
        "pickUpLocation": "ORD",
        "pickUpDateTime": f"{PICKUP}T12:00:00",
        "pickUpLocationType": "IATA",
        "dropOffLocation": "ORD",
        "dropOffLocationType": "IATA",
        "dropOffDateTime": f"{drop}T12:00:00",
        "searchMetadata": json.dumps(
            {"pickUpLocationName": "ORD Airport", "dropOffLocationName": "ORD Airport"}
        ),
    }
    filter_criteria = {"sortBy": "PRICE", "sortAscending": True}
    api_url = (
        "https://www.rentalcars.com/api/search-results?"
        f"searchCriteria={quote_plus(json.dumps(search_criteria))}&"
        f"filterCriteria={quote_plus(json.dumps(filter_criteria))}&"
        'serviceFeatures=["RETURN_EXTRAS_IN_MULTI_CAR_RESPONSE"]'
    )
    matches = []
    for _ in range(8):
        r = page.request.get(api_url, headers={"accept": "application/json"})
        if r.status == 200:
            try:
                matches = (r.json() or {}).get("matches") or []
            except Exception:
                matches = []
            if matches:
                break
        page.wait_for_timeout(2000)
    url = rentalcars_url(drop)
    cars: list[dict] = []
    for m in matches:
        veh = m.get("vehicle") or {}
        price_obj = veh.get("driveAwayPrice") or veh.get("price") or {}
        amount = price_obj.get("amount")
        if amount is None:
            continue
        price = int(round(float(amount)))
        if price < 10_000:
            continue
        model = (veh.get("makeAndModel") or "차량").strip()
        cats = veh.get("carCategories") or []
        category = normalize_category(cats[0] if cats else veh.get("carClass") or "")
        opts: list[str] = []
        if veh.get("freeCancellation"):
            opts.append("무료 취소")
        fuel = (veh.get("fuel") or "").lower()
        electric = fuel in ("electric", "ev") or "electric" in fuel
        if electric:
            category = "전기차"
            opts.append("Fully electric")
        cars.append(
            offer_row(
                source="rentalcars",
                drop=drop,
                model=model,
                category=category,
                price=price,
                seats=int(veh["numberOfSeats"]) if str(veh.get("numberOfSeats", "")).isdigit() else None,
                bags=veh.get("bigSuitcase"),
                doors=int(veh["numberOfDoors"]) if str(veh.get("numberOfDoors", "")).isdigit() else None,
                location="ORD · Rentalcars.com",
                options=opts,
                seller_url=url,
                electric=electric,
            )
        )
    cars = keep_gas_and_ev(cars)
    print(f"  found {len(cars)} (ev={sum(1 for c in cars if c.get('electric'))})")
    for c in cars[:3]:
        print(f"  - {c.get('price'):,} KRW | {c['category']} | {c['model']}")
    return cars


def load_kayak() -> dict[str, list[dict]]:
    """Load KAYAK cars including electric (not cut off by cheapest-only top-N)."""
    if not KAYAK_FILE.exists():
        return {}
    rows = json.loads(KAYAK_FILE.read_text(encoding="utf-8"))
    out: dict[str, list[dict]] = {}
    for day in rows:
        drop = day.get("dropoff_date")
        cars = []
        for c in day.get("cars") or []:
            if c.get("price") is None:
                continue
            electric = bool(c.get("electric") or c.get("category") == "전기차")
            opts = list(c.get("options") or [])
            if electric and not any("electric" in o.lower() or "전기" in o for o in opts):
                opts.insert(0, "Fully electric")
            cars.append(
                offer_row(
                    source="kayak",
                    drop=drop,
                    model=c.get("model") or "차량",
                    category=c.get("category") or "기타",
                    price=int(c["price"]),
                    seats=c.get("seats"),
                    bags=c.get("bags"),
                    doors=c.get("doors"),
                    location=c.get("location") or "ORD · KAYAK",
                    options=opts,
                    seller_url=c.get("seller_url") or kayak_url(drop, electric=electric),
                    electric=electric,
                )
            )
        out[drop] = keep_gas_and_ev(cars)
    return out


def main() -> int:
    kayak_by_drop = load_kayak()
    results: list[dict] = []

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            viewport={"width": 1400, "height": 900},
            locale="ko-KR",
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.pages[0] if context.pages else context.new_page()

        page.goto("https://www.discovercars.com/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2000)
        dismiss(page)

        for drop in DROPOFF_DATES:
            discover = scrape_discover(page, drop)
            rentalcars = scrape_rentalcars(page, drop)
            kayak = kayak_by_drop.get(drop) or []

            sources = {
                "discover": discover,
                "rentalcars": rentalcars,
                "kayak": kayak,
            }
            cheapest_by_source = {key: (cars[0] if cars else None) for key, cars in sources.items()}

            all_cars: list[dict] = []
            for key in ("discover", "rentalcars", "kayak"):
                all_cars.extend(sources[key])
            all_cars.sort(key=lambda c: (0 if c.get("electric") else 1, c["price"]))

            results.append(
                {
                    "pickup_date": PICKUP,
                    "dropoff_date": drop,
                    "pickup_location": "ORD",
                    "dropoff_location": "ORD",
                    "nights": nights(PICKUP, drop),
                    "sources": {
                        "discover": {
                            "label": "DiscoverCars",
                            "url": discover[0]["seller_url"]
                            if discover
                            else "https://www.discovercars.com/usa-illinois/chicago/ord",
                            "cars": discover,
                            "cheapest": cheapest_by_source["discover"],
                        },
                        "rentalcars": {
                            "label": "Rentalcars.com",
                            "url": rentalcars_url(drop),
                            "cars": rentalcars,
                            "cheapest": cheapest_by_source["rentalcars"],
                        },
                        "kayak": {
                            "label": "KAYAK",
                            "url": kayak_url(drop),
                            "cars": kayak,
                            "cheapest": cheapest_by_source["kayak"],
                        },
                    },
                    "cars": all_cars,
                    "synced_at": now_kst(),
                }
            )

        context.close()

    OUT_FILE.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT_FILE.name}")
    for day in results:
        bits = []
        for key, label in (("discover", "DC"), ("rentalcars", "RC"), ("kayak", "KY")):
            c = day["sources"][key].get("cheapest") or {}
            price = c.get("price")
            bits.append(f"{label}:{price:,}" if price else f"{label}:-")
        ev_n = sum(1 for c in day["cars"] if c.get("electric") or c.get("category") == "전기차")
        print(day["dropoff_date"], " | ".join(bits), f"| EV:{ev_n}")
    ok = any(
        (d["sources"]["discover"]["cars"] or d["sources"]["rentalcars"]["cars"] or d["sources"]["kayak"]["cars"])
        for d in results
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
