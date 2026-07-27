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
AIRBNB_LODGING = ROOT / "airbnb_lodging_data.json"

ADULTS = 2
CHILD_AGES = [7, 8]
OUTBOUND = "2026-09-23"
CHECKIN = "2026-09-23"
GUESTS = ADULTS + len(CHILD_AGES)

FLIGHT_LABELS = {"sky": "Skyscanner", "kayak": "KAYAK", "google": "Google"}

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


def load_list(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def load_flights(path: Path) -> dict[str, dict]:
    return {row["return_date"]: row for row in load_list(path)}


def load_lodging(path: Path) -> dict[str, dict]:
    return {row["checkout_date"]: row for row in load_list(path)}


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


def lodging_pick_cell(a: dict, cheapest: int | None) -> str:
    checkout = a["checkout_date"]
    return f"""
          <td>
            <label class="pick-label lodging-pick-label">
              <input type="radio" name="lodging-pick" class="lodging-pick" value="{checkout}"
                data-price="{a.get('price', 0)}" data-nights="{a.get('nights', 0)}">
              <span>{'★' if a.get('price') == cheapest else '선택'}</span>
            </label>
          </td>"""


def build_trip_data(sky: dict, kayak: dict, google: dict, airbnb: dict) -> dict:
    flights = []
    dates = sorted(set(sky) | set(kayak) | set(google))
    for ret in dates:
        for source, row in (("sky", sky.get(ret)), ("kayak", kayak.get(ret)), ("google", google.get(ret))):
            if row and row.get("price") is not None:
                flights.append(
                    {
                        "id": f"{source}:{ret}",
                        "source": source,
                        "source_label": FLIGHT_LABELS[source],
                        "return_date": ret,
                        "price": row["price"],
                        "price_text": row["price_text"],
                        "price_per_person": flight_per_person(row["price"]),
                        "price_per_person_text": flight_per_person_text(row["price"]),
                        "duration_text": row.get("duration_text", ""),
                        "carrier_text": row.get("carrier_text", ""),
                        "seller_url": row.get("seller_url", ""),
                    }
                )
    flights.sort(key=lambda x: x["price"])

    lodging = []
    for a in sorted(airbnb.values(), key=lambda x: x.get("price") or 10**12):
        lodging.append(
            {
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
    best_lodging = lodging[0] if lodging else None
    if best_flight and best_lodging:
        matched = next((l for l in lodging if l["checkout_date"] == best_flight["return_date"]), None)
        if matched:
            best_lodging = matched

    return {
        "outbound": OUTBOUND,
        "checkin": CHECKIN,
        "guests": GUESTS,
        "defaults": {
            "food_per_day": DEFAULT_FOOD_PER_DAY,
            "car_rental": DEFAULT_CAR_RENTAL,
            "gifts": DEFAULT_GIFTS,
            "misc": DEFAULT_MISC,
        },
        "flights": flights,
        "lodging": lodging,
        "best_flight_id": best_flight["id"] if best_flight else None,
        "best_lodging_checkout": best_lodging["checkout_date"] if best_lodging else None,
    }


def render_flights(sky: dict, kayak: dict, google: dict) -> str:
    dates = sorted(set(sky) | set(kayak) | set(google))
    merged = []
    for ret in dates:
        s, k, g = sky.get(ret), kayak.get(ret), google.get(ret)
        sp = s.get("price") if s else None
        kp = k.get("price") if k else None
        gp = g.get("price") if g else None
        merged.append((ret, sp, kp, gp, winner_label({"sky": sp, "kayak": kp, "google": gp}, FLIGHT_LABELS), s, k, g))

    merged.sort(key=lambda x: min_price(x[1], x[2], x[3]) or 10**12)

    candidates = []
    for label, row in (("Skyscanner", merged[0][5]), ("KAYAK", merged[0][6]), ("Google", merged[0][7])):
        if row:
            candidates.append((label, row))
    candidates.sort(key=lambda x: x[1]["price"])
    overall = candidates[0] if candidates else ("", None)

    rows = []
    for i, (ret, sp, kp, gp, winner, s, k, g) in enumerate(merged):
        cheapest = min_price(sp, kp, gp)
        rows.append(f"""
        <tr class="{'best' if i == 0 else ''}" data-return="{ret}">
          <td>{'★' if i == 0 else ''}</td>
          <td><strong>{ret}</strong></td>
          {flight_pick_cell('sky', ret, s, cheapest)}
          {flight_pick_cell('kayak', ret, k, cheapest)}
          {flight_pick_cell('google', ret, g, cheapest)}
          <td><strong>{winner}</strong></td>
        </tr>""")

    hero = ""
    if overall[1]:
        src, o = overall
        color = {"Skyscanner": "var(--sky)", "KAYAK": "var(--kayak)", "Google": "var(--google)"}.get(src, "var(--sky)")
        hero = f"""
        <section class="hero card">
          <h2>전체 최저가 ({src})</h2>
          <p class="hero-price" style="color:{color}">{flight_per_person_text(o['price'])}</p>
          <p class="muted">1인당 · 4명 합계 {o['price_text']}</p>
          <p>출발 {OUTBOUND} · 귀국 {o['return_date']}</p>
          <p>{o.get('duration_text','')}</p>
          <p>{o.get('carrier_text','')}</p>
          {BTN.format(url=o['seller_url'])}
          <p class="muted" style="margin-top:10px;">아래 가격 옆 라디오 버튼으로 여행경비에 담을 항공권을 선택하세요.</p>
        </section>"""

    return f"""
    {hero}
    <section class="card">
      <div class="legend">
        <span><i class="dot" style="background:var(--sky)"></i> Skyscanner</span>
        <span><i class="dot" style="background:var(--kayak)"></i> KAYAK</span>
        <span><i class="dot" style="background:var(--google)"></i> Google Flights</span>
      </div>
      <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th rowspan="2"></th><th rowspan="2">귀국일</th>
            <th colspan="4" class="sky">Skyscanner</th>
            <th colspan="4" class="kayak">KAYAK</th>
            <th colspan="4" class="google">Google Flights</th>
            <th rowspan="2">최저</th>
          </tr>
          <tr>
            <th class="sky">1인당·선택</th><th class="sky">비행</th><th class="sky">항공사</th><th class="sky">예약</th>
            <th class="kayak">1인당·선택</th><th class="kayak">비행</th><th class="kayak">항공사</th><th class="kayak">예약</th>
            <th class="google">1인당·선택</th><th class="google">비행</th><th class="google">항공사</th><th class="google">예약</th>
          </tr>
        </thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
      </div>
      <p class="muted" style="margin-top:12px;">※ 항공권 가격은 1인당(성인·어린이 동일 적용) · 4명 일행 합계는 여행경비 탭에 반영 · ○ 선택으로 담기</p>
    </section>"""


def render_lodging(airbnb: dict[str, dict]) -> str:
    merged = sorted(airbnb.values(), key=lambda x: x.get("price") or 10**12)
    best = merged[0] if merged else None

    hero = ""
    if best:
        hero = f"""
        <section class="hero card">
          <h2>숙박 최저가 (Airbnb)</h2>
          <p class="hero-price" style="color:var(--airbnb)">{best['price_text']}</p>
          <p>체크인 {CHECKIN} · 체크아웃 {best['checkout_date']} · {best.get('nights','')}박</p>
          <p>{best.get('title','')}</p>
          <p>{best.get('distance_text','')} · {best.get('amenities_text','')}</p>
          {BTN.format(url=best['seller_url'])}
          <p class="muted" style="margin-top:10px;">아래 ○ 선택으로 여행경비에 담을 숙소를 고르세요.</p>
        </section>"""

    rows = []
    cheapest = best.get("price") if best else None
    for i, a in enumerate(merged):
        row_cls = "best" if i == 0 else ""
        rows.append(f"""
        <tr class="{row_cls}" data-checkout="{a['checkout_date']}">
          {lodging_pick_cell(a, cheapest)}
          <td>{a['checkout_date']}<br><span class="muted">{a.get('nights','')}박</span></td>
          <td class="price airbnb{price_cls(a.get('price'), cheapest)}">{a['price_text']}</td>
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
        ※ 시카고대 근처 · 주방 포함 · 집 전체 · 게스트 4명 · 귀국일과 체크아웃을 맞추면 일정이 깔끔합니다.
      </p>
    </section>"""


def render_dashboard_shell() -> str:
    return """
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
      --bg: #f1f2f8; --card: #fff; --text: #161616; --muted: #626971;
      --best: #e8f4fd; --highlight: #fff8e1; --picked: #e7f7f0;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: "Segoe UI", "Noto Sans KR", sans-serif; background: var(--bg); color: var(--text); }}
    .wrap {{ max-width: 1400px; margin: 0 auto; padding: 24px; }}
    h1 {{ margin: 0 0 8px; font-size: 1.75rem; }}
    h3 {{ margin: 0 0 12px; font-size: 1.05rem; }}
    .meta {{ color: var(--muted); font-size: 0.95rem; margin-bottom: 16px; }}
    .tabs {{ display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; }}
    .tab {{
      border: none; background: #dde1e8; color: var(--text);
      padding: 12px 24px; border-radius: 999px; font-size: 1rem; font-weight: 600; cursor: pointer;
    }}
    .tab.active {{ background: #222; color: #fff; }}
    .panel {{ display: none; }}
    .panel.active {{ display: block; }}
    .card {{ background: var(--card); border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,.06); margin-bottom: 20px; }}
    .hero {{ text-align: center; }}
    .hero-price {{ font-size: 2rem; font-weight: 700; margin: 8px 0; }}
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
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>서울 → 시카고(ORD) 여행경비</h1>
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
      <p class="meta">출발 {OUTBOUND} · 귀국 10/8~10/13 · Skyscanner · KAYAK · Google Flights</p>
      {flights_html}
    </div>

    <div id="lodging" class="panel" role="tabpanel">
      <p class="meta">체크인 {CHECKIN} · 체크아웃 10/8~10/13 · 시카고대 근처 · 주방 포함 · 집 전체</p>
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
    const STORE_KEY = 'chicago-trip-budget-v1';

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

    function findLodging(checkout) {{
      return TRIP.lodging.find(l => l.checkout_date === checkout) || null;
    }}

    function getState() {{
      const saved = loadState();
      const d = TRIP.defaults;
      return {{
        flightId: saved.flightId || TRIP.best_flight_id,
        lodgingCheckout: saved.lodgingCheckout || TRIP.best_lodging_checkout,
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
      document.querySelectorAll('tr[data-return]').forEach(tr => {{
        tr.classList.toggle('picked-row', tr.dataset.return === (findFlight(state.flightId)?.return_date || ''));
      }});
      document.querySelectorAll('tr[data-checkout]').forEach(tr => {{
        tr.classList.toggle('picked-row', tr.dataset.checkout === state.lodgingCheckout);
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
        ? `${{flight.source_label}} · 귀국 ${{flight.return_date}} · 1인 ${{flight.price_per_person_text || fmt(flightPerPerson)}}<br><span class="muted">${{flight.carrier_text}}</span> · <a href="#" data-goto="flights">변경</a>`
        : '미선택 · <a href="#" data-goto="flights">항공권 탭에서 선택</a>';

      document.getElementById('detail-lodging').innerHTML = lodging
        ? `${{lodging.title}}<br><span class="muted">체크아웃 ${{lodging.checkout_date}} · ${{nights}}박 · ${{lodging.distance_text}}</span> · <a href="#" data-goto="lodging">변경</a>`
        : '미선택 · <a href="#" data-goto="lodging">숙박 탭에서 선택</a>';

      document.getElementById('food-calc').textContent = `${{nights}}박 × ${{fmt(state.foodPerDay)}}/일 = ${{fmt(foodAmt)}}`;

      const schedule = flight && lodging
        ? `${{TRIP.outbound}} → ${{lodging.checkout_date}}`
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
            const matched = findLodging(fl.return_date);
            if (matched) s.lodgingCheckout = matched.checkout_date;
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

      renderDashboard();
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

    const hashPanel = {{ '#dashboard': 'dashboard', '#flights': 'flights', '#lodging': 'lodging' }}[location.hash];
    if (hashPanel) document.querySelector(`[data-panel="${{hashPanel}}"]`).click();

    initBudget();
  </script>
</body>
</html>"""


def main() -> None:
    now_kst = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S KST")
    sky = load_flights(SKY_FILE)
    kayak = load_flights(KAYAK_FILE)
    google = load_flights(GOOGLE_FILE)
    airbnb = load_lodging(AIRBNB_LODGING)
    trip_data = build_trip_data(sky, kayak, google, airbnb)
    flights_html = render_flights(sky, kayak, google)
    lodging_html = render_lodging(airbnb)
    dashboard_html = render_dashboard_shell()
    page = render_page(flights_html, lodging_html, dashboard_html, trip_data, now_kst)
    HTML.write_text(page, encoding="utf-8")
    INDEX_HTML.write_text(page, encoding="utf-8")
    DOCS_INDEX.parent.mkdir(parents=True, exist_ok=True)
    DOCS_INDEX.write_text(page, encoding="utf-8")
    print(f"Wrote {HTML}")
    print(f"Wrote {INDEX_HTML}")
    print(f"Wrote {DOCS_INDEX}")


if __name__ == "__main__":
    main()
