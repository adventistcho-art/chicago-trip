#!/usr/bin/env python3
"""Build tabbed travel page: budget dashboard + flights + lodging."""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

import itinerary_plans

ROOT = Path(__file__).resolve().parent
REFRESH_HOURS = 3
REFRESH_SECONDS = REFRESH_HOURS * 3600
HTML = ROOT / "flights.html"
INDEX_HTML = ROOT / "index.html"
DOCS_INDEX = ROOT / "docs" / "index.html"
SKY_FILE = ROOT / "flight_data.json"
KAYAK_FILE = ROOT / "kayak_flight_data.json"
GOOGLE_FILE = ROOT / "google_flight_data.json"
ROUTE_CHI_FILE = ROOT / "route_chi_roundtrip.json"
ROUTE_NYC_FILE = ROOT / "route_nyc_in_chi_out.json"
CAR_FILE = ROOT / "car_rental_data.json"
CAR_COMPARE_FILE = ROOT / "car_compare_data.json"
AIRBNB_LODGING = ROOT / "airbnb_lodging_data.json"
CAR_PICKUP = "2026-09-24"
CAR_SOURCE_META = {
    "discover": {"label": "DiscoverCars", "color": "#1f6feb", "css": "discover"},
    "rentalcars": {"label": "Rentalcars.com", "color": "#0d9488", "css": "rentalcars"},
    "kayak": {"label": "KAYAK", "color": "#ff690f", "css": "kayak"},
}

ADULTS = 2
CHILD_AGES = [7, 8]
OUTBOUND = "2026-09-24"
CHECKIN = "2026-09-26"
BOOKED_CHECKIN = "2026-09-27"
BOOKED_CHECKOUT = "2026-10-09"
LODGING_NOTE = "9/24 오전 출발 · 숙소 예약완료 9/27~10/9"
GUESTS = ADULTS + len(CHILD_AGES)

FLIGHT_KIND_META = {
    "cheapest": ("💰 최저가", "cheapest"),
    "shortest": ("⚡ 최단시간", "shortest"),
    "cheap17": ("⏱ 17h 이내", "cheap17"),
}
ROUTE_META = {
    "nyc_in": {
        "key": "nyc_in",
        "label": "뉴욕 인 · 시카고 아웃",
        "blurb": "서울 → 뉴욕 입국 · 시카고 → 서울 귀국",
        "chip": "NYC → ORD",
    },
    "chi_round": {
        "key": "chi_round",
        "label": "시카고 인 · 시카고 아웃",
        "blurb": "서울 ↔ 시카고(ORD) 왕복",
        "chip": "ORD 왕복",
    },
}

# Dashboard default estimates (KRW, editable in browser)
DEFAULT_FOOD_PER_DAY = 120_000
DEFAULT_CAR_RENTAL = 900_000
DEFAULT_GIFTS = 300_000
DEFAULT_MISC = 500_000

BTN = """
<a class="cta-link" href="{url}" target="_blank" rel="noopener noreferrer">
  <button type="button" class="cta-btn">선택하기</button>
</a>"""


def fmt_won(amount: int | None) -> str:
    if amount is None:
        return "-"
    return f"₩{amount:,}"


def flight_per_person(total: int | None) -> int | None:
    if total is None:
        return None
    return round(total / GUESTS)


def flight_per_person_text(total: int | None) -> str:
    return fmt_won(flight_per_person(total))


def load_route_rows(path: Path) -> list[dict]:
    return load_list(path)


def flatten_route_flights(route_rows: list[dict]) -> list[dict]:
    """Turn route JSON into selectable flight options for the dashboard."""
    out: list[dict] = []
    for day in route_rows:
        ret = day["return_date"]
        route = day.get("route", "")
        route_label = day.get("route_label") or ROUTE_META.get(route, {}).get("label", route)
        for kind in ("cheapest", "shortest"):
            opt = day.get(kind)
            if not opt or opt.get("price") is None:
                continue
            kind_label = FLIGHT_KIND_META[kind][0].split(" ", 1)[-1]
            if kind == "cheapest":
                kind_label = "최저가"
            elif kind == "shortest":
                kind_label = "최단시간"
            out.append(
                {
                    "id": f"{route}:{kind}:{ret}",
                    "source": route,
                    "source_label": f"{route_label} · {kind_label}",
                    "route": route,
                    "route_label": route_label,
                    "kind": kind,
                    "kind_label": kind_label,
                    "return_date": ret,
                    "price": opt["price"],
                    "price_text": opt.get("price_text", fmt_won(opt["price"])),
                    "price_per_person": opt.get("price_per_person") or flight_per_person(opt["price"]),
                    "price_per_person_text": opt.get("price_per_person_text")
                    or flight_per_person_text(opt["price"]),
                    "duration_text": opt.get("duration_text", ""),
                    "duration_minutes": opt.get("duration_minutes"),
                    "stops_text": opt.get("stops_text", ""),
                    "carrier_text": opt.get("carrier_text", ""),
                    "self_transfer": opt.get("self_transfer", False),
                    "seller_url": opt.get("seller_url", ""),
                }
            )
        for i, opt in enumerate(day.get("cheap_under_17h") or []):
            if not opt or opt.get("price") is None:
                continue
            out.append(
                {
                    "id": f"{route}:cheap17:{ret}:{i}",
                    "source": route,
                    "source_label": f"{route_label} · 17h 이내",
                    "route": route,
                    "route_label": route_label,
                    "kind": "cheap17",
                    "kind_label": "17h 이내",
                    "return_date": ret,
                    "price": opt["price"],
                    "price_text": opt.get("price_text", fmt_won(opt["price"])),
                    "price_per_person": opt.get("price_per_person") or flight_per_person(opt["price"]),
                    "price_per_person_text": opt.get("price_per_person_text")
                    or flight_per_person_text(opt["price"]),
                    "duration_text": opt.get("duration_text", ""),
                    "duration_minutes": opt.get("duration_minutes"),
                    "stops_text": opt.get("stops_text", ""),
                    "carrier_text": opt.get("carrier_text", ""),
                    "self_transfer": opt.get("self_transfer", False),
                    "seller_url": opt.get("seller_url", ""),
                }
            )
    out.sort(key=lambda x: (x["price"], x.get("duration_minutes") or 10**9))
    return out


def best_flight_for_date(flights: list[dict], ret: str, kind: str = "cheapest") -> dict | None:
    candidates = [f for f in flights if f["return_date"] == ret and f.get("kind") == kind]
    if not candidates:
        candidates = [f for f in flights if f["return_date"] == ret]
    if not candidates:
        return None
    if kind == "shortest":
        return min(candidates, key=lambda x: x.get("duration_minutes") or 10**9)
    return min(candidates, key=lambda x: x["price"])


def analyze_combos(flights: list[dict], airbnb: dict) -> list[dict]:
    dates = sorted({f["return_date"] for f in flights} | set(airbnb))
    combos: list[dict] = []
    for ret in dates:
        flight = best_flight_for_date(flights, ret, "cheapest")
        lodging = airbnb.get(ret)
        if not flight or not lodging or lodging.get("price") is None:
            continue
        combos.append(
            {
                "return_date": ret,
                "flight_id": flight["id"],
                "flight_source": flight["source_label"],
                "flight_price": flight["price"],
                "flight_per_person_text": flight["price_per_person_text"],
                "flight_carrier": flight.get("carrier_text", ""),
                "lodging_id": lodging_id(lodging),
                "lodging_checkout": lodging["checkout_date"],
                "lodging_price": lodging["price"],
                "lodging_price_text": lodging.get("price_text", fmt_won(lodging["price"])),
                "lodging_nights": lodging.get("nights", 0),
                "lodging_title": lodging.get("title", ""),
                "combined": flight["price"] + lodging["price"],
            }
        )
    combos.sort(key=lambda x: x["combined"])
    return combos


def load_list(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def load_flights(path: Path) -> dict[str, dict]:
    return {row["return_date"]: row for row in load_list(path)}


def lodging_id(row: dict) -> str:
    return f"{row['checkout_date']}|{row.get('room_id', row.get('seller_url', ''))}"


def load_lodging_list(path: Path) -> list[dict]:
    return load_list(path)


def load_lodging_cheapest(rows: list[dict]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for row in rows:
        co = row["checkout_date"]
        if co not in out or row.get("price", 10**12) < out[co].get("price", 10**12):
            out[co] = row
    return out


def min_price(*prices: int | None) -> int | None:
    valid = [p for p in prices if p is not None]
    return min(valid) if valid else None


def winner_label(prices: dict[str, int | None], labels: dict[str, str]) -> str:
    valid = {k: v for k, v in prices.items() if v is not None}
    if not valid:
        return "-"
    best = min(valid.values())
    winners = [labels[k] for k, v in valid.items() if v == best]
    return " · ".join(winners)


def price_cls(price: int | None, cheapest: int | None) -> str:
    return " highlight" if price == cheapest and price is not None else ""


def flight_pick_cell(source: str, ret: str, row: dict | None, cheapest: int | None) -> str:
    if not row or row.get("price") is None:
        return "<td>-</td><td>-</td><td>-</td><td>-</td>"
    pid = f"{source}:{ret}"
    cls = price_cls(row.get("price"), cheapest)
    return f"""
          <td class="price {source}{cls}">
            <label class="pick-label">
              <input type="radio" name="flight-pick" class="flight-pick" value="{pid}"
                data-price="{row['price']}" data-return="{ret}" data-source="{source}">
              <span>{flight_per_person_text(row['price'])}</span>
            </label>
          </td>
          <td>{row.get('duration_text', '-')}</td>
          <td>{row.get('carrier_text', '-')}</td>
          <td>{BTN.format(url=row['seller_url'])}</td>"""


def lodging_pick_cell(a: dict, is_best: bool) -> str:
    lid = lodging_id(a)
    label = "예약" if a.get("booked") else ("★" if is_best else "선택")
    checked = " checked" if a.get("booked") else ""
    return f"""
          <td>
            <label class="pick-label lodging-pick-label">
              <input type="radio" name="lodging-pick" class="lodging-pick" value="{lid}"
                data-checkout="{a['checkout_date']}"
                data-price="{a.get('price', 0)}" data-nights="{a.get('nights', 0)}"{checked}>
              <span>{label}</span>
            </label>
          </td>"""


def flatten_cars(car_days: list[dict]) -> list[dict]:
    out: list[dict] = []
    seen: set[str] = set()
    for day in car_days:
        drop = day.get("dropoff_date", "")
        for car in day.get("cars") or []:
            cid = car.get("id") or f"car:{drop}:{car.get('model')}:{car.get('price')}"
            if cid in seen:
                continue
            seen.add(cid)
            source = car.get("source") or "kayak"
            source_label = CAR_SOURCE_META.get(source, {}).get("label", source)
            out.append(
                {
                    "id": cid,
                    "source": source,
                    "source_label": source_label,
                    "pickup_date": day.get("pickup_date", CAR_PICKUP),
                    "dropoff_date": drop,
                    "nights": day.get("nights", 0),
                    "model": car.get("model", ""),
                    "category": car.get("category", "기타"),
                    "price": car.get("price"),
                    "price_text": car.get("price_text", fmt_won(car.get("price"))),
                    "seats": car.get("seats"),
                    "bags": car.get("bags"),
                    "doors": car.get("doors"),
                    "location": car.get("location", ""),
                    "options": car.get("options") or [],
                    "seller_url": car.get("seller_url", ""),
                }
            )
    out.sort(key=lambda x: (x.get("price") or 10**12, x.get("dropoff_date", "")))
    return out


def build_trip_data(
    route_flights: list[dict],
    airbnb_all: list[dict],
    airbnb: dict[str, dict],
    car_days: list[dict] | None = None,
) -> dict:
    flights = list(route_flights)
    cars = flatten_cars(car_days or [])

    lodging = []
    booked_row_raw = next((a for a in airbnb_all if a.get("booked")), None)
    for a in sorted(
        airbnb_all,
        key=lambda x: (0 if x.get("booked") else 1, x.get("checkout_date", ""), x.get("price") or 10**12),
    ):
        lodging.append(
            {
                "id": lodging_id(a),
                "checkin_date": a.get("checkin") or CHECKIN,
                "checkout_date": a["checkout_date"],
                "nights": a.get("nights", 0),
                "price": a.get("price"),
                "price_text": a.get("price_text", ""),
                "title": a.get("title", ""),
                "distance_text": a.get("distance_text", ""),
                "seller_url": a.get("seller_url", ""),
                "booked": bool(a.get("booked")),
                "reservation_code": a.get("reservation_code", ""),
                "host": a.get("host", ""),
                "address": a.get("address", ""),
            }
        )

    best_flight = flights[0] if flights else None
    cheapest_rows = sorted(airbnb.values(), key=lambda x: x.get("price") or 10**12)
    best_lodging = lodging[0] if lodging else None
    for row in lodging:
        if cheapest_rows and row["id"] == lodging_id(cheapest_rows[0]):
            best_lodging = row
            break
    booked_lodging = next((l for l in lodging if l.get("booked")), None)
    if booked_lodging:
        best_lodging = booked_lodging
    combos = analyze_combos(flights, airbnb)
    recommended = combos[0] if combos else None
    if booked_lodging:
        best_lodging_id = booked_lodging["id"]
        best_flight_id = recommended["flight_id"] if recommended else (best_flight["id"] if best_flight else None)
        if best_flight and booked_lodging["checkout_date"]:
            matched_flight = next(
                (
                    f
                    for f in flights
                    if f["return_date"] == booked_lodging["checkout_date"] and f.get("kind") == "cheapest"
                ),
                None,
            )
            if matched_flight:
                best_flight_id = matched_flight["id"]
    elif recommended:
        best_flight_id = recommended["flight_id"]
        best_lodging_id = recommended.get("lodging_id") or recommended["lodging_checkout"]
    else:
        best_flight_id = best_flight["id"] if best_flight else None
        best_lodging_id = best_lodging["id"] if best_lodging else None
        if best_flight and best_lodging:
            matched = next((l for l in lodging if l["checkout_date"] == best_flight["return_date"]), None)
            if matched:
                best_lodging_id = matched["id"]

    best_car_id = None
    if cars and recommended:
        same_day = [c for c in cars if c["dropoff_date"] == recommended["return_date"]]
        pool = same_day or cars
        best_car_id = min(pool, key=lambda x: x.get("price") or 10**12)["id"]
    elif cars:
        best_car_id = cars[0]["id"]

    return_dates = sorted({f["return_date"] for f in flights})
    checkout_dates = sorted({l["checkout_date"] for l in lodging})
    dropoff_dates = sorted({c["dropoff_date"] for c in cars}) or return_dates
    checkin_dates = sorted({l.get("checkin_date") or CHECKIN for l in lodging}) or [CHECKIN]
    outbound_dates = sorted({OUTBOUND})
    pickup_dates = sorted({c.get("pickup_date") or CAR_PICKUP for c in cars}) or [CAR_PICKUP]

    return {
        "outbound": OUTBOUND,
        "checkin": (booked_row_raw or {}).get("checkin") or CHECKIN,
        "lodging_note": LODGING_NOTE,
        "booked_lodging_id": booked_lodging["id"] if booked_lodging else None,
        "guests": GUESTS,
        "adults": ADULTS,
        "child_ages": CHILD_AGES,
        "car_pickup": CAR_PICKUP,
        "date_options": {
            "outbound": outbound_dates,
            "return": return_dates,
            "checkin": checkin_dates,
            "checkout": checkout_dates,
            "pickup": pickup_dates,
            "dropoff": dropoff_dates,
        },
        "defaults": {
            "food_per_day": DEFAULT_FOOD_PER_DAY,
            "car_rental": DEFAULT_CAR_RENTAL,
            "gifts": DEFAULT_GIFTS,
            "misc": DEFAULT_MISC,
        },
        "flights": flights,
        "lodging": lodging,
        "cars": cars,
        "combos": combos,
        "recommended": recommended,
        "best_flight_id": best_flight_id,
        "best_lodging_id": best_lodging_id,
        "best_lodging_checkout": best_lodging_id,
        "best_car_id": best_car_id,
    }


def _date_options_html(dates: list[str], selected: str | None = None) -> str:
    if not dates:
        return ""
    sel = selected if selected in dates else dates[0]
    parts = []
    for d in dates:
        parts.append(
            f'<option value="{d}"{" selected" if d == sel else ""}>{_fmt_date_ko(d)} ({d})</option>'
        )
    return "".join(parts)


def render_date_filter(
    *,
    prefix: str,
    start_id: str,
    end_id: str,
    start_label: str,
    end_label: str,
    start_dates: list[str],
    end_dates: list[str],
    start_selected: str | None = None,
    end_selected: str | None = None,
    note: str = "",
) -> str:
    guests_note = (
        f"성인 {ADULTS}명 · 아동 {len(CHILD_AGES)}명 "
        f"(만 {CHILD_AGES[0]}·{CHILD_AGES[1]}세) · 인원 고정"
    )
    return f"""
    <section class="date-filter card" data-date-filter="{prefix}">
      <div class="date-filter-head">
        <div>
          <p class="date-kicker">DATE FILTER</p>
          <h3 class="date-filter-title">날짜 선택</h3>
        </div>
        <p class="date-filter-guests">{guests_note}</p>
      </div>
      <div class="date-filter-grid">
        <label class="date-field">
          <span class="field-label">{start_label}</span>
          <select id="{start_id}" class="date-select" data-date-role="start">
            {_date_options_html(start_dates, start_selected)}
          </select>
        </label>
        <label class="date-field">
          <span class="field-label">{end_label}</span>
          <select id="{end_id}" class="date-select" data-date-role="end">
            {_date_options_html(end_dates, end_selected)}
          </select>
        </label>
      </div>
      <p class="muted date-filter-note">{note or "선택한 날짜에 맞는 결과만 아래에 표시됩니다."}</p>
    </section>"""


def _fmt_date_ko(iso: str) -> str:
    _y, m, d = iso.split("-")
    return f"{int(m)}월 {int(d)}일"


def _opt_card(flight_id: str, opt: dict | None, kind: str, route: str, ret: str) -> str:
    badge_text, css_kind = FLIGHT_KIND_META.get(kind, (kind, kind))
    if not opt:
        return f"""
        <article class="opt-card opt-{css_kind} is-empty">
          <header class="opt-head"><span class="opt-badge">{badge_text}</span></header>
          <p class="muted">데이터 없음</p>
        </article>"""
    note = '<span class="pill warn">자가환승</span>' if opt.get("self_transfer") else ""
    return f"""
    <article class="opt-card opt-{css_kind}">
      <header class="opt-head">
        <span class="opt-badge">{badge_text}</span>
        {note}
      </header>
      <p class="opt-price">{opt.get('price_per_person_text') or flight_per_person_text(opt.get('price'))}</p>
      <p class="opt-sub">1인 · 4명 합계 {opt.get('price_text') or fmt_won(opt.get('price'))}</p>
      <dl class="opt-meta">
        <div><dt>비행</dt><dd>{opt.get('duration_text') or '-'}</dd></div>
        <div><dt>경유</dt><dd>{opt.get('stops_text') or '-'}</dd></div>
        <div><dt>항공사</dt><dd>{opt.get('carrier_text') or '-'}</dd></div>
      </dl>
      <div class="opt-actions">
        <label class="pick-label">
          <input type="radio" name="flight-pick" class="flight-pick" value="{flight_id}"
            data-price="{opt['price']}" data-return="{ret}" data-source="{route}">
          <span>경비에 담기</span>
        </label>
        {BTN.format(url=opt.get('seller_url', '#'))}
      </div>
    </article>"""


def _route_panel(route_key: str, days: list[dict], active: bool) -> str:
    meta = ROUTE_META[route_key]
    cheap_opts = [d["cheapest"] for d in days if d.get("cheapest")]
    short_opts = [d["shortest"] for d in days if d.get("shortest")]
    best_cheap = min(cheap_opts, key=lambda x: x["price"]) if cheap_opts else None
    best_short = min(short_opts, key=lambda x: x.get("duration_minutes") or 10**9) if short_opts else None

    hero_bits = []
    if best_cheap:
        hero_bits.append(
            f'<div class="route-stat"><span class="muted">루트 최저가</span>'
            f'<strong>{best_cheap["price_per_person_text"]}</strong>'
            f'<span class="muted">{best_cheap.get("carrier_text","")}</span></div>'
        )
    if best_short:
        hero_bits.append(
            f'<div class="route-stat"><span class="muted">루트 최단</span>'
            f'<strong>{best_short.get("duration_text","")}</strong>'
            f'<span class="muted">{best_short.get("price_per_person_text","")}</span></div>'
        )

    day_cards = []
    for day in days:
        ret = day["return_date"]
        cheap = day.get("cheapest")
        short = day.get("shortest")
        under_17 = day.get("cheap_under_17h") or []
        extra_block = ""
        if under_17:
            extra_cards = "".join(
                _opt_card(f"{route_key}:cheap17:{ret}:{i}", opt, "cheap17", route_key, ret)
                for i, opt in enumerate(under_17)
            )
            extra_block = f"""
          <div class="opt-extra">
            <p class="opt-extra-title">최저가 중 편도 17시간 이내 · {len(under_17)}개</p>
            <div class="opt-grid opt-grid-extra">{extra_cards}</div>
          </div>"""
        day_cards.append(f"""
        <section class="date-card" data-return="{ret}">
          <div class="date-card-head">
            <div>
              <p class="date-kicker">귀국일</p>
              <h3>{_fmt_date_ko(ret)}</h3>
              <p class="muted">출국 {_fmt_date_ko(OUTBOUND)}</p>
            </div>
            <span class="date-chip">{meta['chip']}</span>
          </div>
          <div class="opt-grid">
            {_opt_card(f"{route_key}:cheapest:{ret}", cheap, "cheapest", route_key, ret)}
            {_opt_card(f"{route_key}:shortest:{ret}", short, "shortest", route_key, ret)}
          </div>
          {extra_block}
        </section>""")

    return f"""
    <div class="route-panel {'active' if active else ''}" data-route-panel="{route_key}" role="tabpanel">
      <section class="route-hero card">
        <div class="route-hero-copy">
          <p class="route-kicker">{meta['chip']}</p>
          <h2>{meta['label']}</h2>
          <p class="muted">{meta['blurb']} · KAYAK 1인 기준 · 최저가 / 최단시간 / 17h 이내 5개</p>
        </div>
        <div class="route-stats">{''.join(hero_bits)}</div>
      </section>
      <div class="date-stack">{''.join(day_cards)}</div>
    </div>"""


def render_flights(chi_days: list[dict], nyc_days: list[dict]) -> str:
    returns = sorted(
        {d["return_date"] for d in chi_days + nyc_days}
        or {"2026-10-08", "2026-10-09", "2026-10-10", "2026-10-11", "2026-10-12", "2026-10-13"}
    )
    date_bar = render_date_filter(
        prefix="flights",
        start_id="flight-outbound",
        end_id="flight-return",
        start_label="출국일",
        end_label="귀국일",
        start_dates=[OUTBOUND],
        end_dates=returns,
        start_selected=OUTBOUND,
        end_selected=returns[0] if returns else None,
        note="출국·귀국일을 고르면 해당 일정의 최저가 / 최단시간만 표시됩니다.",
    )
    return f"""
    {date_bar}
    <div class="route-switch" role="tablist" aria-label="항공 루트">
      <button type="button" class="route-tab active" role="tab" aria-selected="true" data-route="nyc_in">
        <span class="route-tab-title">뉴욕 인 · 시카고 아웃</span>
        <span class="route-tab-sub">SEL→NYC / ORD→SEL</span>
      </button>
      <button type="button" class="route-tab" role="tab" aria-selected="false" data-route="chi_round">
        <span class="route-tab-title">시카고 인 · 시카고 아웃</span>
        <span class="route-tab-sub">SEL↔ORD 왕복</span>
      </button>
    </div>
    <p class="flight-hint muted">선택한 귀국일의 <strong>최저가</strong>·<strong>최단시간</strong>과, 최저가 순 <strong>17시간 이내</strong> 후보 5개를 표시합니다. ○ 경비에 담기 → 여행경비 탭에 반영됩니다.</p>
    <p id="flight-empty" class="empty-filter muted" hidden>선택한 날짜의 항공 데이터가 없습니다.</p>
    {_route_panel("nyc_in", nyc_days, True)}
    {_route_panel("chi_round", chi_days, False)}
    """


def _dedupe_cars(cars: list[dict]) -> list[dict]:
    seen: set[tuple] = set()
    out: list[dict] = []
    for c in cars:
        key = (c.get("model"), c.get("category"), c.get("price"), c.get("location"))
        if key in seen:
            continue
        seen.add(key)
        out.append(c)
    return out


def _car_source_cell(
    src: dict | None, drop: str, source_key: str, day_best_price: int | None = None
) -> str:
    meta = CAR_SOURCE_META.get(source_key, {"label": source_key, "css": source_key})
    css = meta.get("css", source_key)
    if not src:
        return f'<td class="price {css}"><span class="muted">-</span></td>'
    cheap = src.get("cheapest")
    url = src.get("url") or "#"
    note = src.get("note")
    if not cheap:
        link = BTN.format(url=url).replace("선택하기", "사이트에서 보기")
        tip = f'<br><span class="muted">{note}</span>' if note else ""
        return (
            f'<td class="price {css}"><span class="muted">수집 불가</span>{tip}'
            f'<div style="margin-top:8px">{link}</div></td>'
        )
    cls = price_cls(cheap.get("price"), day_best_price)
    best_cls = " best-src" if day_best_price is not None and cheap.get("price") == day_best_price else ""
    return f"""
    <td class="price {css}{cls}{best_cls}">
      <label class="pick-label" style="flex-direction:column;align-items:flex-start;gap:4px;">
        <span style="display:inline-flex;align-items:center;gap:6px;">
          <input type="radio" name="car-pick" class="car-pick" value="{cheap['id']}"
            data-price="{cheap.get('price') or 0}" data-dropoff="{drop}">
          <strong>{cheap.get('price_text') or fmt_won(cheap.get('price'))}</strong>
        </span>
        <span class="muted">{cheap.get('category','')} · {cheap.get('model','')}</span>
      </label>
      <div style="margin-top:8px;">{BTN.format(url=cheap.get('seller_url') or url)}</div>
    </td>"""


def render_cars(car_days: list[dict]) -> str:
    if not car_days:
        return (
            '<section class="card"><p class="muted">'
            "렌트카 데이터가 없습니다. sync_car_compare.py 또는 sync_cars.py를 실행하세요."
            "</p></section>"
        )

    compare_mode = any(day.get("sources") for day in car_days)
    all_cars = []
    for day in car_days:
        all_cars.extend(day.get("cars") or [])
        if day.get("sources"):
            for src in day["sources"].values():
                if src.get("cheapest"):
                    all_cars.append(src["cheapest"])
    cheapest = min((c for c in all_cars if c.get("price")), key=lambda x: x["price"], default=None)

    source_keys = ["discover", "rentalcars", "kayak"]

    date_tabs = []
    panels = []
    compare_rows = []

    for i, day in enumerate(car_days):
        drop = day["dropoff_date"]
        active = "active" if i == 0 else ""
        sources = day.get("sources") or {}
        cars = _dedupe_cars(day.get("cars") or [])
        cars.sort(key=lambda x: (x.get("price") or 10**12))

        day_best = None
        if sources:
            cands = [sources[k]["cheapest"] for k in source_keys if sources.get(k, {}).get("cheapest")]
            day_best = min(cands, key=lambda x: x["price"]) if cands else None
        elif cars:
            day_best = cars[0]

        date_tabs.append(
            f'<button type="button" class="car-date-tab {active}" data-car-date="{drop}" role="tab" aria-selected="{"true" if i == 0 else "false"}">'
            f'<span class="car-date-main">{_fmt_date_ko(drop)} 반납</span>'
            f'<span class="car-date-sub">{day.get("nights", 0)}일 · 최저 '
            f'{fmt_won(day_best["price"]) if day_best else "-"}</span></button>'
        )

        if compare_mode and sources:
            best_price = day_best.get("price") if day_best else None
            cells = [_car_source_cell(sources.get(key), drop, key, best_price) for key in source_keys]
            winner = ""
            if day_best:
                lab = CAR_SOURCE_META.get(day_best.get("source", ""), {}).get(
                    "label", day_best.get("source", "")
                )
                winner = f'{lab} {day_best.get("price_text")}'
            compare_rows.append(
                f'<tr class="{"best" if i == 0 else ""}" data-dropoff="{drop}">'
                f"<td><strong>{_fmt_date_ko(drop)}</strong><br>"
                f'<span class="muted">{day.get("nights", 0)}일 · 최저 {winner or "-"}</span></td>'
                f'{"".join(cells)}</tr>'
            )

        by_cat: dict[str, list[dict]] = {}
        for c in cars:
            by_cat.setdefault(c.get("category") or "기타", []).append(c)

        cat_order = sorted(
            by_cat.keys(),
            key=lambda k: (0 if k == "전기차" else 1, min(c.get("price") or 10**12 for c in by_cat[k])),
        )
        cat_blocks = []
        for cat in cat_order:
            rows = by_cat[cat]
            cards = []
            for c in rows:
                src = c.get("source") or "kayak"
                src_label = CAR_SOURCE_META.get(src, {}).get("label", src)
                opts = "".join(
                    f'<span class="car-pill{" ev" if ("electric" in o.lower() or "전기" in o or o.startswith("Fully")) else ""}">{o}</span>'
                    for o in (c.get("options") or [])
                )
                specs = " · ".join(
                    x
                    for x in [
                        f"좌석 {c['seats']}" if c.get("seats") else "",
                        f"짐 {c['bags']}" if c.get("bags") is not None else "",
                        f"도어 {c['doors']}" if c.get("doors") else "",
                    ]
                    if x
                )
                cards.append(f"""
                <article class="car-card">
                  <div class="car-card-top">
                    <div>
                      <p class="car-cat"><span class="car-src-tag {src}">{src_label}</span> {cat}</p>
                      <h3 class="car-model">{c.get('model','')}</h3>
                      <p class="muted">{specs or '스펙 정보 없음'}</p>
                    </div>
                    <p class="car-price">{c.get('price_text') or fmt_won(c.get('price'))}</p>
                  </div>
                  <p class="car-loc muted">{c.get('location') or 'ORD'}</p>
                  <div class="car-pills">{opts or '<span class="muted">추가 옵션 정보 없음</span>'}</div>
                  <div class="opt-actions">
                    <label class="pick-label">
                      <input type="radio" name="car-pick" class="car-pick" value="{c['id']}"
                        data-price="{c.get('price') or 0}" data-dropoff="{drop}">
                      <span>경비에 담기</span>
                    </label>
                    {BTN.format(url=c.get('seller_url', '#'))}
                  </div>
                </article>""")
            cat_blocks.append(
                f'<div class="car-cat-block" data-cat="{cat}"><h3 class="car-cat-title">{cat}</h3>'
                f'<div class="car-grid">{"".join(cards)}</div></div>'
            )

        panels.append(f"""
        <div class="car-date-panel {active}" data-car-panel="{drop}">
          <p class="muted" style="margin:0 0 12px;">인수 {_fmt_date_ko(day.get('pickup_date', CAR_PICKUP))} 정오 · 반납 {_fmt_date_ko(drop)} 정오 · ORD</p>
          {''.join(cat_blocks) if cat_blocks else '<p class="muted">상세 목록 없음 · 위 사이트별 최저가를 확인하세요.</p>'}
        </div>""")

    hero = ""
    if cheapest:
        src_label = CAR_SOURCE_META.get(cheapest.get("source", ""), {}).get(
            "label", cheapest.get("source") or ""
        )
        hero = f"""
        <section class="route-hero card car-hero" id="car-hero"
          data-price-text="{cheapest.get('price_text') or ''}"
          data-meta="{src_label} · {cheapest.get('category') or ''} · {cheapest.get('model') or ''}">
          <div class="route-hero-copy">
            <p class="route-kicker">ORD RENTAL COMPARE</p>
            <h2>렌트카 · 사이트 비교</h2>
            <p class="muted" id="car-hero-blurb">DiscoverCars · Rentalcars.com · KAYAK · 전기차 포함 · 인수 {CAR_PICKUP}</p>
          </div>
          <div class="route-stats">
            <div class="route-stat">
              <span class="muted" id="car-hero-label">선택일 최저가</span>
              <strong id="car-hero-price">{cheapest.get('price_text')}</strong>
              <span class="muted" id="car-hero-meta">{src_label} · {cheapest.get('category')} · {cheapest.get('model')}</span>
            </div>
          </div>
        </section>"""

    legend = "".join(
        f'<span><i class="dot" style="background:{CAR_SOURCE_META[k]["color"]}"></i> {CAR_SOURCE_META[k]["label"]}</span>'
        for k in source_keys
        if k in CAR_SOURCE_META
    )

    compare_table = ""
    if compare_rows:
        heads = "".join(
            f'<th class="{CAR_SOURCE_META[k]["css"]}">{CAR_SOURCE_META[k]["label"]}</th>' for k in source_keys
        )
        compare_table = f"""
        <section class="card" id="car-compare-card">
          <div class="legend">{legend}</div>
          <p class="muted" style="margin:0 0 12px;" id="car-compare-hint">반납일을 고르면 해당일 사이트 최저가만 표시됩니다. ○ 선택 → 여행경비 반영 · 아래 목록에 전기차(EV)도 포함됩니다.</p>
          <div class="table-wrap">
          <table class="car-compare-table">
            <thead>
              <tr>
                <th>반납일</th>
                {heads}
              </tr>
            </thead>
            <tbody>{''.join(compare_rows)}</tbody>
          </table>
          </div>
        </section>"""

    pickups = sorted({day.get("pickup_date", CAR_PICKUP) for day in car_days}) or [CAR_PICKUP]
    dropoffs = sorted({day["dropoff_date"] for day in car_days})
    date_bar = render_date_filter(
        prefix="cars",
        start_id="car-pickup",
        end_id="car-dropoff",
        start_label="인수일",
        end_label="반납일",
        start_dates=pickups,
        end_dates=dropoffs,
        start_selected=pickups[0],
        end_selected=dropoffs[0] if dropoffs else None,
        note="인수·반납일을 고르면 해당 기간의 사이트 비교·차종 목록만 표시됩니다.",
    )
    return f"""
    {date_bar}
    {hero}
    {compare_table}
    <p class="flight-hint muted" id="car-detail-hint">선택한 반납일의 상세 차종·옵션입니다.</p>
    <p id="car-empty" class="empty-filter muted" hidden>선택한 날짜의 렌트카 데이터가 없습니다.</p>
    <div class="car-date-switch" role="tablist" aria-label="반납일">{''.join(date_tabs)}</div>
    {''.join(panels)}
    """


def render_lodging(airbnb_all: list[dict], airbnb: dict[str, dict]) -> str:
    booked = next((a for a in airbnb_all if a.get("booked")), None)
    merged = sorted(
        airbnb_all,
        key=lambda x: (0 if x.get("booked") else 1, x.get("checkout_date", ""), x.get("price") or 10**12),
    )
    cheapest_by_date = {co: row.get("price") for co, row in airbnb.items()}
    checkins = sorted({a.get("checkin") or CHECKIN for a in airbnb_all}) or [CHECKIN]
    checkouts = sorted({a["checkout_date"] for a in airbnb_all})
    best = booked or airbnb.get(checkouts[0] if checkouts else "") or (
        sorted(airbnb.values(), key=lambda x: x.get("price") or 10**12)[0] if airbnb else None
    )
    start_sel = (booked.get("checkin") if booked else None) or checkins[0]
    end_sel = (booked.get("checkout_date") if booked else None) or (checkouts[0] if checkouts else None)

    date_bar = render_date_filter(
        prefix="lodging",
        start_id="lodging-checkin",
        end_id="lodging-checkout",
        start_label="체크인",
        end_label="체크아웃",
        start_dates=checkins,
        end_dates=checkouts,
        start_selected=start_sel,
        end_selected=end_sel,
        note="체크인·체크아웃을 고르면 해당 기간 숙소만 표시됩니다. (인원 4명 고정)",
    )

    hero = ""
    if best:
        if booked and best is booked:
            hero_title = "✅ 예약 완료 숙소"
            hero_dates = (
                f"체크인 {booked.get('checkin')} {booked.get('checkin_time','')} · "
                f"체크아웃 {booked['checkout_date']} {booked.get('checkout_time','')} · "
                f"{booked.get('nights','')}박"
            )
            hero_meta = (
                f"호스트 {booked.get('host','')} · 예약코드 {booked.get('reservation_code','')} · "
                f"{booked.get('address') or booked.get('location_text','')}"
            )
            hero_note = "여행경비 탭에 이 숙소가 기본 선택되어 있습니다."
        else:
            hero_title = "숙박 후보 (Airbnb 검색 · 주방·집 전체)"
            hero_dates = (
                f"체크인 {best.get('checkin') or CHECKIN} · 체크아웃 {best['checkout_date']} · "
                f"{best.get('nights','')}박 · 해당일 최저"
            )
            hero_meta = f"{best.get('distance_text','')} · {best.get('amenities_text','')}"
            hero_note = "아래 표 · ○ 선택으로 여행경비에 반영"
        hero = f"""
        <section class="hero card" id="lodging-hero">
          <h2 id="lodging-hero-heading">{hero_title}</h2>
          <p class="hero-price" id="lodging-hero-price" style="color:var(--airbnb)">{best['price_text']}</p>
          <p id="lodging-hero-dates">{hero_dates}</p>
          <p id="lodging-hero-title">{best.get('title','')}</p>
          <p id="lodging-hero-meta">{hero_meta}</p>
          <span id="lodging-hero-cta">{BTN.format(url=best['seller_url'])}</span>
          <p class="muted" style="margin-top:10px;" id="lodging-hero-note">{hero_note}</p>
        </section>"""

    rows = []
    for a in merged:
        co = a["checkout_date"]
        ci = a.get("checkin") or CHECKIN
        is_booked = bool(a.get("booked"))
        is_best = is_booked or a.get("price") == cheapest_by_date.get(co)
        row_cls = "best booked-row" if is_booked else ("best" if is_best else "")
        lid = lodging_id(a)
        title_extra = ""
        if is_booked:
            title_extra = (
                f"<br><span class=\"pill booked-pill\">예약완료 · {a.get('reservation_code','')}</span>"
                f"<br><span class=\"muted\">{a.get('address') or a.get('location_text','')}</span>"
            )
        else:
            title_extra = f"<br><span class=\"muted\">{a.get('location_text','')}</span>"
        rows.append(f"""
        <tr class="{row_cls}" data-checkout="{co}" data-checkin="{ci}" data-lodging-id="{lid}"
            data-price="{a.get('price') or 0}" data-price-text="{a.get('price_text','')}"
            data-title="{a.get('title','')}" data-distance="{a.get('distance_text','')}"
            data-amenities="{a.get('amenities_text','')}" data-nights="{a.get('nights','')}"
            data-url="{a.get('seller_url','#')}" data-booked="{'1' if is_booked else '0'}">
          {lodging_pick_cell(a, is_booked or is_best)}
          <td>{co}<br><span class="muted">{a.get('nights','')}박</span>
            {"<br><span class='muted'>체크인 " + ci + "</span>" if is_booked else ""}</td>
          <td class="price airbnb{price_cls(a.get('price'), a.get('price') if is_booked else (cheapest_by_date.get(co) if is_best else None))}">{a['price_text']}</td>
          <td>{a.get('title','-')}{title_extra}</td>
          <td><strong>{a.get('distance_text','-')}</strong></td>
          <td>{a.get('amenities_text','-')}</td>
          <td>{BTN.format(url=a['seller_url'])}</td>
        </tr>""")

    return f"""
    {date_bar}
    {hero}
    <section class="card">
      <div class="legend">
        <span><i class="dot" style="background:var(--airbnb)"></i> Airbnb · 시카고대(University of Chicago) 기준 거리</span>
      </div>
      <p id="lodging-empty" class="empty-filter muted" hidden>선택한 날짜의 숙소 데이터가 없습니다.</p>
      <div class="table-wrap">
      <table class="lodging-table">
        <thead>
          <tr>
            <th>선택</th>
            <th>체크아웃</th>
            <th class="airbnb">총액</th>
            <th class="airbnb">숙소</th>
            <th class="airbnb">시카고대 거리</th>
            <th class="airbnb">조건</th>
            <th class="airbnb">예약</th>
          </tr>
        </thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
      </div>
      <p class="muted" style="margin-top:12px;">
        ※ {LODGING_NOTE} · 시카고대 인근 · 주방 · 집 전체 · 성인 {ADULTS} + 아동 {len(CHILD_AGES)}<br>
        ※ 선택한 체크아웃(귀국일) 후보 · 3시간마다 갱신
      </p>
    </section>"""


def render_combo_analysis(combos: list[dict]) -> str:
    if not combos:
        return ""
    best = combos[0]
    rows = []
    for i, c in enumerate(combos):
        badge = "★ 추천" if i == 0 else ""
        rows.append(f"""
        <tr class="{'best' if i == 0 else ''}" data-return="{c['return_date']}">
          <td>{badge}</td>
          <td><strong>{c['return_date']}</strong></td>
          <td>{c['flight_source']}<br><span class="muted">1인 {c['flight_per_person_text']}</span></td>
          <td class="price">{fmt_won(c['flight_price'])}</td>
          <td>{c['lodging_nights']}박<br><span class="muted">{c['lodging_title'][:28]}…</span></td>
          <td class="price airbnb">{c['lodging_price_text']}</td>
          <td class="price"><strong>{fmt_won(c['combined'])}</strong></td>
          <td><button type="button" class="cta-btn combo-apply" data-flight="{c['flight_id']}" data-lodging="{c.get('lodging_id', c['lodging_checkout'])}">적용</button></td>
        </tr>""")

    return f"""
    <section class="card">
      <h3>📊 귀국일 분석 — 항공+숙박 최저 조합</h3>
      <p class="muted">출발 {OUTBOUND} · {LODGING_NOTE} · Airbnb 체크인 {CHECKIN} · 귀국일=체크아웃</p>
      <div class="combo-hero">
        <strong>추천: {best['return_date']} 귀국</strong>
        · {best['flight_source']} + Airbnb {best['lodging_nights']}박
        · 항공+숙박 <span class="price">{fmt_won(best['combined'])}</span>
      </div>
      <div class="table-wrap">
      <table class="combo-table">
        <thead>
          <tr>
            <th></th><th>귀국/체크아웃</th><th>항공(최저)</th><th>항공 4명</th>
            <th>숙박</th><th>숙박 총액</th><th>합계</th><th></th>
          </tr>
        </thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
      </div>
      <p class="muted" style="margin-top:12px;">※ 각 귀국일별 루트(뉴욕인·시카고아웃 / 시카고왕복) 최저가 항공 + 해당일 Airbnb 숙박 합계입니다.</p>
    </section>"""


def render_dashboard_shell(combo_html: str) -> str:
    return f"""
    {combo_html}
    <section class="dashboard-hero card">
      <div class="dash-hero-inner">
        <div>
          <p class="dash-kicker">Total Trip Budget</p>
          <h2>총 여행경비</h2>
          <p id="total-budget" class="total-price">₩0</p>
          <p id="trip-summary" class="muted">항공권과 숙박을 선택하면 합계가 계산됩니다.</p>
        </div>
        <div class="dash-meta-box">
          <div><span class="muted">일정</span><strong id="dash-schedule">-</strong></div>
          <div><span class="muted">인원</span><strong>성인 2 + 어린이 2</strong></div>
          <div><span class="muted">숙박</span><strong id="dash-nights">-</strong></div>
        </div>
      </div>
    </section>

    <div class="dash-grid">
      <article class="dash-card" data-kind="flight">
        <div class="dash-card-head"><span>✈️</span><h3>항공권</h3></div>
        <p class="dash-amount" id="amt-flight">₩0</p>
        <p class="dash-sub" id="sub-flight">1인당</p>
        <p class="dash-detail" id="detail-flight">미선택 · <a href="#" data-goto="flights">항공권 탭에서 선택</a></p>
      </article>
      <article class="dash-card" data-kind="lodging">
        <div class="dash-card-head"><span>🏠</span><h3>숙박</h3></div>
        <p class="dash-amount" id="amt-lodging">₩0</p>
        <p class="dash-detail" id="detail-lodging">미선택 · <a href="#" data-goto="lodging">숙박 탭에서 선택</a></p>
      </article>
      <article class="dash-card" data-kind="food">
        <div class="dash-card-head"><span>🍽️</span><h3>식비</h3></div>
        <label class="field-label" for="food-per-day">1일 식비 (4명)</label>
        <input id="food-per-day" type="number" min="0" step="10000" class="cost-input">
        <p class="dash-sub" id="food-calc">0박 × ₩0 = ₩0</p>
        <p class="dash-amount" id="amt-food">₩0</p>
      </article>
      <article class="dash-card" data-kind="car">
        <div class="dash-card-head"><span>🚗</span><h3>자동차 렌트</h3></div>
        <p class="dash-amount" id="amt-car">₩0</p>
        <p class="dash-detail" id="detail-car">미선택 · <a href="#" data-goto="cars">렌트카 탭에서 선택</a></p>
        <label class="field-label" for="cost-car">직접 수정 (총액)</label>
        <input id="cost-car" type="number" min="0" step="10000" class="cost-input">
      </article>
      <article class="dash-card" data-kind="gift">
        <div class="dash-card-head"><span>🎁</span><h3>선물비</h3></div>
        <label class="field-label" for="cost-gift">선물 예산</label>
        <input id="cost-gift" type="number" min="0" step="10000" class="cost-input">
        <p class="dash-amount" id="amt-gift">₩0</p>
      </article>
      <article class="dash-card" data-kind="misc">
        <div class="dash-card-head"><span>🎫</span><h3>기타 여행비</h3></div>
        <label class="field-label" for="cost-misc">관광·교통·기타</label>
        <input id="cost-misc" type="number" min="0" step="10000" class="cost-input">
        <p class="dash-amount" id="amt-misc">₩0</p>
      </article>
    </div>

    <section class="card">
      <h3>경비 breakdown</h3>
      <div class="breakdown-wrap">
        <table class="breakdown-table">
          <thead>
            <tr><th>항목</th><th>금액</th><th>비율</th><th></th></tr>
          </thead>
          <tbody id="breakdown-body"></tbody>
        </table>
        <div class="bar-chart" id="bar-chart"></div>
      </div>
      <p class="muted" style="margin-top:12px;">
        ※ 항공권·숙박·렌트카는 각 탭에서 선택한 값이 자동 반영됩니다. 식비·렌트 금액·선물·기타는 직접 수정 가능하며 브라우저에 저장됩니다.
      </p>
    </section>"""


def render_page(
    flights_html: str,
    lodging_html: str,
    cars_html: str,
    chicago_plan_html: str,
    east_plan_html: str,
    dashboard_html: str,
    trip_data: dict,
    now_kst: str,
) -> str:
    trip_json = json.dumps(trip_data, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="refresh" content="{REFRESH_SECONDS}">
  <title>서울→시카고 여행계획 | 항공 · 숙박 · 렌트 · 일정</title>
  <style>
    :root {{
      --sky: #0770e3; --kayak: #ff690f; --google: #1a73e8;
      --discover: #1f6feb; --rentalcars: #0d9488;
      --airbnb: #ff385c; --budget: #0d7a5f;
      --bg: #eef1f6; --card: #fff; --text: #14171c; --muted: #5f6773;
      --best: #e8f4fd; --highlight: #fff8e1; --picked: #e7f7f0;
      --nyc: #1f4b99; --chi: #c45c26; --cheap: #0f7a57; --fast: #2558c8;
      --line: #e2e7ef;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; font-family: "Segoe UI", "Noto Sans KR", sans-serif;
      background:
        radial-gradient(1200px 500px at 10% -10%, #d9e7ff 0%, transparent 55%),
        radial-gradient(900px 420px at 90% 0%, #ffe4d4 0%, transparent 50%),
        var(--bg);
      color: var(--text);
    }}
    .wrap {{ max-width: 1180px; margin: 0 auto; padding: 24px; }}
    h1 {{ margin: 0 0 8px; font-size: 1.75rem; letter-spacing: -0.02em; }}
    h3 {{ margin: 0 0 12px; font-size: 1.05rem; }}
    .meta {{ color: var(--muted); font-size: 0.95rem; margin-bottom: 16px; }}
    .tabs {{ display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; }}
    .tab {{
      border: none; background: rgba(255,255,255,.75); color: var(--text);
      padding: 12px 22px; border-radius: 999px; font-size: 1rem; font-weight: 600; cursor: pointer;
      box-shadow: 0 1px 2px rgba(20,25,35,.06);
    }}
    .tab.active {{ background: #1b1f27; color: #fff; }}
    .panel {{ display: none; }}
    .panel.active {{ display: block; }}
    .card {{ background: var(--card); border-radius: 16px; padding: 20px; box-shadow: 0 8px 24px rgba(24,33,50,.06); margin-bottom: 20px; border: 1px solid rgba(255,255,255,.7); }}
    .hero {{ text-align: center; }}
    .hero-price {{ font-size: 2rem; font-weight: 700; margin: 8px 0; }}
    .route-switch {{
      display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px;
    }}
    .route-tab {{
      text-align: left; border: 1px solid var(--line); background: rgba(255,255,255,.88);
      border-radius: 16px; padding: 16px 18px; cursor: pointer;
      transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease;
    }}
    .route-tab:hover {{ transform: translateY(-1px); box-shadow: 0 8px 20px rgba(24,33,50,.08); }}
    .route-tab.active[data-route="nyc_in"] {{
      border-color: rgba(31,75,153,.45); background: linear-gradient(135deg, # diversc8f 0%, #ffffff 70%);
      box-shadow: 0 10px 24px rgba(31,75,153,.12);
    }}
    .route-tab.active[data-route="chi_round"] {{
      border-color: rgba(196,92,38,.4); background: linear-gradient(135deg, #ffe8d8 0%, #ffffff 70%);
      box-shadow: 0 10px 24px rgba(196,92,38,.12);
    }}
    .route-tab-title {{ display: block; font-size: 1.05rem; font-weight: 800; margin-bottom: 4px; }}
    .route-tab-sub {{ display: block; color: var(--muted); font-size: 0.82rem; }}
    .flight-hint {{ margin: 0 0 18px; }}
    .route-panel {{ display: none; }}
    .route-panel.active {{ display: block; }}
    .route-hero {{
      display: flex; justify-content: space-between; gap: 20px; flex-wrap: wrap; align-items: stretch;
      background: linear-gradient(135deg, #162033 0%, #243552 100%); color: #fff;
    }}
    .route-hero .muted {{ color: rgba(255,255,255,.72); }}
    .route-kicker {{
      margin: 0 0 6px; font-size: 0.78rem; letter-spacing: .08em; text-transform: uppercase; opacity: .8;
    }}
    .route-hero h2 {{ margin: 0 0 8px; font-size: 1.45rem; }}
    .route-stats {{ display: flex; gap: 12px; flex-wrap: wrap; }}
    .route-stat {{
      min-width: 160px; background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.12);
      border-radius: 14px; padding: 14px 16px; display: grid; gap: 4px;
    }}
    .route-stat strong {{ font-size: 1.2rem; }}
    .date-filter {{
      background: linear-gradient(180deg, #ffffff 0%, #f7f9fc 100%);
      border: 1px solid var(--line);
      margin-bottom: 16px;
    }}
    .date-filter-head {{
      display: flex; justify-content: space-between; gap: 12px; align-items: flex-start;
      flex-wrap: wrap; margin-bottom: 14px;
    }}
    .date-filter-title {{ margin: 0; font-size: 1.15rem; }}
    .date-filter-guests {{
      margin: 0; font-size: 0.85rem; font-weight: 700; color: #334155;
      background: #eef2ff; border-radius: 999px; padding: 8px 12px;
    }}
    .date-filter-grid {{
      display: grid; grid-template-columns: 1fr 1fr; gap: 14px;
    }}
    .date-field {{ display: block; }}
    .date-select {{
      width: 100%; padding: 12px 14px; border: 1px solid #d7dbe3; border-radius: 10px;
      font-size: 1rem; font-family: inherit; background: #fff; font-weight: 600;
    }}
    .date-filter-note {{ margin: 12px 0 0; }}
    .empty-filter {{
      background: #fff7ed; border: 1px dashed #fdba74; border-radius: 12px;
      padding: 14px 16px; margin: 0 0 16px;
    }}
    .date-stack {{ display: grid; gap: 16px; }}
    .date-card {{
      background: var(--card); border: 1px solid var(--line); border-radius: 18px; padding: 18px;
      box-shadow: 0 6px 18px rgba(24,33,50,.05);
    }}
    .date-card[hidden], .car-date-panel[hidden], tr[hidden] {{ display: none !important; }}
    .date-card-head {{
      display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; margin-bottom: 14px;
    }}
    .date-kicker {{ margin: 0; font-size: 0.75rem; color: var(--muted); letter-spacing: .06em; text-transform: uppercase; }}
    .date-card-head h3 {{ margin: 2px 0 4px; font-size: 1.35rem; letter-spacing: -0.02em; }}
    .date-chip {{
      background: #f3f5f9; color: #334155; border-radius: 999px; padding: 6px 12px;
      font-size: 0.78rem; font-weight: 700; white-space: nowrap;
    }}
    .opt-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    .opt-card {{
      border-radius: 14px; padding: 16px; border: 1px solid var(--line); background: #fbfcfe;
      min-height: 100%;
    }}
    .opt-card.opt-cheapest {{ border-top: 4px solid var(--cheap); }}
    .opt-card.opt-shortest {{ border-top: 4px solid var(--fast); }}
    .opt-card.opt-cheap17 {{ border-top: 4px solid #0ea5e9; }}
    .opt-cheap17 .opt-badge {{ color: #0ea5e9; }}
    .opt-extra {{ margin-top: 14px; padding-top: 12px; border-top: 1px dashed var(--border); }}
    .opt-extra-title {{ font-size: 0.88rem; font-weight: 700; margin: 0 0 10px; color: #0369a1; }}
    .opt-grid-extra {{ grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); }}
    .opt-card.is-empty {{ opacity: .65; }}
    .opt-head {{ display: flex; justify-content: space-between; gap: 8px; align-items: center; margin-bottom: 8px; }}
    .opt-badge {{ font-size: 0.82rem; font-weight: 800; }}
    .opt-cheapest .opt-badge {{ color: var(--cheap); }}
    .opt-shortest .opt-badge {{ color: var(--fast); }}
    .pill {{
      display: inline-block; font-size: 0.72rem; font-weight: 700; border-radius: 999px;
      padding: 3px 8px; background: #fff1d6; color: #9a6700;
    }}
    .opt-price {{ margin: 0; font-size: 1.55rem; font-weight: 800; letter-spacing: -0.02em; }}
    .opt-sub {{ margin: 4px 0 12px; color: var(--muted); font-size: 0.8rem; }}
    .opt-meta {{ margin: 0 0 14px; display: grid; gap: 8px; }}
    .opt-meta div {{ display: grid; grid-template-columns: 52px 1fr; gap: 8px; font-size: 0.86rem; }}
    .opt-meta dt {{ color: var(--muted); margin: 0; }}
    .opt-meta dd {{ margin: 0; font-weight: 600; }}
    .opt-actions {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }}
    .opt-actions .cta-btn {{ background: #1b1f27; }}
    .date-card.is-picked, .date-card:has(.flight-pick:checked) {{
      border-color: rgba(13,122,95,.35); box-shadow: 0 0 0 2px rgba(13,122,95,.12);
    }}
    .car-hero {{ background: linear-gradient(135deg, #312e81 0%, #4338ca 55%, #6366f1 100%); }}
    .car-date-switch {{
      display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 10px; margin-bottom: 16px;
    }}
    .car-date-tab {{
      text-align: left; border: 1px solid var(--line); background: rgba(255,255,255,.9);
      border-radius: 14px; padding: 12px 14px; cursor: pointer;
    }}
    .car-date-tab.active {{
      border-color: rgba(99,102,241,.45);
      background: linear-gradient(135deg, #e0e7ff 0%, #fff 70%);
      box-shadow: 0 8px 18px rgba(99,102,241,.12);
    }}
    .car-date-main {{ display: block; font-weight: 800; margin-bottom: 2px; }}
    .car-date-sub {{ display: block; color: var(--muted); font-size: 0.78rem; }}
    .car-date-panel {{ display: none; }}
    .car-date-panel.active {{ display: block; }}
    .car-cat-block {{ margin-bottom: 22px; }}
    .car-cat-title {{
      margin: 0 0 10px; font-size: 1rem; padding-left: 10px;
      border-left: 4px solid #6366f1;
    }}
    .car-cat-block[data-cat="전기차"] .car-cat-title {{ border-left-color: #059669; color: #047857; }}
    .car-cat-block[data-cat="전기차"] .car-card {{
      background: linear-gradient(180deg, #ecfdf5 0%, #fff 45%);
      border-color: #a7f3d0;
    }}
    .car-pill.ev {{ background: #d1fae5; color: #065f46; }}
    .car-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; }}
    .car-card {{
      background: #fff; border: 1px solid var(--line); border-radius: 14px; padding: 14px 16px;
      box-shadow: 0 4px 14px rgba(24,33,50,.04);
    }}
    .car-card:has(.car-pick:checked) {{
      border-color: rgba(99,102,241,.45); box-shadow: 0 0 0 2px rgba(99,102,241,.12);
    }}
    .car-card-top {{ display: flex; justify-content: space-between; gap: 10px; align-items: flex-start; }}
    .car-cat {{ margin: 0; font-size: 0.75rem; font-weight: 800; color: #6366f1; letter-spacing: .04em; }}
    .car-model {{ margin: 2px 0 4px; font-size: 1.05rem; }}
    .car-price {{ margin: 0; font-size: 1.25rem; font-weight: 800; color: #312e81; white-space: nowrap; }}
    .car-loc {{ margin: 8px 0; font-size: 0.8rem; }}
    .car-pills {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; min-height: 24px; }}
    .car-pill {{
      background: #eef2ff; color: #3730a3; border-radius: 999px;
      padding: 4px 9px; font-size: 0.72rem; font-weight: 700;
    }}
    .itin-hero.chi-itin-hero {{
      background: linear-gradient(135deg, #0c4a6e 0%, #0369a1 55%, #0ea5e9 100%);
    }}
    .itin-hero.east-itin-hero {{
      background: linear-gradient(135deg, #3b0764 0%, #6d28d9 50%, #a78bfa 100%);
    }}
    .itin-stack {{ display: grid; gap: 14px; }}
    .itin-day {{
      background: #fff; border: 1px solid var(--line); border-radius: 16px; padding: 16px 18px;
      box-shadow: 0 4px 14px rgba(24,33,50,.04);
    }}
    .itin-day-head {{
      display: flex; flex-wrap: wrap; gap: 10px; align-items: baseline; margin-bottom: 10px;
    }}
    .itin-day-num {{
      background: #0ea5e9; color: #fff; font-size: 0.75rem; font-weight: 800;
      border-radius: 999px; padding: 4px 10px;
    }}
    .east-nyc .itin-day-num {{ background: #4f46e5; }}
    .east-dc .itin-day-num {{ background: #b45309; }}
    .east-bos .itin-day-num {{ background: #047857; }}
    .itin-day-head h3 {{ margin: 0; flex: 1; font-size: 1.1rem; }}
    .itin-day-total {{ font-weight: 800; color: var(--budget); white-space: nowrap; }}
    .itin-places {{ margin: 0 0 10px; padding-left: 18px; color: #334155; line-height: 1.5; }}
    .itin-tip {{
      margin: 0 0 10px; padding: 8px 12px; background: #f8fafc; border-radius: 10px;
      color: var(--muted); font-size: 0.85rem;
    }}
    .itin-spend {{ width: 100%; border-collapse: collapse; font-size: 0.86rem; min-width: 0 !important; }}
    .itin-spend th, .itin-spend td {{ padding: 8px 6px; border-bottom: 1px solid #eef2f7; text-align: left; }}
    .itin-spend th {{ background: transparent; color: var(--muted); font-size: 0.75rem; }}
    .east-panel {{ display: none; }}
    .east-panel.active {{ display: block; }}
    .east-switch {{ margin-bottom: 16px; }}
    .dashboard-hero {{ background: linear-gradient(135deg, #0d7a5f 0%, #0a5c48 100%); color: #fff; }}
    .dashboard-hero .muted {{ color: rgba(255,255,255,.78); }}
    .dash-hero-inner {{ display: flex; justify-content: space-between; gap: 24px; flex-wrap: wrap; align-items: flex-start; }}
    .dash-kicker {{ margin: 0; font-size: 0.8rem; letter-spacing: .08em; text-transform: uppercase; opacity: .85; }}
    .total-price {{ font-size: 2.6rem; font-weight: 800; margin: 8px 0 12px; line-height: 1.1; }}
    .dash-meta-box {{ display: grid; gap: 10px; min-width: 180px; background: rgba(255,255,255,.12); padding: 16px; border-radius: 10px; }}
    .dash-meta-box .muted {{ display: block; font-size: 0.75rem; margin-bottom: 2px; }}
    .dash-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 20px; }}
    .dash-card {{ background: var(--card); border-radius: 12px; padding: 18px; box-shadow: 0 2px 8px rgba(0,0,0,.06); border-top: 4px solid #ddd; }}
    .dash-card[data-kind="flight"] {{ border-top-color: var(--sky); }}
    .dash-card[data-kind="lodging"] {{ border-top-color: var(--airbnb); }}
    .dash-card[data-kind="food"] {{ border-top-color: #f59e0b; }}
    .dash-card[data-kind="car"] {{ border-top-color: #6366f1; }}
    .dash-card[data-kind="gift"] {{ border-top-color: #ec4899; }}
    .dash-card[data-kind="misc"] {{ border-top-color: #64748b; }}
    .dash-card-head {{ display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }}
    .dash-card-head h3 {{ margin: 0; font-size: 1rem; }}
    .dash-amount {{ font-size: 1.35rem; font-weight: 800; margin: 8px 0 4px; color: var(--budget); }}
    .dash-detail, .dash-sub {{ font-size: 0.82rem; color: var(--muted); margin: 0; line-height: 1.45; }}
    .dash-detail a {{ color: var(--sky); }}
    .field-label {{ display: block; font-size: 0.78rem; color: var(--muted); margin-bottom: 6px; }}
    .cost-input {{
      width: 100%; padding: 10px 12px; border: 1px solid #d7dbe3; border-radius: 8px;
      font-size: 0.95rem; font-family: inherit;
    }}
    .breakdown-wrap {{ display: grid; grid-template-columns: 1.2fr 1fr; gap: 24px; align-items: start; }}
    .breakdown-table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
    .breakdown-table th, .breakdown-table td {{ padding: 10px 8px; border-bottom: 1px solid #e0e4ea; text-align: left; }}
    .breakdown-table th {{ color: var(--muted); font-size: 0.78rem; }}
    .bar-row {{ display: flex; align-items: center; gap: 10px; margin-bottom: 10px; font-size: 0.82rem; }}
    .bar-label {{ width: 88px; flex-shrink: 0; }}
    .bar-track {{ flex: 1; height: 10px; background: #eceef3; border-radius: 999px; overflow: hidden; }}
    .bar-fill {{ height: 100%; border-radius: 999px; }}
    .table-wrap {{ overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; min-width: 1100px; }}
    table.lodging-table {{ min-width: 800px; }}
    table.combo-table {{ min-width: 900px; font-size: 0.82rem; }}
    .combo-hero {{
      background: var(--best); border-radius: 8px; padding: 12px 16px;
      margin: 12px 0 16px; font-size: 0.95rem;
    }}
    th, td {{ padding: 10px 8px; border-bottom: 1px solid #e0e4ea; vertical-align: middle; }}
    th {{ background: #fafbfc; color: var(--muted); font-size: 0.78rem; }}
    th.sky {{ color: var(--sky); border-top: 3px solid var(--sky); }}
    th.kayak {{ color: var(--kayak); border-top: 3px solid var(--kayak); }}
    th.google {{ color: var(--google); border-top: 3px solid var(--google); }}
    th.discover {{ color: var(--discover); border-top: 3px solid var(--discover); }}
    th.rentalcars {{ color: var(--rentalcars); border-top: 3px solid var(--rentalcars); }}
    th.airbnb {{ color: var(--airbnb); border-top: 3px solid var(--airbnb); }}
    tr.best {{ background: var(--best); }}
    tr.picked-row {{ background: var(--picked) !important; }}
    tr.booked-row {{ outline: 2px solid var(--airbnb); outline-offset: -2px; }}
    .booked-pill {{
      display: inline-block; margin-top: 4px; padding: 2px 8px; border-radius: 999px;
      background: #ffe8ee; color: var(--airbnb); font-size: 0.75rem; font-weight: 700;
    }}
    .price {{ font-weight: 700; }}
    .price.sky {{ color: var(--sky); }}
    .price.kayak {{ color: var(--kayak); }}
    .price.google {{ color: var(--google); }}
    .price.discover {{ color: var(--discover); }}
    .price.rentalcars {{ color: var(--rentalcars); }}
    .price.airbnb {{ color: var(--airbnb); }}
    .price.highlight {{ background: var(--highlight); border-radius: 4px; }}
    table.car-compare-table {{ min-width: 960px; }}
    td.best-src {{ background: var(--highlight); }}
    .car-src-tag {{
      display: inline-block; font-size: 0.68rem; padding: 2px 6px; border-radius: 999px;
      background: #eef2ff; color: #3730a3; margin-right: 4px; vertical-align: middle;
    }}
    .car-src-tag.discover {{ background: #dbeafe; color: #1e40af; }}
    .car-src-tag.rentalcars {{ background: #ccfbf1; color: #115e59; }}
    .car-src-tag.kayak {{ background: #ffedd5; color: #9a3412; }}
    .pick-label {{ display: flex; align-items: center; gap: 8px; cursor: pointer; }}
    .pick-label input {{ accent-color: var(--budget); }}
    .lodging-pick-label span {{ font-size: 0.78rem; font-weight: 700; color: var(--budget); }}
    .muted {{ color: var(--muted); font-size: 0.8rem; }}
    .cta-link {{ text-decoration: none; }}
    .cta-btn {{
      background: #333; color: #fff; border: none; border-radius: 999px;
      padding: 8px 14px; font-size: 0.85rem; font-weight: 600; cursor: pointer;
    }}
    .legend {{ display: flex; gap: 16px; margin-bottom: 12px; font-size: 0.9rem; flex-wrap: wrap; }}
    .legend span {{ display: inline-flex; align-items: center; gap: 6px; }}
    .dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
    footer {{ text-align: center; color: var(--muted); font-size: 0.85rem; margin-top: 16px; }}
    footer a {{ color: var(--muted); }}
    @media (max-width: 900px) {{
      table {{ font-size: 0.75rem; }}
      .cta-btn {{ padding: 6px 10px; }}
      .breakdown-wrap {{ grid-template-columns: 1fr; }}
      .total-price {{ font-size: 2rem; }}
      .route-switch, .opt-grid, .car-grid, .east-switch, .date-filter-grid {{ grid-template-columns: 1fr; }}
      .route-hero {{ padding: 18px; }}
      .opt-price {{ font-size: 1.35rem; }}
      .tab {{ padding: 10px 14px; font-size: 0.9rem; }}
      .itin-day-head {{ align-items: flex-start; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>서울 → 시카고 여행계획</h1>
      <p class="meta">
        성인 {ADULTS}명 · 유소아 {len(CHILD_AGES)}명 (만 {CHILD_AGES[0]}·{CHILD_AGES[1]}세) · 동기화: {now_kst} · {REFRESH_HOURS}시간마다 자동 갱신
      </p>
      <nav class="tabs" role="tablist">
        <button class="tab active" role="tab" aria-selected="true" data-panel="dashboard">💰 여행경비</button>
        <button class="tab" role="tab" aria-selected="false" data-panel="flights">✈️ 항공권</button>
        <button class="tab" role="tab" aria-selected="false" data-panel="lodging">🏠 숙박</button>
        <button class="tab" role="tab" aria-selected="false" data-panel="cars">🚗 렌트카</button>
        <button class="tab" role="tab" aria-selected="false" data-panel="chi-plan">🗺️ 시카고 10일</button>
        <button class="tab" role="tab" aria-selected="false" data-panel="east-plan">🗽 동부 3일</button>
      </nav>
    </header>

    <div id="dashboard" class="panel active" role="tabpanel">
      <p class="meta">선택한 항공권·숙박·렌트카 + 식비·선물·기타 = 총 여행경비</p>
      {dashboard_html}
    </div>

    <div id="flights" class="panel" role="tabpanel">
      <p class="meta">위에서 출국·귀국일을 고르면 해당 일정 결과만 표시됩니다 · 성인 {ADULTS} · 아동 {len(CHILD_AGES)}</p>
      {flights_html}
    </div>

    <div id="lodging" class="panel" role="tabpanel">
      <p class="meta">위에서 체크인·체크아웃을 고르면 해당 숙소만 표시됩니다 · 시카고대 · 주방 · 집 전체</p>
      {lodging_html}
    </div>

    <div id="cars" class="panel" role="tabpanel">
      <p class="meta">위에서 인수·반납일을 고르면 해당 렌트 결과만 표시됩니다 · ORD · 사이트 비교</p>
      {cars_html}
    </div>

    <div id="chi-plan" class="panel" role="tabpanel">
      <p class="meta">시카고 현지 10일 동선 · 대략 지출(항공·숙박·렌트 제외)</p>
      {chicago_plan_html}
    </div>

    <div id="east-plan" class="panel" role="tabpanel">
      <p class="meta">뉴욕 · 워싱턴 · 보스턴 각 3일 코스 · 대략 지출(도시 간 이동비 별도)</p>
      {east_plan_html}
    </div>

    <footer>
      <a href="https://www.skyscanner.co.kr/" target="_blank">Skyscanner</a> ·
      <a href="https://www.kayak.co.kr/" target="_blank">KAYAK</a> ·
      <a href="https://www.google.com/travel/flights?hl=ko" target="_blank">Google Flights</a> ·
      <a href="https://www.airbnb.co.kr/" target="_blank">Airbnb</a>
    </footer>
  </div>

  <script id="trip-data" type="application/json">{trip_json}</script>
  <script>
    const TRIP = JSON.parse(document.getElementById('trip-data').textContent);
    const STORE_KEY = 'chicago-trip-budget-v7';
    const DATE_OPTS = TRIP.date_options || {{}};

    const fmt = n => '₩' + Math.round(n || 0).toLocaleString('ko-KR');
    const pct = (part, total) => total ? Math.round(part / total * 100) : 0;

    const COLORS = {{
      flight: '#0770e3', lodging: '#ff385c', food: '#f59e0b',
      car: '#6366f1', gift: '#ec4899', misc: '#64748b'
    }};

    function loadState() {{
      try {{ return JSON.parse(localStorage.getItem(STORE_KEY) || '{{}}'); }}
      catch {{ return {{}}; }}
    }}

    function saveState(state) {{
      // Merge so budget saves never wipe date filters.
      const merged = Object.assign({{}}, loadState(), state);
      localStorage.setItem(STORE_KEY, JSON.stringify(merged));
    }}

    function firstAvailable(list, preferred) {{
      const arr = list || [];
      if (preferred && arr.includes(preferred)) return preferred;
      return arr[0] || '';
    }}

    function getBookedLodging() {{
      return (TRIP.lodging || []).find(l => l.booked) || findLodging(TRIP.booked_lodging_id);
    }}

    function getTripDates() {{
      const saved = loadState();
      const rec = TRIP.recommended?.return_date;
      const booked = getBookedLodging();
      const preferCheckout = booked?.checkout_date || saved.checkout || rec;
      const preferReturn = booked?.checkout_date || saved.returnDate || rec || TRIP.outbound;
      return {{
        outbound: firstAvailable(DATE_OPTS.outbound, saved.outbound || TRIP.outbound),
        returnDate: firstAvailable(DATE_OPTS.return, preferReturn),
        checkin: firstAvailable(DATE_OPTS.checkin, booked?.checkin_date || saved.checkin || TRIP.checkin),
        checkout: firstAvailable(DATE_OPTS.checkout, preferCheckout),
        pickup: firstAvailable(DATE_OPTS.pickup, saved.pickup || TRIP.car_pickup),
        dropoff: firstAvailable(DATE_OPTS.dropoff, booked?.checkout_date || saved.dropoff || rec),
      }};
    }}

    function setSelectValue(id, value) {{
      const el = document.getElementById(id);
      if (!el || !value) return;
      if ([...el.options].some(o => o.value === value)) el.value = value;
    }}

    function syncDateSelects(dates) {{
      setSelectValue('flight-outbound', dates.outbound);
      setSelectValue('flight-return', dates.returnDate);
      setSelectValue('lodging-checkin', dates.checkin);
      setSelectValue('lodging-checkout', dates.checkout);
      setSelectValue('car-pickup', dates.pickup);
      setSelectValue('car-dropoff', dates.dropoff);
    }}

    function persistTripDates(dates) {{
      const s = loadState();
      Object.assign(s, {{
        outbound: dates.outbound,
        returnDate: dates.returnDate,
        checkin: dates.checkin,
        checkout: dates.checkout,
        pickup: dates.pickup,
        dropoff: dates.dropoff,
      }});
      saveState(s);
    }}

    function updateLodgingHero(checkout, checkin) {{
      const rows = [...document.querySelectorAll('tr[data-lodging-id]')].filter(tr =>
        tr.dataset.checkout === checkout && (!checkin || tr.dataset.checkin === checkin)
      );
      const hero = document.getElementById('lodging-hero');
      if (!hero) return;
      if (!rows.length) {{
        hero.hidden = true;
        return;
      }}
      hero.hidden = false;
      const bookedRow = rows.find(tr => tr.dataset.booked === '1');
      const best = bookedRow || rows.reduce((a, b) => (Number(a.dataset.price) <= Number(b.dataset.price) ? a : b));
      const priceEl = document.getElementById('lodging-hero-price');
      const datesEl = document.getElementById('lodging-hero-dates');
      const titleEl = document.getElementById('lodging-hero-title');
      const metaEl = document.getElementById('lodging-hero-meta');
      const ctaEl = document.getElementById('lodging-hero-cta');
      const headingEl = document.getElementById('lodging-hero-heading');
      const noteEl = document.getElementById('lodging-hero-note');
      if (priceEl) priceEl.textContent = best.dataset.priceText || fmt(Number(best.dataset.price));
      if (datesEl) {{
        datesEl.textContent = bookedRow
          ? `체크인 ${{checkin}} · 체크아웃 ${{checkout}} · ${{best.dataset.nights || ''}}박 · 예약완료`
          : `체크인 ${{checkin}} · 체크아웃 ${{checkout}} · ${{best.dataset.nights || ''}}박 · 해당일 최저`;
      }}
      if (titleEl) titleEl.textContent = best.dataset.title || '';
      if (metaEl) metaEl.textContent = `${{best.dataset.distance || ''}} · ${{best.dataset.amenities || ''}}`;
      if (headingEl) headingEl.textContent = bookedRow ? '✅ 예약 완료 숙소' : '숙박 후보 (Airbnb 검색 · 주방·집 전체)';
      if (noteEl) noteEl.textContent = bookedRow
        ? '여행경비 탭에 이 숙소가 기본 선택되어 있습니다.'
        : '아래 표 · ○ 선택으로 여행경비에 반영';
      if (ctaEl) {{
        ctaEl.innerHTML = `<a class="cta-link" href="${{best.dataset.url || '#'}}" target="_blank" rel="noopener noreferrer"><button type="button" class="cta-btn">선택하기</button></a>`;
      }}
    }}

    function fmtDateKo(iso) {{
      if (!iso) return '';
      const parts = iso.split('-');
      return `${{Number(parts[1])}}월 ${{Number(parts[2])}}일`;
    }}

    function updateCarHero(dropoff) {{
      const row = document.querySelector(`.car-compare-table tbody tr[data-dropoff="${{dropoff}}"]`);
      const priceEl = document.getElementById('car-hero-price');
      const metaEl = document.getElementById('car-hero-meta');
      const labelEl = document.getElementById('car-hero-label');
      const blurbEl = document.getElementById('car-hero-blurb');
      const hintEl = document.getElementById('car-compare-hint');
      const detailHint = document.getElementById('car-detail-hint');
      if (labelEl) labelEl.textContent = dropoff ? `${{fmtDateKo(dropoff)}} 반납 최저가` : '선택일 최저가';
      if (blurbEl) blurbEl.textContent = dropoff
        ? `DiscoverCars · Rentalcars.com · KAYAK · 인수 ${{TRIP.car_pickup}} · 반납 ${{dropoff}}`
        : `DiscoverCars · Rentalcars.com · KAYAK · 전기차 포함 · 인수 ${{TRIP.car_pickup}}`;
      if (hintEl) hintEl.textContent = dropoff
        ? `${{fmtDateKo(dropoff)}} 반납 기준 사이트 최저가입니다. ○ 선택 → 여행경비 반영 · 아래 목록에 전기차(EV)도 포함됩니다.`
        : '반납일을 고르면 해당일 사이트 최저가만 표시됩니다.';
      if (detailHint) detailHint.textContent = dropoff
        ? `${{fmtDateKo(dropoff)}} 반납 · 상세 차종·옵션입니다.`
        : '선택한 반납일의 상세 차종·옵션입니다.';

      const picks = row
        ? [...row.querySelectorAll('.car-pick')].map(el => ({{
            price: Number(el.dataset.price) || 0,
            label: (el.closest('label')?.querySelector('.muted')?.textContent || '').trim(),
            priceText: el.closest('label')?.querySelector('strong')?.textContent || fmt(Number(el.dataset.price)),
          }})).filter(x => x.price > 0)
        : [];
      if (picks.length) {{
        const best = picks.reduce((a, b) => (a.price <= b.price ? a : b));
        if (priceEl) priceEl.textContent = best.priceText;
        if (metaEl) metaEl.textContent = best.label || '';
        return;
      }}
      const cars = (TRIP.cars || []).filter(c => c.dropoff_date === dropoff && c.price);
      if (cars.length) {{
        const best = cars.reduce((a, b) => (a.price <= b.price ? a : b));
        if (priceEl) priceEl.textContent = best.price_text || fmt(best.price);
        if (metaEl) {{
          metaEl.textContent = `${{best.source_label || best.source || ''}} · ${{best.category || ''}} · ${{best.model || ''}}`;
        }}
      }}
    }}

    function applyDateFilters() {{
      const dates = getTripDates();
      syncDateSelects(dates);

      let flightVisible = 0;
      document.querySelectorAll('.date-card').forEach(card => {{
        const cardReturn = card.getAttribute('data-return') || card.dataset.return;
        const on = cardReturn === dates.returnDate;
        card.hidden = !on;
        if (on) flightVisible += 1;
      }});
      const flightEmpty = document.getElementById('flight-empty');
      if (flightEmpty) flightEmpty.hidden = flightVisible > 0;

      let lodgingVisible = 0;
      document.querySelectorAll('tr[data-lodging-id]').forEach(tr => {{
        const on = tr.dataset.checkout === dates.checkout
          && (!dates.checkin || tr.dataset.checkin === dates.checkin);
        tr.hidden = !on;
        if (on) lodgingVisible += 1;
      }});
      const lodgingEmpty = document.getElementById('lodging-empty');
      if (lodgingEmpty) lodgingEmpty.hidden = lodgingVisible > 0;
      const lodgingTable = document.querySelector('.lodging-table');
      if (lodgingTable) lodgingTable.closest('.table-wrap').hidden = lodgingVisible === 0;
      updateLodgingHero(dates.checkout, dates.checkin);

      let carVisible = 0;
      document.querySelectorAll('.car-date-panel').forEach(p => {{
        const on = p.dataset.carPanel === dates.dropoff;
        p.hidden = !on;
        p.classList.toggle('active', on);
        if (on) carVisible += 1;
      }});
      document.querySelectorAll('.car-compare-table tbody tr[data-dropoff]').forEach(tr => {{
        const on = tr.dataset.dropoff === dates.dropoff;
        tr.hidden = !on;
        tr.classList.toggle('best', on);
      }});
      const carEmpty = document.getElementById('car-empty');
      if (carEmpty) carEmpty.hidden = carVisible > 0;
      showCarDate(dates.dropoff);
      updateCarHero(dates.dropoff);
    }}

    function onEndDateChange(nextEnd, opts = {{}}) {{
      const dates = getTripDates();
      dates.returnDate = firstAvailable(DATE_OPTS.return, nextEnd);
      dates.checkout = firstAvailable(DATE_OPTS.checkout, nextEnd);
      dates.dropoff = firstAvailable(DATE_OPTS.dropoff, nextEnd);
      persistTripDates(dates);

      const s = getState();
      if (!opts.keepFlight) {{
        const sameFlight = (TRIP.flights || []).filter(f => f.return_date === dates.returnDate);
        if (sameFlight.length) {{
          const current = findFlight(s.flightId);
          if (!current || current.return_date !== dates.returnDate) {{
            sameFlight.sort((a, b) => (a.price || 1e12) - (b.price || 1e12));
            s.flightId = sameFlight[0].id;
          }}
        }}
      }}
      if (!opts.keepLodging) {{
        const currentLod = findLodging(s.lodgingCheckout);
        if (!currentLod || currentLod.checkout_date !== dates.checkout) {{
          const matchedLodging = cheapestLodgingForCheckout(dates.checkout);
          if (matchedLodging) s.lodgingCheckout = matchedLodging.id;
        }}
      }}
      if (!opts.keepCar) {{
        const currentCar = findCar(s.carId);
        if (!currentCar || currentCar.dropoff_date !== dates.dropoff) {{
          const matchedCar = (TRIP.cars || [])
            .filter(c => c.dropoff_date === dates.dropoff)
            .sort((a, b) => (a.price || 1e12) - (b.price || 1e12))[0];
          if (matchedCar) {{
            s.carId = matchedCar.id;
            s.car = matchedCar.price;
            const carInput = document.getElementById('cost-car');
            if (carInput) carInput.value = matchedCar.price;
          }}
        }}
      }}
      saveState(s);
      // Re-persist dates after budget save so filters never get wiped.
      persistTripDates(dates);
      applyDateFilters();
      renderDashboard();
    }}

    function bindDateFilters() {{
      const dates = getTripDates();
      persistTripDates(dates);
      syncDateSelects(dates);

      const flightReturn = document.getElementById('flight-return');
      const lodgingCheckout = document.getElementById('lodging-checkout');
      const carDropoff = document.getElementById('car-dropoff');
      const flightOutbound = document.getElementById('flight-outbound');
      const lodgingCheckin = document.getElementById('lodging-checkin');
      const carPickup = document.getElementById('car-pickup');

      if (flightReturn) flightReturn.addEventListener('change', () => onEndDateChange(flightReturn.value));
      if (lodgingCheckout) lodgingCheckout.addEventListener('change', () => onEndDateChange(lodgingCheckout.value));
      if (carDropoff) carDropoff.addEventListener('change', () => onEndDateChange(carDropoff.value));

      const bindStart = (el, key) => {{
        if (!el) return;
        el.addEventListener('change', () => {{
          const d = getTripDates();
          d[key] = el.value;
          persistTripDates(d);
          applyDateFilters();
        }});
      }};
      bindStart(flightOutbound, 'outbound');
      bindStart(lodgingCheckin, 'checkin');
      bindStart(carPickup, 'pickup');

      applyDateFilters();
    }}

    function findFlight(id) {{
      return TRIP.flights.find(f => f.id === id) || null;
    }}

    function findLodging(idOrCheckout) {{
      return TRIP.lodging.find(l => l.id === idOrCheckout)
        || TRIP.lodging.find(l => l.checkout_date === idOrCheckout) || null;
    }}

    function findCar(id) {{
      return (TRIP.cars || []).find(c => c.id === id) || null;
    }}

    function cheapestLodgingForCheckout(checkout) {{
      const rows = TRIP.lodging.filter(l => l.checkout_date === checkout);
      if (!rows.length) return null;
      return rows.reduce((a, b) => (a.price <= b.price ? a : b));
    }}

    function getState() {{
      const saved = loadState();
      const d = TRIP.defaults;
      const dates = getTripDates();
      const flightId = findFlight(saved.flightId) ? saved.flightId : TRIP.best_flight_id;
      const carId = findCar(saved.carId) ? saved.carId : TRIP.best_car_id;
      const pickedCar = findCar(carId);
      return {{
        flightId,
        lodgingCheckout: TRIP.booked_lodging_id
          || (findLodging(saved.lodgingCheckout)
            ? saved.lodgingCheckout
            : (TRIP.best_lodging_id || TRIP.best_lodging_checkout)),
        carId,
        foodPerDay: saved.foodPerDay ?? d.food_per_day,
        car: saved.car ?? (pickedCar ? pickedCar.price : d.car_rental),
        gift: saved.gift ?? d.gifts,
        misc: saved.misc ?? d.misc,
        outbound: dates.outbound,
        returnDate: dates.returnDate,
        checkin: dates.checkin,
        checkout: dates.checkout,
        pickup: dates.pickup,
        dropoff: dates.dropoff,
      }};
    }}

    function syncRadios(state) {{
      document.querySelectorAll('.flight-pick').forEach(el => {{
        el.checked = el.value === state.flightId;
      }});
      document.querySelectorAll('.lodging-pick').forEach(el => {{
        el.checked = el.value === state.lodgingCheckout;
      }});
      document.querySelectorAll('.car-pick').forEach(el => {{
        el.checked = el.value === state.carId;
      }});
      document.querySelectorAll('.date-card').forEach(card => {{
        const checked = card.querySelector('.flight-pick:checked');
        card.classList.toggle('is-picked', !!checked);
      }});
      document.querySelectorAll('tr[data-return]').forEach(tr => {{
        tr.classList.toggle('picked-row', tr.dataset.return === (findFlight(state.flightId)?.return_date || ''));
      }});
      document.querySelectorAll('tr[data-lodging-id]').forEach(tr => {{
        tr.classList.toggle('picked-row', tr.dataset.lodgingId === state.lodgingCheckout);
      }});
    }}

    function showCarDate(drop) {{
      document.querySelectorAll('.car-date-tab').forEach(b => {{
        const on = b.dataset.carDate === drop;
        b.classList.toggle('active', on);
        b.setAttribute('aria-selected', on ? 'true' : 'false');
      }});
      document.querySelectorAll('.car-date-panel').forEach(p => {{
        p.classList.toggle('active', p.dataset.carPanel === drop);
      }});
    }}

    function readInputs() {{
      const state = getState();
      state.foodPerDay = Number(document.getElementById('food-per-day').value) || 0;
      state.car = Number(document.getElementById('cost-car').value) || 0;
      state.gift = Number(document.getElementById('cost-gift').value) || 0;
      state.misc = Number(document.getElementById('cost-misc').value) || 0;
      saveState(state);
      return state;
    }}

    function renderDashboard() {{
      const state = readInputs();
      const flight = findFlight(state.flightId);
      const lodging = findLodging(state.lodgingCheckout);
      const car = findCar(state.carId);
      const nights = lodging?.nights || 0;

      const flightAmt = flight?.price || 0;
      const lodgingAmt = lodging?.price || 0;
      const foodAmt = state.foodPerDay * nights;
      const carAmt = state.car;
      const giftAmt = state.gift;
      const miscAmt = state.misc;
      const total = flightAmt + lodgingAmt + foodAmt + carAmt + giftAmt + miscAmt;

      document.getElementById('total-budget').textContent = fmt(total);
      const flightPerPerson = flight?.price_per_person || (flightAmt ? Math.round(flightAmt / TRIP.guests) : 0);
      document.getElementById('amt-flight').textContent = fmt(flightPerPerson);
      document.getElementById('sub-flight').textContent = flight
        ? `1인당 · 4명 합계 ${{fmt(flightAmt)}}`
        : '1인당';
      document.getElementById('amt-lodging').textContent = fmt(lodgingAmt);
      document.getElementById('amt-food').textContent = fmt(foodAmt);
      document.getElementById('amt-car').textContent = fmt(carAmt);
      document.getElementById('amt-gift').textContent = fmt(giftAmt);
      document.getElementById('amt-misc').textContent = fmt(miscAmt);

      document.getElementById('detail-flight').innerHTML = flight
        ? `${{flight.source_label}} · 귀국 ${{flight.return_date}} · 1인 ${{flight.price_per_person_text || fmt(flightPerPerson)}}<br><span class="muted">${{flight.duration_text || ''}} · ${{flight.carrier_text || ''}}</span> · <a href="#" data-goto="flights">변경</a>`
        : '미선택 · <a href="#" data-goto="flights">항공권 탭에서 선택</a>';

      document.getElementById('detail-lodging').innerHTML = lodging
        ? `${{lodging.title}}<br><span class="muted">체크아웃 ${{lodging.checkout_date}} · ${{nights}}박 · ${{lodging.distance_text}}</span> · <a href="#" data-goto="lodging">변경</a>`
        : '미선택 · <a href="#" data-goto="lodging">숙박 탭에서 선택</a>';

      const carOpts = car ? ((car.options || []).slice(0, 2).join(' · ') || car.location || 'ORD') : '';
      document.getElementById('detail-car').innerHTML = car
        ? `${{car.source_label || ''}} · ${{car.category}} · ${{car.model}} · ${{fmt(carAmt)}}<br><span class="muted">${{car.pickup_date}}~${{car.dropoff_date}} · ${{carOpts}}</span> · <a href="#" data-goto="cars">변경</a>`
        : '미선택 · <a href="#" data-goto="cars">렌트카 탭에서 선택</a>';

      document.getElementById('food-calc').textContent = `${{nights}}박 × ${{fmt(state.foodPerDay)}}/일 = ${{fmt(foodAmt)}}`;

      const schedule = flight && lodging
        ? `${{TRIP.outbound}} 도착 · 숙박 ${{TRIP.checkin}}~${{lodging.checkout_date}}`
        : (flight ? `${{TRIP.outbound}} → ${{flight.return_date}}` : '-');
      document.getElementById('dash-schedule').textContent = schedule;
      document.getElementById('dash-nights').textContent = nights ? `${{nights}}박` : '-';

      const mismatch = flight && lodging && flight.return_date !== lodging.checkout_date;
      document.getElementById('trip-summary').textContent = mismatch
        ? '⚠️ 항공 귀국일과 숙박 체크아웃이 다릅니다. 일정을 맞추면 더 정확합니다.'
        : (total ? `항공 4명 ${{fmt(flightAmt)}} + 숙박 ${{fmt(lodgingAmt)}} + 식비·렌트·선물·기타 ${{fmt(total - flightAmt - lodgingAmt)}}` : '항공권과 숙박을 선택하세요.');

      const items = [
        ['항공권 (4명)', flightAmt, 'flight'],
        ['숙박', lodgingAmt, 'lodging'],
        ['식비', foodAmt, 'food'],
        ['자동차 렌트', carAmt, 'car'],
        ['선물비', giftAmt, 'gift'],
        ['기타 여행비', miscAmt, 'misc'],
      ].filter(([, amt]) => amt > 0);

      document.getElementById('breakdown-body').innerHTML = items.map(([label, amt, key]) => `
        <tr>
          <td>${{label}}</td>
          <td><strong>${{fmt(amt)}}</strong></td>
          <td>${{pct(amt, total)}}%</td>
          <td><span class="dot" style="background:${{COLORS[key]}}"></span></td>
        </tr>`).join('');

      document.getElementById('bar-chart').innerHTML = items.map(([label, amt, key]) => `
        <div class="bar-row">
          <div class="bar-label">${{label}}</div>
          <div class="bar-track"><div class="bar-fill" style="width:${{pct(amt, total)}}%;background:${{COLORS[key]}}"></div></div>
          <div>${{pct(amt, total)}}%</div>
        </div>`).join('');

      syncRadios(state);
      bindGotoLinks();
    }}

    function bindGotoLinks() {{
      document.querySelectorAll('[data-goto]').forEach(a => {{
        a.onclick = e => {{
          e.preventDefault();
          const panel = a.dataset.goto;
          document.querySelector(`[data-panel="${{panel}}"]`).click();
        }};
      }});
    }}

    function initBudget() {{
      const state = getState();
      document.getElementById('food-per-day').value = state.foodPerDay;
      document.getElementById('cost-car').value = state.car;
      document.getElementById('cost-gift').value = state.gift;
      document.getElementById('cost-misc').value = state.misc;

      bindDateFilters();

      document.querySelectorAll('.flight-pick').forEach(el => {{
        el.addEventListener('change', () => {{
          const s = getState();
          s.flightId = el.value;
          saveState(s);
          const fl = findFlight(s.flightId);
          if (fl?.return_date) onEndDateChange(fl.return_date, {{ keepFlight: true }});
          else renderDashboard();
        }});
      }});

      document.querySelectorAll('.lodging-pick').forEach(el => {{
        el.addEventListener('change', () => {{
          const s = getState();
          s.lodgingCheckout = el.value;
          saveState(s);
          const lod = findLodging(s.lodgingCheckout);
          if (lod?.checkout_date) onEndDateChange(lod.checkout_date, {{ keepLodging: true }});
          else renderDashboard();
        }});
      }});

      document.querySelectorAll('.car-pick').forEach(el => {{
        el.addEventListener('change', () => {{
          const s = getState();
          s.carId = el.value;
          const picked = findCar(s.carId);
          if (picked) {{
            s.car = picked.price;
            document.getElementById('cost-car').value = picked.price;
            saveState(s);
            onEndDateChange(picked.dropoff_date, {{ keepCar: true }});
          }} else {{
            saveState(s);
            renderDashboard();
          }}
        }});
      }});

      document.querySelectorAll('.car-date-tab').forEach(btn => {{
        btn.addEventListener('click', () => onEndDateChange(btn.dataset.carDate));
      }});

      ['food-per-day', 'cost-car', 'cost-gift', 'cost-misc'].forEach(id => {{
        document.getElementById(id).addEventListener('input', renderDashboard);
      }});

      document.querySelectorAll('.combo-apply').forEach(btn => {{
        btn.addEventListener('click', () => {{
          const s = getState();
          s.flightId = btn.dataset.flight;
          s.lodgingCheckout = btn.dataset.lodging;
          const matchedCar = (TRIP.cars || []).filter(c => c.dropoff_date === findFlight(s.flightId)?.return_date)
            .sort((a, b) => a.price - b.price)[0];
          if (matchedCar) {{
            s.carId = matchedCar.id;
            s.car = matchedCar.price;
            document.getElementById('cost-car').value = matchedCar.price;
          }}
          saveState(s);
          const fl = findFlight(s.flightId);
          if (fl?.return_date) onEndDateChange(fl.return_date);
          else renderDashboard();
        }});
      }});

      renderDashboard();
      const selected = findFlight(getState().flightId);
      if (selected?.route) showRoute(selected.route);
      applyDateFilters();
    }}

    function showRoute(route) {{
      document.querySelectorAll('.route-tab').forEach(b => {{
        const on = b.dataset.route === route;
        b.classList.toggle('active', on);
        b.setAttribute('aria-selected', on ? 'true' : 'false');
      }});
      document.querySelectorAll('.route-panel').forEach(p => {{
        p.classList.toggle('active', p.dataset.routePanel === route);
      }});
    }}

    document.querySelectorAll('.tab').forEach(btn => {{
      btn.addEventListener('click', () => {{
        document.querySelectorAll('.tab').forEach(b => {{
          b.classList.remove('active');
          b.setAttribute('aria-selected', 'false');
        }});
        document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        btn.setAttribute('aria-selected', 'true');
        document.getElementById(btn.dataset.panel).classList.add('active');
        if (btn.dataset.panel === 'dashboard') renderDashboard();
      }});
    }});

    document.querySelectorAll('.route-tab').forEach(btn => {{
      btn.addEventListener('click', () => showRoute(btn.dataset.route));
    }});

    function showEast(city) {{
      document.querySelectorAll('.east-tab').forEach(b => {{
        const on = b.dataset.east === city;
        b.classList.toggle('active', on);
        b.setAttribute('aria-selected', on ? 'true' : 'false');
      }});
      document.querySelectorAll('.east-panel').forEach(p => {{
        p.classList.toggle('active', p.dataset.eastPanel === city);
      }});
    }}
    document.querySelectorAll('.east-tab').forEach(btn => {{
      btn.addEventListener('click', () => showEast(btn.dataset.east));
    }});

    const hashPanel = {{
      '#dashboard': 'dashboard', '#flights': 'flights', '#lodging': 'lodging', '#cars': 'cars',
      '#chi-plan': 'chi-plan', '#east-plan': 'east-plan'
    }}[location.hash];
    if (hashPanel) document.querySelector(`[data-panel="${{hashPanel}}"]`).click();

    initBudget();
  </script>
</body>
</html>"""


def main() -> None:
    now_kst = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S KST")
    chi_days = load_route_rows(ROUTE_CHI_FILE)
    nyc_days = load_route_rows(ROUTE_NYC_FILE)
    car_days = load_route_rows(CAR_COMPARE_FILE) or load_route_rows(CAR_FILE)
    route_flights = flatten_route_flights(nyc_days) + flatten_route_flights(chi_days)
    route_flights.sort(key=lambda x: (x["price"], x.get("duration_minutes") or 10**9))
    airbnb_all = load_lodging_list(AIRBNB_LODGING)
    airbnb = load_lodging_cheapest(airbnb_all)
    trip_data = build_trip_data(route_flights, airbnb_all, airbnb, car_days)
    flights_html = render_flights(chi_days, nyc_days)
    lodging_html = render_lodging(airbnb_all, airbnb)
    cars_html = render_cars(car_days)
    chicago_plan_html = itinerary_plans.render_chicago_plan()
    east_plan_html = itinerary_plans.render_east_plan()
    combo_html = render_combo_analysis(trip_data.get("combos", []))
    dashboard_html = render_dashboard_shell(combo_html)
    page = render_page(
        flights_html,
        lodging_html,
        cars_html,
        chicago_plan_html,
        east_plan_html,
        dashboard_html,
        trip_data,
        now_kst,
    )
    HTML.write_text(page, encoding="utf-8")
    INDEX_HTML.write_text(page, encoding="utf-8")
    DOCS_INDEX.parent.mkdir(parents=True, exist_ok=True)
    DOCS_INDEX.write_text(page, encoding="utf-8")
    print(f"Wrote {HTML}")
    print(f"Wrote {INDEX_HTML}")
    print(f"Wrote {DOCS_INDEX}")
    print(f"Route flights: {len(route_flights)} · cars: {len(trip_data.get('cars') or [])}")


if __name__ == "__main__":
    main()
