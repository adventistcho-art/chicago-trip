#!/usr/bin/env python3
"""Build tabbed travel page: budget dashboard + flights + lodging."""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

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
AIRBNB_LODGING = ROOT / "airbnb_lodging_data.json"

ADULTS = 2
CHILD_AGES = [7, 8]
OUTBOUND = "2026-09-23"
CHECKIN = "2026-09-26"
LODGING_NOTE = "9/23 도착 · Airbnb 9/26부터"
GUESTS = ADULTS + len(CHILD_AGES)

FLIGHT_LABELS = {"sky": "Skyscanner", "kayak": "KAYAK", "google": "Google"}
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
            kind_label = "최저가" if kind == "cheapest" else "최단시간"
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
    return f"""
          <td>
            <label class="pick-label lodging-pick-label">
              <input type="radio" name="lodging-pick" class="lodging-pick" value="{lid}"
                data-checkout="{a['checkout_date']}"
                data-price="{a.get('price', 0)}" data-nights="{a.get('nights', 0)}">
              <span>{'★' if is_best else '선택'}</span>
            </label>
          </td>"""


def build_trip_data(
    route_flights: list[dict],
    airbnb_all: list[dict],
    airbnb: dict[str, dict],
) -> dict:
    flights = list(route_flights)

    lodging = []
    for a in sorted(airbnb_all, key=lambda x: (x.get("checkout_date", ""), x.get("price") or 10**12)):
        lodging.append(
            {
                "id": lodging_id(a),
                "checkout_date": a["checkout_date"],
                "nights": a.get("nights", 0),
                "price": a.get("price"),
                "price_text": a.get("price_text", ""),
                "title": a.get("title", ""),
                "distance_text": a.get("distance_text", ""),
                "seller_url": a.get("seller_url", ""),
            }
        )

    best_flight = flights[0] if flights else None
    cheapest_rows = sorted(airbnb.values(), key=lambda x: x.get("price") or 10**12)
    best_lodging = lodging[0] if lodging else None
    for row in lodging:
        if cheapest_rows and row["id"] == lodging_id(cheapest_rows[0]):
            best_lodging = row
            break
    combos = analyze_combos(flights, airbnb)
    recommended = combos[0] if combos else None
    if recommended:
        best_flight_id = recommended["flight_id"]
        best_lodging_id = recommended.get("lodging_id") or recommended["lodging_checkout"]
    else:
        best_flight_id = best_flight["id"] if best_flight else None
        best_lodging_id = best_lodging["id"] if best_lodging else None
        if best_flight and best_lodging:
            matched = next((l for l in lodging if l["checkout_date"] == best_flight["return_date"]), None)
            if matched:
                best_lodging_id = matched["id"]

    return {
        "outbound": OUTBOUND,
        "checkin": CHECKIN,
        "lodging_note": LODGING_NOTE,
        "guests": GUESTS,
        "defaults": {
            "food_per_day": DEFAULT_FOOD_PER_DAY,
            "car_rental": DEFAULT_CAR_RENTAL,
            "gifts": DEFAULT_GIFTS,
            "misc": DEFAULT_MISC,
        },
        "flights": flights,
        "lodging": lodging,
        "combos": combos,
        "recommended": recommended,
        "best_flight_id": best_flight_id,
        "best_lodging_id": best_lodging_id,
        "best_lodging_checkout": best_lodging_id,
    }


def _fmt_date_ko(iso: str) -> str:
    _y, m, d = iso.split("-")
    return f"{int(m)}월 {int(d)}일"


def _opt_card(flight_id: str, opt: dict | None, kind: str, route: str, ret: str) -> str:
    if not opt:
        return f"""
        <article class="opt-card opt-{kind} is-empty">
          <header class="opt-head"><span class="opt-badge">{'최저가' if kind == 'cheapest' else '최단시간'}</span></header>
          <p class="muted">데이터 없음</p>
        </article>"""
    badge = "💰 최저가" if kind == "cheapest" else "⚡ 최단시간"
    note = '<span class="pill warn">자가환승</span>' if opt.get("self_transfer") else ""
    return f"""
    <article class="opt-card opt-{kind}">
      <header class="opt-head">
        <span class="opt-badge">{badge}</span>
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
        </section>""")

    return f"""
    <div class="route-panel {'active' if active else ''}" data-route-panel="{route_key}" role="tabpanel">
      <section class="route-hero card">
        <div class="route-hero-copy">
          <p class="route-kicker">{meta['chip']}</p>
          <h2>{meta['label']}</h2>
          <p class="muted">{meta['blurb']} · KAYAK 1인 기준 · 일정별 최저가 / 최단시간</p>
        </div>
        <div class="route-stats">{''.join(hero_bits)}</div>
      </section>
      <div class="date-stack">{''.join(day_cards)}</div>
    </div>"""


def render_flights(chi_days: list[dict], nyc_days: list[dict]) -> str:
    return f"""
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
    <p class="flight-hint muted">귀국일별로 <strong>최저가</strong>와 <strong>최단시간</strong>을 나란히 비교합니다. ○ 경비에 담기 → 여행경비 탭에 반영됩니다.</p>
    {_route_panel("nyc_in", nyc_days, True)}
    {_route_panel("chi_round", chi_days, False)}
    """


def render_lodging(airbnb_all: list[dict], airbnb: dict[str, dict]) -> str:
    merged = sorted(airbnb_all, key=lambda x: (x.get("checkout_date", ""), x.get("price") or 10**12))
    cheapest_by_date = {co: row.get("price") for co, row in airbnb.items()}
    best = airbnb.get("2026-10-08") or (sorted(airbnb.values(), key=lambda x: x.get("price") or 10**12)[0] if airbnb else None)

    hero = ""
    if best:
        hero = f"""
        <section class="hero card">
          <h2>숙박 후보 (Airbnb 검색 · 주방·집 전체)</h2>
          <p class="hero-price" style="color:var(--airbnb)">{best['price_text']}</p>
          <p>체크인 {CHECKIN} · 체크아웃 {best['checkout_date']} · {best.get('nights','')}박 · 해당일 최저</p>
          <p>{best.get('title','')}</p>
          <p>{best.get('distance_text','')} · {best.get('amenities_text','')}</p>
          {BTN.format(url=best['seller_url'])}
          <p class="muted" style="margin-top:10px;">아래 표에 체크아웃별 후보(최대 8곳) · ○ 선택으로 여행경비에 반영</p>
        </section>"""

    rows = []
    for i, a in enumerate(merged):
        co = a["checkout_date"]
        is_best = a.get("price") == cheapest_by_date.get(co)
        row_cls = "best" if is_best else ""
        lid = lodging_id(a)
        rows.append(f"""
        <tr class="{row_cls}" data-checkout="{co}" data-lodging-id="{lid}">
          {lodging_pick_cell(a, is_best)}
          <td>{co}<br><span class="muted">{a.get('nights','')}박</span></td>
          <td class="price airbnb{price_cls(a.get('price'), cheapest_by_date.get(co) if is_best else None)}">{a['price_text']}</td>
          <td>{a.get('title','-')}<br><span class="muted">{a.get('location_text','')}</span></td>
          <td><strong>{a.get('distance_text','-')}</strong></td>
          <td>{a.get('amenities_text','-')}</td>
          <td>{BTN.format(url=a['seller_url'])}</td>
        </tr>""")

    return f"""
    {hero}
    <section class="card">
      <div class="legend">
        <span><i class="dot" style="background:var(--airbnb)"></i> Airbnb · 시카고대(University of Chicago) 기준 거리</span>
      </div>
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
        ※ {LODGING_NOTE} · 체크인 {CHECKIN} · 시카고대 인근 · 주방 · 집 전체 · 4명<br>
        ※ 체크아웃(귀국일)별 주방 있는 집 전체 후보 · 3시간마다 갱신
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
        <label class="field-label" for="cost-car">렌트 총액</label>
        <input id="cost-car" type="number" min="0" step="10000" class="cost-input">
        <p class="dash-amount" id="amt-car">₩0</p>
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
        ※ 항공권·숙박은 각 탭에서 선택한 값이 자동 반영됩니다. 식비·렌트·선물·기타는 직접 수정 가능하며 브라우저에 저장됩니다.
      </p>
    </section>"""


def render_page(flights_html: str, lodging_html: str, dashboard_html: str, trip_data: dict, now_kst: str) -> str:
    trip_json = json.dumps(trip_data, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="refresh" content="{REFRESH_SECONDS}">
  <title>서울→시카고 여행경비 | 항공권 · 숙박 · 대시보드</title>
  <style>
    :root {{
      --sky: #0770e3; --kayak: #ff690f; --google: #1a73e8;
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
    .date-stack {{ display: grid; gap: 16px; }}
    .date-card {{
      background: var(--card); border: 1px solid var(--line); border-radius: 18px; padding: 18px;
      box-shadow: 0 6px 18px rgba(24,33,50,.05);
    }}
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
    th.airbnb {{ color: var(--airbnb); border-top: 3px solid var(--airbnb); }}
    tr.best {{ background: var(--best); }}
    tr.picked-row {{ background: var(--picked) !important; }}
    .price {{ font-weight: 700; }}
    .price.sky {{ color: var(--sky); }}
    .price.kayak {{ color: var(--kayak); }}
    .price.google {{ color: var(--google); }}
    .price.airbnb {{ color: var(--airbnb); }}
    .price.highlight {{ background: var(--highlight); border-radius: 4px; }}
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
      .route-switch, .opt-grid {{ grid-template-columns: 1fr; }}
      .route-hero {{ padding: 18px; }}
      .opt-price {{ font-size: 1.35rem; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>서울 → 시카고 여행경비</h1>
      <p class="meta">
        성인 {ADULTS}명 · 유소아 {len(CHILD_AGES)}명 (만 {CHILD_AGES[0]}·{CHILD_AGES[1]}세) · 동기화: {now_kst} · {REFRESH_HOURS}시간마다 자동 갱신
      </p>
      <nav class="tabs" role="tablist">
        <button class="tab active" role="tab" aria-selected="true" data-panel="dashboard">💰 여행경비</button>
        <button class="tab" role="tab" aria-selected="false" data-panel="flights">✈️ 항공권</button>
        <button class="tab" role="tab" aria-selected="false" data-panel="lodging">🏠 숙박</button>
      </nav>
    </header>

    <div id="dashboard" class="panel active" role="tabpanel">
      <p class="meta">선택한 항공권·숙박 + 식비·렌트·선물·기타 = 총 여행경비</p>
      {dashboard_html}
    </div>

    <div id="flights" class="panel" role="tabpanel">
      <p class="meta">출발 {OUTBOUND} · 귀국 10/8~10/13 · 루트별 최저가 / 최단시간 · {LODGING_NOTE}</p>
      {flights_html}
    </div>

    <div id="lodging" class="panel" role="tabpanel">
      <p class="meta">체크인 {CHECKIN} · 체크아웃 10/8~10/13 · 시카고대 · 주방 · 집 전체</p>
      {lodging_html}
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
    const STORE_KEY = 'chicago-trip-budget-v3';

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
      localStorage.setItem(STORE_KEY, JSON.stringify(state));
    }}

    function findFlight(id) {{
      return TRIP.flights.find(f => f.id === id) || null;
    }}

    function findLodging(idOrCheckout) {{
      return TRIP.lodging.find(l => l.id === idOrCheckout)
        || TRIP.lodging.find(l => l.checkout_date === idOrCheckout) || null;
    }}

    function cheapestLodgingForCheckout(checkout) {{
      const rows = TRIP.lodging.filter(l => l.checkout_date === checkout);
      if (!rows.length) return null;
      return rows.reduce((a, b) => (a.price <= b.price ? a : b));
    }}

    function getState() {{
      const saved = loadState();
      const d = TRIP.defaults;
      const flightId = findFlight(saved.flightId) ? saved.flightId : TRIP.best_flight_id;
      return {{
        flightId,
        lodgingCheckout: findLodging(saved.lodgingCheckout)
          ? saved.lodgingCheckout
          : (TRIP.best_lodging_id || TRIP.best_lodging_checkout),
        foodPerDay: saved.foodPerDay ?? d.food_per_day,
        car: saved.car ?? d.car_rental,
        gift: saved.gift ?? d.gifts,
        misc: saved.misc ?? d.misc,
      }};
    }}

    function syncRadios(state) {{
      document.querySelectorAll('.flight-pick').forEach(el => {{
        el.checked = el.value === state.flightId;
      }});
      document.querySelectorAll('.lodging-pick').forEach(el => {{
        el.checked = el.value === state.lodgingCheckout;
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

      document.querySelectorAll('.flight-pick').forEach(el => {{
        el.addEventListener('change', () => {{
          const s = getState();
          s.flightId = el.value;
          saveState(s);
          const lod = findLodging(s.lodgingCheckout);
          const fl = findFlight(s.flightId);
          if (fl && lod && lod.checkout_date !== fl.return_date) {{
            const matched = cheapestLodgingForCheckout(fl.return_date);
            if (matched) s.lodgingCheckout = matched.id;
          }}
          saveState(s);
          renderDashboard();
        }});
      }});

      document.querySelectorAll('.lodging-pick').forEach(el => {{
        el.addEventListener('change', () => {{
          const s = getState();
          s.lodgingCheckout = el.value;
          saveState(s);
          renderDashboard();
        }});
      }});

      ['food-per-day', 'cost-car', 'cost-gift', 'cost-misc'].forEach(id => {{
        document.getElementById(id).addEventListener('input', renderDashboard);
      }});

      document.querySelectorAll('.combo-apply').forEach(btn => {{
        btn.addEventListener('click', () => {{
          const s = getState();
          s.flightId = btn.dataset.flight;
          s.lodgingCheckout = btn.dataset.lodging;
          saveState(s);
          renderDashboard();
        }});
      }});

      renderDashboard();
      const selected = findFlight(getState().flightId);
      if (selected?.route) showRoute(selected.route);
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

    const hashPanel = {{ '#dashboard': 'dashboard', '#flights': 'flights', '#lodging': 'lodging' }}[location.hash];
    if (hashPanel) document.querySelector(`[data-panel="${{hashPanel}}"]`).click();

    initBudget();
  </script>
</body>
</html>"""


def main() -> None:
    now_kst = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S KST")
    chi_days = load_route_rows(ROUTE_CHI_FILE)
    nyc_days = load_route_rows(ROUTE_NYC_FILE)
    route_flights = flatten_route_flights(nyc_days) + flatten_route_flights(chi_days)
    route_flights.sort(key=lambda x: (x["price"], x.get("duration_minutes") or 10**9))
    airbnb_all = load_lodging_list(AIRBNB_LODGING)
    airbnb = load_lodging_cheapest(airbnb_all)
    trip_data = build_trip_data(route_flights, airbnb_all, airbnb)
    flights_html = render_flights(chi_days, nyc_days)
    lodging_html = render_lodging(airbnb_all, airbnb)
    combo_html = render_combo_analysis(trip_data.get("combos", []))
    dashboard_html = render_dashboard_shell(combo_html)
    page = render_page(flights_html, lodging_html, dashboard_html, trip_data, now_kst)
    HTML.write_text(page, encoding="utf-8")
    INDEX_HTML.write_text(page, encoding="utf-8")
    DOCS_INDEX.parent.mkdir(parents=True, exist_ok=True)
    DOCS_INDEX.write_text(page, encoding="utf-8")
    print(f"Wrote {HTML}")
    print(f"Wrote {INDEX_HTML}")
    print(f"Wrote {DOCS_INDEX}")
    print(f"Route flights: {len(route_flights)}")


if __name__ == "__main__":
    main()
