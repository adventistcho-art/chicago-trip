#!/usr/bin/env python3
"""Build tabbed flights.html: flights (Skyscanner/KAYAK/Google) + lodging (Airbnb)."""

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

FLIGHT_LABELS = {"sky": "Skyscanner", "kayak": "KAYAK", "google": "Google"}

BTN = """
<a class="cta-link" href="{url}" target="_blank" rel="noopener noreferrer">
  <button type="button" class="cta-btn">선택하기</button>
</a>"""


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


def render_flights(sky: dict, kayak: dict, google: dict) -> tuple[str, str]:
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
        <tr class="{'best' if i == 0 else ''}">
          <td>{'★' if i == 0 else ''}</td>
          <td>{ret}</td>
          <td class="price sky{price_cls(sp, cheapest)}">{s['price_text'] if s else '-'}</td>
          <td>{s.get('duration_text','-') if s else '-'}</td>
          <td>{s.get('carrier_text','-') if s else '-'}</td>
          <td>{BTN.format(url=s['seller_url']) if s else '-'}</td>
          <td class="price kayak{price_cls(kp, cheapest)}">{k['price_text'] if k else '-'}</td>
          <td>{k.get('duration_text','-') if k else '-'}</td>
          <td>{k.get('carrier_text','-') if k else '-'}</td>
          <td>{BTN.format(url=k['seller_url']) if k else '-'}</td>
          <td class="price google{price_cls(gp, cheapest)}">{g['price_text'] if g else '-'}</td>
          <td>{g.get('duration_text','-') if g else '-'}</td>
          <td>{g.get('carrier_text','-') if g else '-'}</td>
          <td>{BTN.format(url=g['seller_url']) if g else '-'}</td>
          <td><strong>{winner}</strong></td>
        </tr>""")

    hero = ""
    if overall[1]:
        src, o = overall
        color = {"Skyscanner": "var(--sky)", "KAYAK": "var(--kayak)", "Google": "var(--google)"}.get(src, "var(--sky)")
        hero = f"""
        <section class="hero card">
          <h2>전체 최저가 ({src})</h2>
          <p class="hero-price" style="color:{color}">{o['price_text']}</p>
          <p>출발 {OUTBOUND} · 귀국 {o['return_date']}</p>
          <p>{o.get('duration_text','')}</p>
          <p>{o.get('carrier_text','')}</p>
          {BTN.format(url=o['seller_url'])}
        </section>"""

    body = f"""
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
            <th class="sky">가격</th><th class="sky">비행</th><th class="sky">항공사</th><th class="sky">예약</th>
            <th class="kayak">가격</th><th class="kayak">비행</th><th class="kayak">항공사</th><th class="kayak">예약</th>
            <th class="google">가격</th><th class="google">비행</th><th class="google">항공사</th><th class="google">예약</th>
          </tr>
        </thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
      </div>
      <p class="muted" style="margin-top:12px;">※ 4명(성인 2+어린이 2) 총액 기준 최저 항공권입니다.</p>
    </section>"""

    return body, (overall[1]["return_date"] if overall[1] else "")


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
        </section>"""

    rows = []
    cheapest = best.get("price") if best else None
    for i, a in enumerate(merged):
        row_cls = "best" if i == 0 else ""
        rows.append(f"""
        <tr class="{row_cls}">
          <td>{'★' if i == 0 else ''}</td>
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
            <th></th>
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
        ※ 시카고대 근처 · 주방 포함 · 집 전체 · 게스트 4명(성인 2+어린이 2) · 총액(세금 포함) 기준<br>
        ※ 거리는 Airbnb 숙소 페이지·호스트 안내 기준이며 실제 이동 시간은 교통 상황에 따라 달라질 수 있습니다.
      </p>
    </section>"""


def render_page(flights_html: str, lodging_html: str, now_kst: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="refresh" content="{REFRESH_SECONDS}">
  <title>서울→시카고 여행 비교 | 항공권 · 숙박</title>
  <style>
    :root {{
      --sky: #0770e3; --kayak: #ff690f; --google: #1a73e8;
      --airbnb: #ff385c;
      --bg: #f1f2f8; --card: #fff; --text: #161616; --muted: #626971;
      --best: #e8f4fd; --highlight: #fff8e1;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: "Segoe UI", "Noto Sans KR", sans-serif; background: var(--bg); color: var(--text); }}
    .wrap {{ max-width: 1400px; margin: 0 auto; padding: 24px; }}
    h1 {{ margin: 0 0 8px; font-size: 1.75rem; }}
    .meta {{ color: var(--muted); font-size: 0.95rem; margin-bottom: 16px; }}
    .tabs {{ display: flex; gap: 8px; margin-bottom: 20px; }}
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
    .price {{ font-weight: 700; }}
    .price.sky {{ color: var(--sky); }}
    .price.kayak {{ color: var(--kayak); }}
    .price.google {{ color: var(--google); }}
    .price.airbnb {{ color: var(--airbnb); }}
    .price.highlight {{ background: var(--highlight); border-radius: 4px; }}
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
    @media (max-width: 900px) {{ table {{ font-size: 0.75rem; }} .cta-btn {{ padding: 6px 10px; }} }}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>서울 → 시카고(ORD) 여행 비교</h1>
      <p class="meta">
        성인 {ADULTS}명 · 유소아 {len(CHILD_AGES)}명 (만 {CHILD_AGES[0]}·{CHILD_AGES[1]}세) · 동기화: {now_kst} · {REFRESH_HOURS}시간마다 자동 갱신
      </p>
      <nav class="tabs" role="tablist">
        <button class="tab active" role="tab" aria-selected="true" data-panel="flights">✈️ 항공권</button>
        <button class="tab" role="tab" aria-selected="false" data-panel="lodging">🏠 숙박</button>
      </nav>
    </header>

    <div id="flights" class="panel active" role="tabpanel">
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
  <script>
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
      }});
    }});
    if (location.hash === '#lodging') {{
      document.querySelector('[data-panel="lodging"]').click();
    }}
  </script>
</body>
</html>"""


def main() -> None:
    now_kst = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S KST")
    flights_html, _ = render_flights(load_flights(SKY_FILE), load_flights(KAYAK_FILE), load_flights(GOOGLE_FILE))
    lodging_html = render_lodging(load_lodging(AIRBNB_LODGING))
    page = render_page(flights_html, lodging_html, now_kst)
    HTML.write_text(page, encoding="utf-8")
    INDEX_HTML.write_text(page, encoding="utf-8")
    DOCS_INDEX.parent.mkdir(parents=True, exist_ok=True)
    DOCS_INDEX.write_text(page, encoding="utf-8")
    print(f"Wrote {HTML}")
    print(f"Wrote {INDEX_HTML}")
    print(f"Wrote {DOCS_INDEX}")


if __name__ == "__main__":
    main()
