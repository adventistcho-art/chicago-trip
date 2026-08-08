#!/usr/bin/env python3
"""Chicago 10-day + East Coast 3-day itinerary content for the travel page."""

from __future__ import annotations

from urllib.parse import quote_plus


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
    "subtitle": "뉴욕 인 루트/별도 일정용 · 도시별 3일 코스 · 숙박(2박) 포함 대략 지출",
    "cities": [
        {
            "key": "nyc",
            "label": "뉴욕",
            "chip": "NYC 3일",
            "blurb": "맨해튼 핵심 · 아이와 걷기 좋은 코스",
            "lodging": {
                "nights": 2,
                "per_night": 550_000,
                "amount": 1_100_000,
                "note": "맨해튼/미드타운 가족실·Apt 대략 · 세금·수수료 포함 가정",
                "area": "Times Square · Midtown 인근",
            },
            "days": [
                {
                    "day": 1,
                    "title": "미드타운 · 센트럴파크",
                    "places": ["Times Square", "Rockefeller Center", "Central Park · Zoo"],
                    "spend": [
                        {"item": "숙박 1박 (체크인)", "amount": 550_000},
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
                        {"item": "숙박 1박", "amount": 550_000},
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
            "lodging": {
                "nights": 2,
                "per_night": 400_000,
                "amount": 800_000,
                "note": "National Mall / Downtown 호텔·Apt 대략 · 세금 포함 가정",
                "area": "National Mall · Downtown DC",
            },
            "days": [
                {
                    "day": 1,
                    "title": "내셔널몰 입문",
                    "places": ["National Mall", "Lincoln Memorial", "Washington Monument 주변"],
                    "spend": [
                        {"item": "숙박 1박 (체크인)", "amount": 400_000},
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
                        {"item": "숙박 1박", "amount": 400_000},
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
            "lodging": {
                "nights": 2,
                "per_night": 450_000,
                "amount": 900_000,
                "note": "Downtown / Back Bay 가족실 대략 · 세금 포함 가정",
                "area": "Downtown · Back Bay",
            },
            "days": [
                {
                    "day": 1,
                    "title": "프리덤 트레일",
                    "places": ["Boston Common", "Freedom Trail 핵심 스팟", "Quincy Market"],
                    "spend": [
                        {"item": "숙박 1박 (체크인)", "amount": 450_000},
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
                        {"item": "숙박 1박", "amount": 450_000},
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
    "budget_note": "동부 3일은 숙박 2박 대략치를 Day1·Day2에 포함합니다(가족 4명). 시카고 숙박 탭 금액과는 별도입니다. 도시 간 이동(기차·항공) 비용은 별도입니다.",
}


def _day_spend_total(day: dict) -> int:
    return sum(int(x.get("amount") or 0) for x in day.get("spend") or [])


def _plan_total(days: list[dict]) -> int:
    return sum(_day_spend_total(d) for d in days)


def _city_lodging_total(city: dict) -> int:
    lodging = city.get("lodging") or {}
    if lodging.get("amount") is not None:
        return int(lodging["amount"])
    # Fallback: sum spend rows that look like lodging (already in day totals if present)
    return 0


def _city_activity_total(city: dict) -> int:
    """Day spends minus lodging line items (for breakdown display)."""
    lodging_amt = 0
    for day in city.get("days") or []:
        for s in day.get("spend") or []:
            if "숙박" in (s.get("item") or ""):
                lodging_amt += int(s.get("amount") or 0)
    return _plan_total(city.get("days") or []) - lodging_amt


def _city_total(city: dict) -> int:
    # Lodging is already embedded in day spends; use day total as source of truth.
    return _plan_total(city.get("days") or [])


def plan_budget_summary() -> dict:
    """Totals for dashboard: Chicago 10-day + default East city (NYC)."""
    chicago_total = _plan_total(CHICAGO_10["days"])
    east_cities = {}
    for city in EAST_COAST_3["cities"]:
        total = _city_total(city)
        lodging = city.get("lodging") or {}
        east_cities[city["key"]] = {
            "key": city["key"],
            "label": city["label"],
            "chip": city["chip"],
            "total": total,
            "total_text": fmt_won(total),
            "lodging": lodging.get("amount") or _city_lodging_total(city),
            "lodging_text": fmt_won(lodging.get("amount") or _city_lodging_total(city)),
            "lodging_nights": lodging.get("nights", 2),
            "activity": _city_activity_total(city),
            "activity_text": fmt_won(_city_activity_total(city)),
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
            "note": "뉴욕 3일+숙박 2박 포함 · 도시 변경은 동부 탭",
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


# NYC-in route: arrive 9/23 → Chicago Airbnb 9/26. East 3-day plan budgets 2 nights.
NYC_HOTEL_CHECKIN = "2026-09-23"
NYC_HOTEL_CHECKOUT = "2026-09-25"
NYC_HOTEL_NIGHTS = 2
NYC_HOTEL_AREA = {
    "name": "미드타운 웨스트 · Times Square / Theater District",
    "why": "Day1 센트럴파크·타임스스퀘어, Day2 5번가·박물관과 도보·지하철로 가깝고, Day3 다운타운은 지하철 1번·A/C/E로 이동이 쉽습니다. 가족 4명(초등)에게 동선이 가장 짧습니다.",
    "alt": "조용하면 Midtown East(Grand Central), 박물관 위주면 Upper West Side도 후보.",
}


def _nyc_hotel_booking_urls(hotel_name: str | None = None) -> list[dict]:
    """Deep links to major OTAs for the NYC stay window (2 adults + kids 7 & 8)."""
    q = hotel_name or "Midtown Manhattan Times Square"
    q_enc = quote_plus(q)
    area_enc = quote_plus("Midtown Manhattan, New York")
    cin, cout = NYC_HOTEL_CHECKIN, NYC_HOTEL_CHECKOUT
    return [
        {
            "key": "kayak",
            "label": "KAYAK",
            "css": "kayak",
            "url": (
                f"https://www.kayak.co.kr/hotels/{q_enc}/{cin}/{cout}/"
                "2adults/children-7-8?sort=rank_a"
                if hotel_name
                else (
                    "https://www.kayak.co.kr/hotels/New-York,NY,USA-p9282/"
                    f"{cin}/{cout}/2adults/children-7-8?sort=rank_a"
                )
            ),
        },
        {
            "key": "booking",
            "label": "Booking.com",
            "css": "booking",
            "url": (
                "https://www.booking.com/searchresults.html?"
                f"ss={q_enc}&checkin={cin}&checkout={cout}"
                "&group_adults=2&group_children=2&age=7&age=8&no_rooms=1&selected_currency=KRW"
            ),
        },
        {
            "key": "hotels",
            "label": "Hotels.com",
            "css": "hotels",
            "url": (
                "https://kr.hotels.com/Hotel-Search?"
                f"destination={area_enc}&startDate={cin}&endDate={cout}"
                "&adults=2&children=7%2C8&rooms=1"
                + (f"&keyword={q_enc}" if hotel_name else "")
            ),
        },
        {
            "key": "expedia",
            "label": "Expedia",
            "css": "expedia",
            "url": (
                "https://www.expedia.co.kr/Hotel-Search?"
                f"destination={q_enc if hotel_name else area_enc}"
                f"&startDate={cin}&endDate={cout}"
                "&adults=2&children=7,8&rooms=1"
            ),
        },
        {
            "key": "agoda",
            "label": "Agoda",
            "css": "agoda",
            "url": (
                "https://www.agoda.com/search?"
                f"city=318&checkIn={cin}&checkOut={cout}"
                "&rooms=1&adults=2&children=2&childages=7,8"
                f"&textToSearch={q_enc}"
            ),
        },
        {
            "key": "google",
            "label": "Google 호텔",
            "css": "google",
            "url": (
                "https://www.google.com/travel/hotels?"
                f"q={q_enc}&checkin={cin}&checkout={cout}"
                "&adults=2&children=7%2C8&hl=ko&curr=KRW"
            ),
        },
    ]


NYC_HOTEL_SEARCH = _nyc_hotel_booking_urls()[0]["url"]
NYC_HOTEL_SITES = _nyc_hotel_booking_urls()  # area-wide Midtown search

# Curated family picks for Midtown; prices are approximate KRW totals for 2 nights
# (2 adults + children 7–8), taxes/fees often extra — verify on booking site.
NYC_HOTEL_RECS = [
    {
        "id": "msocial",
        "name": "M Social Hotel New York Times Square",
        "stars": 4,
        "area": "Times Square · Theater District",
        "price": 1_250_000,
        "price_note": "2박 대략 · 시즌·객실타입별 변동",
        "badge": "가족 추천",
        "conditions": [
            "패밀리 패키지·조식 옵션 자주 있음",
            "어린이 동반 시 조식 할인/무료 프로모션 확인",
            "무료 취소 가능 요금제 선택 권장",
            "타임스스퀘어 도보권 · 소음 대비 고층/안쪽 객실",
        ],
        "why": "브로드웨이·록펠러와 가깝고 가족 패키지가 잘 나와 Day1 동선에 최적.",
        "query": "M Social Hotel New York Times Square",
    },
    {
        "id": "parkcentral",
        "name": "Park Central Hotel New York",
        "stars": 4,
        "area": "7th Ave · Central Park South 인근",
        "price": 1_180_000,
        "price_note": "2박 대략 · Twin/Queen 가족실 기준",
        "badge": "동선 최적",
        "conditions": [
            "센트럴파크·타임스스퀘어 사이 위치",
            "더블/트윈 가족 배치 가능 객실 확인",
            "조식 미포함 요금 많음 · 주변 딜리 활용",
            "무료 Wi-Fi · 짐 보관 가능 여부 예약 시 확인",
        ],
        "why": "파크·미드타운 중간이라 Day1·Day2를 걷기 좋게 소화하기 좋습니다.",
        "query": "Park Central Hotel New York",
    },
    {
        "id": "newyorker",
        "name": "The New Yorker, A Wyndham Hotel",
        "stars": 4,
        "area": "Midtown South · Penn Station 인근",
        "price": 1_050_000,
        "price_note": "2박 대략 · 스위트/소파베드 옵션",
        "badge": "가성비",
        "conditions": [
            "가족 스위트·소파베드로 4인 수용 가능성 높음",
            "Penn Station·지하철 접근 좋음 (Day3 다운타운/이동)",
            "리조트 피(일비) 별도인 경우 많음 · 총액 확인",
            "무료 취소 마감일 요금제별 상이",
        ],
        "why": "공간이 넓고 교통 허브 근처라 짐·이동이 많은 가족에게 실용적.",
        "query": "The New Yorker A Wyndham Hotel",
    },
    {
        "id": "homewood",
        "name": "Homewood Suites Midtown Manhattan / Times Square-South",
        "stars": 3,
        "area": "Midtown · Times Square South",
        "price": 1_420_000,
        "price_note": "2박 대략 · 키친ette 스위트",
        "badge": "키친·조식",
        "conditions": [
            "전 객실 스위트 · 간이주방(식비 절약)",
            "핫 브렉퍼스트 포함인 경우가 많음",
            "세탁실·장기 체류형 편의",
            "4인 기준 소파베드 포함 객실 선택",
        ],
        "why": "아이 둘과 조식·간단 식사를 호텔에서 해결하기 좋아 실속형.",
        "query": "Homewood Suites Midtown Manhattan Times Square South",
    },
    {
        "id": "westin",
        "name": "The Westin New York at Times Square",
        "stars": 4,
        "area": "Times Square",
        "price": 1_680_000,
        "price_note": "2박 대략 · 연결객실/패밀리 패키지",
        "badge": "프리미엄",
        "conditions": [
            "연결 객실·롤어웨이로 가족 분리 가능",
            "Westin Family 프로그램(키즈 가이드 등)",
            "2번째 객실 할인 패키지 시즌별 확인",
            "총액에 세금·리조트피 포함 여부 꼭 확인",
        ],
        "why": "공간·브랜드 안정성을 우선할 때. 예산 여유 있으면 1순위 후보.",
        "query": "The Westin New York at Times Square",
    },
]


def _render_east_lodging_card(city: dict) -> str:
    lodging = city.get("lodging") or {}
    if not lodging:
        return ""
    nights = lodging.get("nights", 2)
    per_night = lodging.get("per_night")
    amount = lodging.get("amount") or (per_night * nights if per_night else 0)
    area = lodging.get("area") or ""
    note = lodging.get("note") or ""

    # NYC only: interactive lodging card that opens hotel recommendation modal
    if city.get("key") == "nyc":
        return f"""
        <button type="button" class="card east-lodging-card east-lodging-card-nyc" id="nyc-lodging-open"
          aria-haspopup="dialog" aria-controls="nyc-hotel-modal">
          <div class="east-lodging-top">
            <div>
              <p class="date-kicker">LODGING · {nights}박 · 클릭해서 호텔 추천</p>
              <h3>뉴욕 숙박 추천 보기</h3>
              <p class="muted">{NYC_HOTEL_AREA['name']}</p>
            </div>
            <div class="east-lodging-price">
              <strong>{fmt_won(amount)}</strong>
              <span class="muted">{nights}박 예산대 · 1박 약 {fmt_won(per_night)}</span>
            </div>
          </div>
          <p class="muted" style="margin:10px 0 0;">
            {NYC_HOTEL_CHECKIN} 체크인 → {NYC_HOTEL_CHECKOUT} 체크아웃 · 추천 지역 호텔 {len(NYC_HOTEL_RECS)}곳
            <span class="east-lodging-cta">금액·조건 비교 →</span>
          </p>
        </button>"""

    return f"""
    <section class="card east-lodging-card">
      <div class="east-lodging-top">
        <div>
          <p class="date-kicker">LODGING · {nights}박</p>
          <h3>{city['label']} 숙박 대략</h3>
          <p class="muted">{area}</p>
        </div>
        <div class="east-lodging-price">
          <strong>{fmt_won(amount)}</strong>
          <span class="muted">{nights}박 · 1박 약 {fmt_won(per_night)}</span>
        </div>
      </div>
      <p class="muted" style="margin:10px 0 0;">{note} · Day1·Day2 지출에 이미 포함</p>
    </section>"""


def _render_booking_site_buttons(sites: list[dict], *, compact: bool = False) -> str:
    cls = "nyc-book-btn compact" if compact else "nyc-book-btn"
    bits = []
    for s in sites:
        bits.append(
            f'<a class="{cls} {s["css"]}" href="{s["url"]}" target="_blank" rel="noopener noreferrer">'
            f'<span class="nyc-book-label">{s["label"]}</span>'
            f'<span class="nyc-book-go">예약</span></a>'
        )
    return f'<div class="nyc-book-row">{"".join(bits)}</div>'


def render_nyc_hotel_modal() -> str:
    cards = []
    for h in NYC_HOTEL_RECS:
        conds = "".join(f"<li>{c}</li>" for c in h.get("conditions") or [])
        stars = "★" * int(h.get("stars") or 0)
        sites = _nyc_hotel_booking_urls(h.get("query") or h["name"])
        cards.append(f"""
        <article class="nyc-hotel-card">
          <header class="nyc-hotel-head">
            <div>
              <span class="nyc-hotel-badge">{h.get('badge', '추천')}</span>
              <h3>{h['name']}</h3>
              <p class="muted">{stars} · {h.get('area', '')}</p>
            </div>
            <div class="nyc-hotel-price">
              <strong>{fmt_won(h.get('price'))}</strong>
              <span class="muted">{h.get('price_note', '')}</span>
            </div>
          </header>
          <p class="nyc-hotel-why">{h.get('why', '')}</p>
          <ul class="nyc-hotel-conds">{conds}</ul>
          <p class="nyc-book-caption">이 호텔 · 사이트별 검색·예약</p>
          {_render_booking_site_buttons(sites, compact=True)}
        </article>""")

    area_sites = _render_booking_site_buttons(NYC_HOTEL_SITES)

    return f"""
    <div id="nyc-hotel-modal" class="nyc-modal" hidden role="dialog" aria-modal="true"
      aria-labelledby="nyc-hotel-modal-title">
      <div class="nyc-modal-backdrop" data-nyc-close></div>
      <div class="nyc-modal-panel">
        <header class="nyc-modal-head">
          <div>
            <p class="date-kicker">NYC LODGING PICKS</p>
            <h2 id="nyc-hotel-modal-title">뉴욕 숙박 추천</h2>
            <p class="muted">
              {NYC_HOTEL_CHECKIN} → {NYC_HOTEL_CHECKOUT} · {NYC_HOTEL_NIGHTS}박 ·
              성인 2 · 아동 2(만 7·8세) · 추천 지역: {NYC_HOTEL_AREA['name']}
            </p>
          </div>
          <button type="button" class="nyc-modal-close" data-nyc-close aria-label="닫기">×</button>
        </header>
        <div class="nyc-modal-why card">
          <strong>왜 이 지역?</strong>
          <p class="muted" style="margin:6px 0 0;">{NYC_HOTEL_AREA['why']}</p>
          <p class="muted" style="margin:8px 0 0;">{NYC_HOTEL_AREA['alt']}</p>
        </div>
        <section class="nyc-sites-bar card">
          <div class="nyc-sites-bar-copy">
            <strong>주요 사이트에서 Midtown 검색·예약</strong>
            <p class="muted" style="margin:4px 0 0;">날짜·인원(성인2·아동7·8세)이 들어간 링크로 바로 이동합니다.</p>
          </div>
          {area_sites}
        </section>
        <p class="muted nyc-modal-note">
          금액은 2박 총액 대략치(KRW)입니다. 사이트마다 세금·리조트피가 다를 수 있으니 예약 전 총액을 확인하세요.
          시카고 Airbnb 체크인이 9/26이면 체크아웃을 9/26으로 하루 연장하는 것도 검토하세요.
        </p>
        <div class="nyc-hotel-grid">{''.join(cards)}</div>
        <footer class="nyc-modal-foot">
          <button type="button" class="nyc-modal-secondary" data-nyc-close>닫기</button>
        </footer>
      </div>
    </div>
    """


def render_east_plan() -> str:
    plan = EAST_COAST_3
    tabs = []
    panels = []
    for i, city in enumerate(plan["cities"]):
        active = "active" if i == 0 else ""
        city_total = _city_total(city)
        lodging = city.get("lodging") or {}
        lodge_amt = lodging.get("amount") or 0
        activity = _city_activity_total(city)
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
          {_render_east_lodging_card(city)}
          <div class="east-budget-strip">
            <span>숙박 {fmt_won(lodge_amt)}</span>
            <span>활동·식사 {fmt_won(activity)}</span>
            <span><strong>합계 {fmt_won(city_total)}</strong></span>
          </div>
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
          <span class="muted">각 3일 · 숙박 2박 포함</span>
        </div>
      </div>
    </section>
    <p class="flight-hint muted">{plan['budget_note']}</p>
    <div class="route-switch east-switch" role="tablist">{''.join(tabs)}</div>
    {''.join(panels)}
    {render_nyc_hotel_modal()}
    """
