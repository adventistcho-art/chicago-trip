#!/usr/bin/env python3
"""Chicago 10-day + East Coast 3-day itinerary content for the travel page."""

from __future__ import annotations


def fmt_won(amount: int | None) -> str:
    if amount is None:
        return "-"
    return f"₩{amount:,}"


CHICAGO_10 = {
    "title": "시카고 10일 여행계획",
    "subtitle": "가족 4명(성인2·어린이2) · Hyde Park/UChicago 거점 · 대략 지출 포함",
    "days": [
        {
            "day": 1,
            "title": "도착 · 시내 첫인상",
            "places": ["ORD 도착 · 숙소 체크인", "Millennium Park · Cloud Gate", "Michigan Avenue 산책"],
            "tips": "시차 적응 위주 · 가볍게 걷기",
            "spend": [
                {"item": "시내 교통/우버", "amount": 80000},
                {"item": "식사", "amount": 120000},
                {"item": "간식·기타", "amount": 40000},
            ],
        },
        {
            "day": 2,
            "title": "미술관 · 강변",
            "places": ["Art Institute of Chicago", "Chicago Riverwalk", "Navy Pier (야경)"],
            "tips": "미술관은 어린이 할인/무료 요일 확인",
            "spend": [
                {"item": "미술관 입장(4명)", "amount": 180000},
                {"item": "식사", "amount": 130000},
                {"item": "교통", "amount": 50000},
            ],
        },
        {
            "day": 3,
            "title": "박물관 캠퍼스",
            "places": ["Shedd Aquarium", "Field Museum 또는 Adler Planetarium", "Grant Park"],
            "tips": "CityPASS/박물관 콤보권 비교 추천",
            "spend": [
                {"item": "수족관·박물관(4명)", "amount": 320000},
                {"item": "식사", "amount": 140000},
                {"item": "교통", "amount": 50000},
            ],
        },
        {
            "day": 4,
            "title": "하이드파크 데이",
            "places": ["Museum of Science and Industry", "University of Chicago 캠퍼스", "Promontory Point"],
            "tips": "숙소 근처라 이동 부담 적음 · 아이 친화",
            "spend": [
                {"item": "MSI 입장(4명)", "amount": 200000},
                {"item": "식사", "amount": 120000},
                {"item": "간식·기념품", "amount": 60000},
            ],
        },
        {
            "day": 5,
            "title": "링컨파크 · 동물원",
            "places": ["Lincoln Park Zoo (무료)", "Lincoln Park Conservatory", "North Avenue Beach"],
            "tips": "무료 코스로 예산 절약 데이",
            "spend": [
                {"item": "식사", "amount": 130000},
                {"item": "교통", "amount": 60000},
                {"item": "아이스크림·기타", "amount": 40000},
            ],
        },
        {
            "day": 6,
            "title": "건축 크루즈 · 루프",
            "places": ["Architecture River Cruise", "The Loop 워킹", "Willis Tower Skydeck (선택)"],
            "tips": "크루즈는 주말 오전 예약 권장",
            "spend": [
                {"item": "크루즈(4명)", "amount": 220000},
                {"item": "스카이덱(선택)", "amount": 180000},
                {"item": "식사·교통", "amount": 160000},
            ],
        },
        {
            "day": 7,
            "title": "매그니피션트 마일",
            "places": ["360 CHICAGO / John Hancock", "Water Tower · 쇼핑", "American Girl / Lego Store"],
            "tips": "쇼핑·기념품은 예산 상한 정해두기",
            "spend": [
                {"item": "전망대(4명)", "amount": 160000},
                {"item": "식사", "amount": 150000},
                {"item": "기념품·쇼핑", "amount": 200000},
            ],
        },
        {
            "day": 8,
            "title": "근교 데이트립",
            "places": ["Oak Park (Frank Lloyd Wright) 또는", "Suburban outlet / 지역 공원", "저녁은 숙소 근처"],
            "tips": "렌트카 있으면 여유 · 대중교통도 가능",
            "spend": [
                {"item": "유류/주차 또는 교통", "amount": 100000},
                {"item": "입장·액티비티", "amount": 120000},
                {"item": "식사", "amount": 140000},
            ],
        },
        {
            "day": 9,
            "title": "여유 · 재방문",
            "places": ["좋아하는 장소 재방문", "호숫가 피크닉", "시카고 딥디시 피자"],
            "tips": "짐 정리·세탁 · 귀국 전 여유 일정",
            "spend": [
                {"item": "식사(피자 포함)", "amount": 160000},
                {"item": "교통", "amount": 40000},
                {"item": "여유 예산", "amount": 80000},
            ],
        },
        {
            "day": 10,
            "title": "출국 준비",
            "places": ["숙소 체크아웃", "ORD 이동", "공항 식사·쇼핑"],
            "tips": "공항 3시간 전 도착 권장 · 짐 여유",
            "spend": [
                {"item": "공항 이동", "amount": 100000},
                {"item": "공항 식사", "amount": 120000},
                {"item": "잡비", "amount": 50000},
            ],
        },
    ],
    "budget_note": "위 금액은 4명 기준 대략치(KRW)이며 시즌·환율·할인에 따라 달라집니다. 항공·숙박·렌트 총액은 다른 탭 선택값을 참고하세요.",
}

EAST_COAST_3 = {
    "title": "동부 3일 여행계획",
    "subtitle": "뉴욕 인 루트/별도 일정용 · 도시별 3일 코스 · 대략 지출 포함",
    "cities": [
        {
            "key": "nyc",
            "label": "뉴욕",
            "chip": "NYC 3일",
            "blurb": "맨해튼 핵심 · 아이와 걷기 좋은 코스",
            "days": [
                {
                    "day": 1,
                    "title": "미드타운 · 센트럴파크",
                    "places": ["Times Square", "Rockefeller Center", "Central Park · Zoo"],
                    "spend": [
                        {"item": "교통(MetroCard/우버)", "amount": 80000},
                        {"item": "식사", "amount": 180000},
                        {"item": "동물원·잡비", "amount": 120000},
                    ],
                },
                {
                    "day": 2,
                    "title": "박물관 · 5번가",
                    "places": ["American Museum of Natural History 또는 MoMA", "5th Avenue", "Empire State (선택)"],
                    "spend": [
                        {"item": "박물관(4명)", "amount": 220000},
                        {"item": "식사", "amount": 180000},
                        {"item": "전망대(선택)", "amount": 200000},
                    ],
                },
                {
                    "day": 3,
                    "title": "다운타운 · 자유의 여신",
                    "places": ["Statue of Cruise / Ferry", "Wall Street · 9/11 Memorial", "Brooklyn Bridge 산책"],
                    "spend": [
                        {"item": "페리·입장", "amount": 200000},
                        {"item": "식사", "amount": 170000},
                        {"item": "교통·기념품", "amount": 100000},
                    ],
                },
            ],
        },
        {
            "key": "dc",
            "label": "워싱턴",
            "chip": "DC 3일",
            "blurb": "내셔널몰 박물관이 대부분 무료 · 예산 친화",
            "days": [
                {
                    "day": 1,
                    "title": "내셔널몰 입문",
                    "places": ["National Mall", "Lincoln Memorial", "Washington Monument 주변"],
                    "spend": [
                        {"item": "교통", "amount": 70000},
                        {"item": "식사", "amount": 150000},
                        {"item": "간식·물", "amount": 40000},
                    ],
                },
                {
                    "day": 2,
                    "title": "스미스소니언 데이",
                    "places": ["Air and Space Museum", "Natural History Museum", "National Gallery (선택)"],
                    "spend": [
                        {"item": "식사", "amount": 160000},
                        {"item": "교통", "amount": 60000},
                        {"item": "기념품", "amount": 80000},
                    ],
                },
                {
                    "day": 3,
                    "title": "국회 · 백악관 주변",
                    "places": ["U.S. Capitol 외부", "Library of Congress (선택)", "White House 포토스팟"],
                    "spend": [
                        {"item": "식사", "amount": 150000},
                        {"item": "교통", "amount": 60000},
                        {"item": "여유 예산", "amount": 70000},
                    ],
                },
            ],
        },
        {
            "key": "bos",
            "label": "보스턴",
            "chip": "BOS 3일",
            "blurb": "프리덤 트레일 · 하버드 · 가족 걷기 코스",
            "days": [
                {
                    "day": 1,
                    "title": "프리덤 트레일",
                    "places": ["Boston Common", "Freedom Trail 핵심 스팟", "Quincy Market"],
                    "spend": [
                        {"item": "식사", "amount": 160000},
                        {"item": "교통", "amount": 60000},
                        {"item": "간식·기념품", "amount": 70000},
                    ],
                },
                {
                    "day": 2,
                    "title": "캠브리지 · 하버드",
                    "places": ["Harvard Yard", "MIT 캠퍼스 포토", "Charles River"],
                    "spend": [
                        {"item": "식사", "amount": 150000},
                        {"item": "교통", "amount": 70000},
                        {"item": "박물관(선택)", "amount": 100000},
                    ],
                },
                {
                    "day": 3,
                    "title": "항구 · 박물관",
                    "places": ["New England Aquarium 또는 Museum of Science", "Harborwalk", "North End 이탈리안"],
                    "spend": [
                        {"item": "입장(4명)", "amount": 200000},
                        {"item": "식사", "amount": 180000},
                        {"item": "교통", "amount": 60000},
                    ],
                },
            ],
        },
    ],
    "budget_note": "동부 3일은 시카고와 별도 일정/연결 일정으로 쓰세요. NYC 입국 후 시카고로 이동하는 루트와 잘 맞습니다. 도시 간 이동(기차·항공) 비용은 별도입니다.",
}


def _day_spend_total(day: dict) -> int:
    return sum(int(x.get("amount") or 0) for x in day.get("spend") or [])


def _plan_total(days: list[dict]) -> int:
    return sum(_day_spend_total(d) for d in days)


def plan_budget_summary() -> dict:
    """Totals for dashboard: Chicago 10-day + default East city (NYC)."""
    chicago_total = _plan_total(CHICAGO_10["days"])
    east_cities = {}
    for city in EAST_COAST_3["cities"]:
        east_cities[city["key"]] = {
            "key": city["key"],
            "label": city["label"],
            "chip": city["chip"],
            "total": _plan_total(city["days"]),
            "total_text": fmt_won(_plan_total(city["days"])),
        }
    nyc = east_cities.get("nyc") or next(iter(east_cities.values()), None)
    return {
        "chicago": {
            "label": "시카고 여행경비",
            "chip": "10일 현지",
            "total": chicago_total,
            "total_text": fmt_won(chicago_total),
            "note": "항공·숙박·렌트 제외 · 현지 활동비 대략",
        },
        "east": {
            "label": "동부 3일",
            "chip": (nyc or {}).get("chip", "NYC 3일"),
            "city_key": (nyc or {}).get("key", "nyc"),
            "city_label": (nyc or {}).get("label", "뉴욕"),
            "total": (nyc or {}).get("total", 0),
            "total_text": (nyc or {}).get("total_text", "₩0"),
            "note": "뉴욕 3일 코스 대략 · 도시 변경은 동부 탭",
            "cities": east_cities,
        },
    }


def _render_day_card(day: dict, accent: str = "") -> str:
    places = "".join(f"<li>{p}</li>" for p in day.get("places") or [])
    spend_rows = "".join(
        f"<tr><td>{s['item']}</td><td class='price'>{fmt_won(s['amount'])}</td></tr>"
        for s in day.get("spend") or []
    )
    tip = day.get("tips") or ""
    tip_html = f'<p class="itin-tip">{tip}</p>' if tip else ""
    total = _day_spend_total(day)
    return f"""
    <article class="itin-day {accent}">
      <header class="itin-day-head">
        <span class="itin-day-num">Day {day['day']}</span>
        <h3>{day['title']}</h3>
        <span class="itin-day-total">{fmt_won(total)}</span>
      </header>
      <ul class="itin-places">{places}</ul>
      {tip_html}
      <table class="itin-spend">
        <thead><tr><th>지출 항목</th><th>대략</th></tr></thead>
        <tbody>{spend_rows}</tbody>
      </table>
    </article>"""


def render_chicago_plan() -> str:
    plan = CHICAGO_10
    days_html = "".join(_render_day_card(d) for d in plan["days"])
    total = _plan_total(plan["days"])
    return f"""
    <section class="route-hero card itin-hero chi-itin-hero">
      <div class="route-hero-copy">
        <p class="route-kicker">CHICAGO · 10 DAYS</p>
        <h2>{plan['title']}</h2>
        <p class="muted">{plan['subtitle']}</p>
      </div>
      <div class="route-stats">
        <div class="route-stat">
          <span class="muted">현지 활동비 합계(대략)</span>
          <strong>{fmt_won(total)}</strong>
          <span class="muted">항공·숙박·렌트 제외 · 4명</span>
        </div>
      </div>
    </section>
    <p class="flight-hint muted">{plan['budget_note']}</p>
    <div class="itin-stack">{days_html}</div>
    """


def render_east_plan() -> str:
    plan = EAST_COAST_3
    tabs = []
    panels = []
    for i, city in enumerate(plan["cities"]):
        active = "active" if i == 0 else ""
        city_total = _plan_total(city["days"])
        tabs.append(
            f'<button type="button" class="east-tab {active}" data-east="{city["key"]}" role="tab" '
            f'aria-selected="{"true" if i == 0 else "false"}">'
            f'<span class="route-tab-title">{city["label"]} 3일</span>'
            f'<span class="route-tab-sub">{city["chip"]} · 약 {fmt_won(city_total)}</span></button>'
        )
        days_html = "".join(_render_day_card(d, accent=f"east-{city['key']}") for d in city["days"])
        panels.append(f"""
        <div class="east-panel {active}" data-east-panel="{city['key']}">
          <p class="muted" style="margin:0 0 14px;">{city['blurb']}</p>
          <div class="itin-stack">{days_html}</div>
        </div>""")

    return f"""
    <section class="route-hero card itin-hero east-itin-hero">
      <div class="route-hero-copy">
        <p class="route-kicker">EAST COAST · 3 DAYS</p>
        <h2>{plan['title']}</h2>
        <p class="muted">{plan['subtitle']}</p>
      </div>
      <div class="route-stats">
        <div class="route-stat">
          <span class="muted">도시 선택</span>
          <strong>NYC · DC · BOS</strong>
          <span class="muted">각 3일 코스</span>
        </div>
      </div>
    </section>
    <p class="flight-hint muted">{plan['budget_note']}</p>
    <div class="route-switch east-switch" role="tablist">{''.join(tabs)}</div>
    {''.join(panels)}
    """
