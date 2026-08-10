"""시카고 15박 16일 알찬 동선 (Sleeping Bear Dunes 포함) · 9/24–10/9."""

from __future__ import annotations

USD_KRW = 1400


def won(n: int) -> str:
    return f"₩{n:,}"


def _yt(video_id: str, title: str) -> dict:
    return {
        "id": video_id,
        "title": title,
        "embed": f"https://www.youtube.com/embed/{video_id}",
        "watch": f"https://www.youtube.com/watch?v={video_id}",
        "thumb": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
    }


# 주차별 요약 + 일별 상세
WEEKS = [
    {
        "id": "w1",
        "label": "1주차",
        "title": "시카고 도심 핵심 · 가을 팝업",
        "dates": "9/24(목) ~ 9/28(월)",
        "mode": "대중교통 · 하루 2~3곳",
        "blurb": "도착 직인 후 네이비피어·박물관캠퍼스·MSI·옥토버페스트·리버크루즈까지 도심을 압축 체험.",
    },
    {
        "id": "w2",
        "label": "2주차",
        "title": "슬리핑 비어 던스 로드트립",
        "dates": "9/29(화) ~ 10/2(금)",
        "mode": "렌트카 · M-22 해안 도로",
        "blurb": "시카고→소거턱/홀랜드→트래버스시티 거점 · Dune Climb · Pierce Stocking · 사과따기 · 인디애나 던스 경유 복귀.",
    },
    {
        "id": "w3",
        "label": "3주차",
        "title": "농장 축제 & 할로윈 카운트다운",
        "dates": "10/3(토) ~ 10/9(금)",
        "mode": "자차·근교 데이트립",
        "blurb": "애플페스트·링컨파크·리차드슨 농장·브룩필드·호박등불·쇼핑 마무리 후 ORD 출국.",
    },
]


DAYS: list[dict] = [
    # —— Week 1 ——
    {
        "week": "w1",
        "date": "9/24(목)",
        "theme": "도착 & 도심 구경",
        "transport": "대중교통 / 우버",
        "distance": "ORD→시내 약 27km · 피어↔밀레니엄 도보·버스 3km대",
        "drive_note": "첫날은 렌트 없이 CTA/우버 권장",
        "flow": [
            "시카고 도착 후 숙소 체크인",
            "Navy Pier 대관람차",
            "Millennium Park · Chicago Bean 사진",
        ],
        "places": [
            {
                "name": "Navy Pier",
                "addr": "600 E Grand Ave, Chicago, IL 60611",
                "note": "대관람차(Centennial Wheel) · 호숫가 산책",
            },
            {
                "name": "Millennium Park / Cloud Gate",
                "addr": "201 E Randolph St, Chicago, IL 60601",
                "note": "빈(The Bean) 야경·황금시간 촬영",
            },
        ],
        "spend": [
            ("이동(ORD→숙소·시내)", 90000),
            ("대관람차(4명)", 100000),
            ("식사·간식", 140000),
        ],
        "media": [
            _yt("vfozrRFSKuM", "Navy Pier · Centennial Wheel"),
            _yt("ZKq5fL1hxhs", "Millennium Park · Cloud Gate (The Bean)"),
        ],
        "tips": "시차 적응 위주 · 짐은 숙소에 두고 가볍게. 행사·날씨에 따라 피어 혼잡.",
    },
    {
        "week": "w1",
        "date": "9/25(금)",
        "theme": "박물관 & 전망대",
        "transport": "대중교통 / 우버",
        "distance": "Museum Campus 도보권 · Skydeck까지 약 2–3km",
        "drive_note": "Museum Campus ↔ Willis는 CTA/우버",
        "flow": [
            "오전 Shedd Aquarium (돌고래·해양생물)",
            "오후 Field Museum (Sue 공룡)",
            "저녁 Willis Tower Skydeck 103층",
        ],
        "places": [
            {
                "name": "Shedd Aquarium",
                "addr": "1200 S Lake Shore Dr, Chicago, IL 60605",
                "note": "돌고래 쇼 타임테이블 사전 확인",
            },
            {
                "name": "Field Museum",
                "addr": "1400 S Lake Shore Dr, Chicago, IL 60605",
                "note": "T. rex Sue · 자연사 핵심",
            },
            {
                "name": "Willis Tower Skydeck",
                "addr": "233 S Wacker Dr, Chicago, IL 60606",
                "note": "The Ledge 유리바닥 · 야경 예약 권장",
            },
        ],
        "spend": [
            ("Shedd+Field (4명, CityPASS 시 절약)", 380000),
            ("Skydeck (4명)", 180000),
            ("식사·교통", 180000),
        ],
        "media": [
            _yt("R65SK8gIUhI", "Shedd Aquarium walkthrough"),
            _yt("GyBTWEsYFxk", "Field Museum · Sue"),
            _yt("DmSk42LDLKw", "Willis Tower Skydeck / The Ledge"),
        ],
        "tips": "CityPASS·Go City로 Shedd+Field+Skydeck 묶음 비교. 스카이덱은 일몰 전후 타임슬롯.",
    },
    {
        "week": "w1",
        "date": "9/26(토)",
        "theme": "과학 체험 & 야외 축제",
        "transport": "Metra / CTA + 우버",
        "distance": "숙소→MSI 약 2–4km · MSI→Jack’s 약 14km",
        "drive_note": "Jack’s는 Goose Island · 우버 또는 버스+도보",
        "flow": [
            "오전 MSI (U-505 잠수함)",
            "오후 Jack’s Pumpkin Pop-Up (호박·옥수수 미로)",
        ],
        "places": [
            {
                "name": "Museum of Science and Industry",
                "addr": "5700 S Lake Shore Dr, Chicago, IL 60637",
                "note": "U-505 · 아이 친화 · Hyde Park 거점이면 최적",
            },
            {
                "name": "Jack’s Pumpkin Pop-Up",
                "addr": "1265 W Le Moyne St, Chicago, IL 60642",
                "note": "2026시즌 대략 9/19–11/1 · 타임입장 티켓",
            },
        ],
        "spend": [
            ("MSI 입장(4명)", 200000),
            ("Jack’s 입장·체험(4명)", 180000),
            ("식사·교통", 160000),
        ],
        "media": [
            _yt("4Sv3NdH2w_o", "MSI · U-505 / 과학산업박물관"),
            _yt("wh6JBEM8cyg", "Jack’s Pumpkin Pop-Up Chicago"),
        ],
        "tips": "Jack’s는 주말 혼잡 · 오전 MSI → 오후 타임슬롯 예약. 야외라 바람·비 대비.",
    },
    {
        "week": "w1",
        "date": "9/27(일)",
        "theme": "독일 가을 축제",
        "transport": "CTA / 우버",
        "distance": "Art Institute↔Lincoln Square 약 12–15km",
        "drive_note": "브라운라인 Western 또는 우버",
        "flow": [
            "오전 Art Institute (어린이 체험관)",
            "오후 Lincoln Square Oktoberfest",
        ],
        "places": [
            {
                "name": "Art Institute of Chicago",
                "addr": "111 S Michigan Ave, Chicago, IL 60603",
                "note": "Ryan Learning Center 등 키즈 프로그램 확인",
            },
            {
                "name": "Lincoln Square Oktoberfest",
                "addr": "Lincoln Square, Chicago (Lincoln Ave / Leland 일대)",
                "note": "독일 소시지·프레첼·라이브 · 연중 날짜 변동 → 공식 공지 확인",
            },
        ],
        "spend": [
            ("미술관(4명)", 180000),
            ("옥토버페스트 먹거리", 160000),
            ("교통", 50000),
        ],
        "media": [
            _yt("NOUX3_CUP-Q", "Art Institute of Chicago"),
            _yt("wh6JBEM8cyg", "가을 시카고 야외 축제 분위기 참고"),
        ],
        "tips": "축제 주말은 일찍 도착. 알콜 구역·키즈 존 구분 확인.",
    },
    {
        "week": "w1",
        "date": "9/28(월)",
        "theme": "크루즈 & 쇼핑",
        "transport": "도보 / CTA",
        "distance": "Riverwalk↔Mag Mile 도보권 (2–3km)",
        "drive_note": "주차 부담 큰 구간 · 대중교통 유리",
        "flow": [
            "오전 Architecture River Cruise",
            "오후 Magnificent Mile 쇼핑",
            "딥디시 피자 파티",
        ],
        "places": [
            {
                "name": "Architecture River Cruise",
                "addr": "Chicago Riverwalk docks (Michigan Ave / State St 일대)",
                "note": " Wendella / First Lady / Shoreline 등 사전예약",
            },
            {
                "name": "Magnificent Mile",
                "addr": "N Michigan Ave, Chicago, IL 60611",
                "note": "Water Tower · 기념품 · 패밀리 스토어",
            },
        ],
        "spend": [
            ("리버 크루즈(4명)", 220000),
            ("딥디시·식사", 180000),
            ("쇼핑·기념품", 200000),
        ],
        "media": [
            _yt("hLQvkiCdBmE", "Chicago Architecture River Cruise"),
            _yt("Y5Q5ZZ-JN40", "Chicago deep dish pizza"),
        ],
        "tips": "크루즈는 오전 타임이 여유. 피자는 Giordano’s / Lou Malnati’s / Pequod’s 등.",
    },
    # —— Week 2 ——
    {
        "week": "w2",
        "date": "9/29(화)",
        "theme": "미시간호 해안 마을 북상",
        "transport": "렌트카 (다운타운/시내 픽업)",
        "distance": "CHI→Saugatuck/Holland ≈ 220–240km · 약 2.5–3시간 · Holland→Traverse City ≈ 250km · 약 3시간",
        "drive_note": "총 주행 약 470–500km · M-22 해안선은 다음 날부터",
        "flow": [
            "오전 렌트 수령 후 시카고 출발",
            "Saugatuck / Holland (풍차·해변)",
            "Traverse City 방면 북상 · 숙소 체크인",
        ],
        "places": [
            {
                "name": "Saugatuck / Douglas",
                "addr": "Saugatuck, MI 49453",
                "note": "예술 마을 · Oval Beach",
            },
            {
                "name": "Holland Windmill Island",
                "addr": "1 Lincoln Ave, Holland, MI 49423",
                "note": "네덜란드 풍차 마을 포토",
            },
            {
                "name": "Traverse City 숙소",
                "addr": "Traverse City, MI 49684",
                "note": "슬리핑비어 거점 · 2~3박",
            },
        ],
        "spend": [
            ("유류·톨 (당일)", 120000),
            ("마을 입장·간식", 80000),
            ("식사", 150000),
            ("트래버스시티 숙박(1박)", 280000),
        ],
        "media": [
            _yt("VHgPAQAGbpg", "Saugatuck / Michigan lakeshore towns"),
            _yt("Mxr1w5Cw-WU", "Sleeping Bear Dunes 미리보기"),
        ],
        "tips": "아이 있으면 운전 교대·휴게 자주. 숙소는 Glen Arbor/Empire도 대안(공원 더 가까움).",
    },
    {
        "week": "w2",
        "date": "9/30(수)",
        "theme": "던스 마을 & 트레일 (중간일)",
        "transport": "렌트카",
        "distance": "TC↔Empire/Glen Arbor ≈ 40–55km · 왕복 약 1.5시간대",
        "drive_note": "M-22 / M-109 해안 드라이브 시작",
        "flow": [
            "오전 Empire Bluff 또는 Sleeping Bear Point 트레일",
            "Glen Arbor 마을 점심·기념품",
            "해변·호수 산책 · 일찍 휴식",
        ],
        "places": [
            {
                "name": "Empire Bluff Trail",
                "addr": "Empire, MI 49630",
                "note": "왕복 약 2.4km · 미시간호 절경",
            },
            {
                "name": "Glen Arbor",
                "addr": "Glen Arbor, MI 49636",
                "note": "Cherry Republic · 마을 카페",
            },
        ],
        "spend": [
            ("국립호안 입장(차량)", 45000),
            ("식사·기념품", 160000),
            ("숙박(1박)", 280000),
        ],
        "media": [
            _yt("Mxr1w5Cw-WU", "Sleeping Bear Dunes · Empire / overlooks"),
        ],
        "tips": "원안 3박4일 중 ‘여유일’. 바람·모래 대비 모자·물. NPS 주간 패스($25/차량대 수준) 확인.",
    },
    {
        "week": "w2",
        "date": "10/1(목)",
        "theme": "슬리핑 비어 던스 집중",
        "transport": "렌트카",
        "distance": "Dune Climb↔Pierce Stocking ≈ 10km대 · Scenic Drive 7.5마일(약 12km) 루프",
        "drive_note": "차 안에서 전망 · 아이와 모래썰매",
        "flow": [
            "오전 Dune Climb (모래언덕·썰매)",
            "오후 Pierce Stocking Scenic Drive",
            "저녁 Traverse City 체리 디저트",
        ],
        "places": [
            {
                "name": "Dune Climb",
                "addr": "6748 S Dune Hwy, Glen Arbor, MI 49636",
                "note": "높이 체감 큰 모래벽 · 내려올 때 최고",
            },
            {
                "name": "Pierce Stocking Scenic Drive",
                "addr": "Pierce Stocking Scenic Dr, Empire, MI",
                "note": "12개 전망 스톱 · Lake Michigan Overlook",
            },
            {
                "name": "Traverse City downtown",
                "addr": "Front St, Traverse City, MI",
                "note": "체리 파이·아이스크림",
            },
        ],
        "spend": [
            ("공원 패스(이미 구매 시 제외)", 0),
            ("모래썰매·간식", 60000),
            ("체리 디저트·저녁", 180000),
            ("숙박(1박)", 280000),
        ],
        "media": [
            _yt("Mxr1w5Cw-WU", "Dune Climb + Pierce Stocking"),
        ],
        "tips": "절벽 가장자리 안전 주의(특히 Overlook). 모래·운동화·여분 옷. 일몰 전 드라이브 완료.",
    },
    {
        "week": "w2",
        "date": "10/2(금)",
        "theme": "사과따기 · 남하 · 시카고 복귀",
        "transport": "렌트카",
        "distance": "TC→과수원 근교 20–40km · TC→Indiana Dunes ≈ 480–520km · 약 5–6시간 · Dunes→CHI ≈ 70–90km · 약 1–1.5시간",
        "drive_note": "장거리 운전일 · 일찍 출발 권장",
        "flow": [
            "오전 과수원 Apple Picking",
            "남하하며 Indiana Dunes 들르기",
            "시카고 숙소 복귀",
        ],
        "places": [
            {
                "name": "Apple orchard (TC 근교)",
                "addr": "Traverse City / Old Mission / Leelanau 일대",
                "note": "시즌 U-pick · 농장별 운영일 확인",
            },
            {
                "name": "Indiana Dunes National Park",
                "addr": "1100 N Mineral Springs Rd, Porter, IN 46304",
                "note": "West Beach 또는 Indiana Dunes State Park 짧게",
            },
        ],
        "spend": [
            ("사과따기·농장", 80000),
            ("유류·톨 (장거리)", 180000),
            ("Indiana Dunes 주차/간식", 50000),
            ("식사", 140000),
        ],
        "media": [
            _yt("qat0Pakzur4", "Indiana Dunes National Park"),
            _yt("Mxr1w5Cw-WU", "Sleeping Bear 여운 · 모래언덕"),
        ],
        "tips": "운전 피로 크면 던스는 스킵하고 직행도 OK. 렌트는 시카고에서 계속 사용(3주차 근교).",
    },
    # —— Week 3 ——
    {
        "week": "w3",
        "date": "10/3(토)",
        "theme": "애플 페스트 & 동물원",
        "transport": "CTA / 우버 / 자차",
        "distance": "Lincoln Square↔Lincoln Park Zoo ≈ 6–8km",
        "drive_note": "축제 주차 어려움 · 대중교통 유리",
        "flow": [
            "오전 Lincoln Square Apple Fest",
            "오후 Lincoln Park Zoo (무료)",
        ],
        "places": [
            {
                "name": "Lincoln Square Apple Fest",
                "addr": "Lincoln Square, Chicago",
                "note": "사과·파이·사이더 도넛 · 연례 주말 행사(날짜 공지 확인)",
            },
            {
                "name": "Lincoln Park Zoo",
                "addr": "2001 N Clark St, Chicago, IL 60614",
                "note": "기본 입장 무료 · 주차·특별전 유료",
            },
        ],
        "spend": [
            ("페스트 먹거리(4명)", 120000),
            ("교통·주차", 50000),
            ("식사", 130000),
        ],
        "media": [
            _yt("IlEZraDeuBs", "Lincoln Park Zoo Chicago"),
        ],
        "tips": "애플페스트는 오전 일찍. 동물원은 해질녘 전 핵심 존만.",
    },
    {
        "week": "w3",
        "date": "10/4(일)",
        "theme": "휴식 & 도심 산책",
        "transport": "CTA / 도보",
        "distance": "Navy Pier↔Riverwalk ≈ 2–3km",
        "drive_note": "가벼운 동선",
        "flow": [
            "오전 Navy Pier 어린이 박물관",
            "오후 Chicago Riverwalk 카페",
        ],
        "places": [
            {
                "name": "Chicago Children’s Museum",
                "addr": "700 E Grand Ave, Chicago, IL 60611",
                "note": "Navy Pier 내 · 연령대별 체험",
            },
            {
                "name": "Chicago Riverwalk",
                "addr": "Chicago Riverwalk, Chicago, IL",
                "note": "카페·보트 구경 · 여유 데이",
            },
        ],
        "spend": [
            ("어린이박물관(4명)", 120000),
            ("카페·간식", 80000),
            ("식사·교통", 140000),
        ],
        "media": [
            _yt("vfozrRFSKuM", "Navy Pier 재방문 · 어린이박물관 인근"),
        ],
        "tips": "로드트립 피로 회복일. 비 오면 실내 위주.",
    },
    {
        "week": "w3",
        "date": "10/5(월)",
        "theme": "세계 최대 옥수수 미로",
        "transport": "렌트카",
        "distance": "시카고→Richardson Farm ≈ 90–100km · 약 1시간 15분",
        "drive_note": "왕복 약 2.5시간 + 하루 올인",
        "flow": [
            "Richardson Adventure Farm 종일",
            "옥수수 미로·호박밭·대형 미끄럼틀·트랙터",
        ],
        "places": [
            {
                "name": "Richardson Adventure Farm",
                "addr": "909 English Prairie Rd, Spring Grove, IL 60081",
                "note": "2026 시즌 대략 9/12–11/1 · 사전 티켓",
            },
        ],
        "spend": [
            ("입장·액티비티(4명)", 220000),
            ("유류·주차", 60000),
            ("식사·간식", 140000),
        ],
        "media": [
            _yt("JCZ5e6tOTj8", "Richardson Adventure Farm corn maze"),
        ],
        "tips": "편한 신발·모기·진흙 대비. 평일 방문이 대기 적음.",
    },
    {
        "week": "w3",
        "date": "10/6(화)",
        "theme": "동물원 트릭오어트리트",
        "transport": "렌트카 / Metra",
        "distance": "시내→Brookfield Zoo ≈ 25–30km · 약 40–50분",
        "drive_note": "주차 넉넉한 편",
        "flow": [
            "Brookfield Zoo 가을 이벤트 · 동물 관람",
        ],
        "places": [
            {
                "name": "Brookfield Zoo",
                "addr": "8400 31st St, Brookfield, IL 60513",
                "note": "가을 한정 Boo!/핼러윈 프로그램은 연도별 공지",
            },
        ],
        "spend": [
            ("입장·주차(4명)", 180000),
            ("식사·기념품", 140000),
        ],
        "media": [
            _yt("Am9Xf5V3u-c", "Brookfield Zoo Chicago"),
        ],
        "tips": "이벤트 데이는 티켓 타임슬롯. 유모차·왜건 대여 확인.",
    },
    {
        "week": "w3",
        "date": "10/7(수)",
        "theme": "1,000개 호박 등불",
        "transport": "렌트카",
        "distance": "시내→Chicago Botanic Garden ≈ 40–45km · 약 45–60분",
        "drive_note": "저녁 입장 · 오후는 휴식",
        "flow": [
            "오전·오후 휴식",
            "저녁 Night of 1,000 Jack-O’-Lanterns",
        ],
        "places": [
            {
                "name": "Chicago Botanic Garden",
                "addr": "1000 Lake Cook Rd, Glencoe, IL 60022",
                "note": "야간 타임티켓 필수 · 2026 운영일은 공식 사이트 확인(해마다 변동)",
            },
        ],
        "spend": [
            ("야간 티켓(4명)", 200000),
            ("유류·주차·간식", 80000),
        ],
        "media": [
            _yt("0TOXqXh-p9s", "Night of 1,000 Jack-O’-Lanterns"),
        ],
        "tips": "어두워서 아이 손잡기·따뜻한 외투. 날짜가 안 맞으면 주말 슬롯으로 조정.",
    },
    {
        "week": "w3",
        "date": "10/8(목)",
        "theme": "쇼핑 & 마무리",
        "transport": "CTA / 우버",
        "distance": "시내 쇼핑권 5km 이내",
        "drive_note": "렌트는 짐·공항용으로 유지하거나 전날 반납 검토",
        "flow": [
            "기념품 쇼핑",
            "좋아하는 레스토랑 마무리 저녁",
        ],
        "places": [
            {
                "name": "Water Tower / Mag Mile 또는 로컬 숍",
                "addr": "835 N Michigan Ave 일대",
                "note": "딥디시 소스·기념품·아울렛은 취향껏",
            },
        ],
        "spend": [
            ("쇼핑", 200000),
            ("저녁 식사", 200000),
        ],
        "media": [],
        "tips": "짐 무게·액체 규정 체크. 익일 새벽 공항이면 일찍 종료.",
    },
    {
        "week": "w3",
        "date": "10/9(금)",
        "theme": "귀국",
        "transport": "렌트카 → ORD 반납",
        "distance": "Hyde Park→ORD ≈ 40–50km · 약 45–75분(교통 따라)",
        "drive_note": "새벽 출발편이면 전날 밤 이동·호텔도 검토",
        "flow": [
            "체크아웃",
            "렌트 반납",
            "ORD 출발",
        ],
        "places": [
            {
                "name": "O’Hare International Airport (ORD)",
                "addr": "10000 W O'Hare Ave, Chicago, IL 60666",
                "note": "국제선 3시간 전 · 렌트 셔틀 여유",
            },
        ],
        "spend": [
            ("공항 이동·주차/셔틀", 80000),
            ("공항 식사", 120000),
        ],
        "media": [],
        "tips": "귀국편 06:00대면 심야 이동. 반납 전 주유·사진 기록.",
    },
]


def _day_total(day: dict) -> int:
    return sum(a for _, a in day.get("spend") or [])


def plan_activity_total() -> int:
    return sum(_day_total(d) for d in DAYS)


def _media_html(media: list[dict]) -> str:
    if not media:
        return ""
    cards = []
    for m in media:
        cards.append(
            f"""
          <figure class="epic-media">
            <a class="epic-thumb-link" href="{m['watch']}" target="_blank" rel="noopener noreferrer">
              <img class="epic-thumb" src="{m['thumb']}" alt="{m['title']}" loading="lazy"
                onerror="this.style.display='none'" />
              <span class="epic-play">▶ YouTube</span>
            </a>
            <figcaption>
              <a href="{m['watch']}" target="_blank" rel="noopener noreferrer">{m['title']}</a>
            </figcaption>
            <details class="epic-embed-details">
              <summary>이 페이지에서 미리보기</summary>
              <div class="epic-embed-wrap">
                <iframe class="epic-embed" data-src="{m['embed']}" title="{m['title']}"
                  loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe>
              </div>
            </details>
          </figure>"""
        )
    return f'<div class="epic-media-grid">{"".join(cards)}</div>'


def _places_html(places: list[dict]) -> str:
    lis = []
    for p in places or []:
        lis.append(
            f"<li><strong>{p['name']}</strong>"
            f"<span class='muted'> · {p.get('addr', '')}</span>"
            f"<br><span class='epic-place-note'>{p.get('note', '')}</span></li>"
        )
    return f"<ul class='epic-places'>{''.join(lis)}</ul>"


def _spend_html(spend: list[tuple[str, int]]) -> str:
    rows = "".join(
        f"<tr><td>{label}</td><td class='price'>{won(amt) if amt else '—'}</td></tr>"
        for label, amt in spend
    )
    total = sum(a for _, a in spend)
    return f"""
    <table class="epic-spend">
      <thead><tr><th>예상 지출 (4명)</th><th>대략</th></tr></thead>
      <tbody>{rows}</tbody>
      <tfoot><tr><th>일 합계</th><th class="price">{won(total)}</th></tr></tfoot>
    </table>"""


def _flow_html(flow: list[str]) -> str:
    return "<ol class='epic-flow'>" + "".join(f"<li>{x}</li>" for x in flow) + "</ol>"


def _day_card(day: dict) -> str:
    total = _day_total(day)
    tip = day.get("tips") or ""
    tip_html = f'<p class="epic-tip">{tip}</p>' if tip else ""
    return f"""
    <article class="epic-day" data-epic-week="{day['week']}">
      <header class="epic-day-head">
        <div>
          <span class="epic-date">{day['date']}</span>
          <h3>{day['theme']}</h3>
        </div>
        <div class="epic-day-meta">
          <span class="epic-pill">{day['transport']}</span>
          <strong class="epic-day-total">{won(total)}</strong>
        </div>
      </header>
      <p class="epic-distance"><strong>거리·시간</strong> · {day['distance']}</p>
      <p class="muted epic-drive">{day.get('drive_note', '')}</p>
      <h4 class="epic-sub">동선</h4>
      {_flow_html(day.get('flow') or [])}
      <h4 class="epic-sub">장소 · 주소</h4>
      {_places_html(day.get('places') or [])}
      {_spend_html(day.get('spend') or [])}
      {tip_html}
      <h4 class="epic-sub">관련 영상 · 미리보기</h4>
      {_media_html(day.get('media') or []) or '<p class="muted">이 날은 별도 영상 없이 일정만 정리했습니다.</p>'}
    </article>"""


def _week_nav() -> str:
    btns = []
    for w in WEEKS:
        btns.append(
            f'<button type="button" class="epic-week-tab" data-epic-week-btn="{w["id"]}" aria-selected="false">'
            f'{w["label"]}<span>{w["dates"]}</span></button>'
        )
    btns.insert(
        0,
        '<button type="button" class="epic-week-tab active" data-epic-week-btn="all" aria-selected="true">'
        "전체<span>9/24 ~ 10/9</span></button>",
    )
    return f'<div class="epic-week-nav" role="tablist">{"".join(btns)}</div>'


def _week_cards() -> str:
    cards = []
    for w in WEEKS:
        cards.append(
            f"""
        <article class="epic-week-card" data-epic-week-card="{w['id']}">
          <p class="date-kicker">{w['label']}</p>
          <h3>{w['title']}</h3>
          <p class="muted">{w['dates']} · {w['mode']}</p>
          <p>{w['blurb']}</p>
        </article>"""
        )
    return f'<div class="epic-week-grid">{"".join(cards)}</div>'


def render_epic_plan() -> str:
    days_html = "".join(_day_card(d) for d in DAYS)
    note_total = plan_activity_total()
    return f"""
    <section class="route-hero card epic-hero">
      <div class="route-hero-copy">
        <p class="route-kicker">CHICAGO · 15N / 16D</p>
        <h2>슬리핑 비어 던스 포함 알찬 동선</h2>
        <p class="muted">2026.9.24(목) ~ 10.9(금) · 가족 4명 · 도심 대중교통 + 미시간 로드트립 + 가을 축제</p>
      </div>
      <div class="route-stats">
        <div class="route-stat">
          <span class="muted">현지 활동·로드트립 예상</span>
          <strong>{won(note_total)}</strong>
          <span class="muted">항공·시카고 장기숙박·전체 렌트료 별도 · 대략치</span>
        </div>
      </div>
    </section>

    <section class="card epic-summary">
      <h3>한눈에 보기</h3>
      <ul class="epic-summary-list">
        <li><strong>1주차 (9/24–28)</strong> 도심 핵심 · 박물관 · Jack’s Pumpkin · 옥토버페스트 · 리버크루즈 — <em>대중교통</em></li>
        <li><strong>2주차 (9/29–10/2)</strong> 렌트 픽업 → Saugatuck/Holland → Traverse City · Sleeping Bear · Apple Picking · Indiana Dunes 복귀</li>
        <li><strong>3주차 (10/3–9)</strong> Apple Fest · 어린이박물관 · Richardson Farm · Brookfield · 호박등불 · 출국</li>
      </ul>
      <p class="muted">※ 가을 축제·야간 호박전시는 <strong>해마다 날짜가 바뀝니다</strong>. 티켓 오픈 시 공식 사이트로 확정하세요.
      로드트립 숙박비는 일자 카드에 포함(트래버스시티 3박 대략). 시카고 Airbnb·국제선·렌트 일당은 다른 탭 금액을 더하세요.</p>
      <p class="muted">거리·유류·입장료는 2026 시즌 변동·환율(약 $1≈₩{USD_KRW}) 가정 대략치입니다.</p>
    </section>

    {_week_nav()}
    {_week_cards()}

    <div class="epic-stack">
      {days_html}
    </div>
    """


def epic_styles() -> str:
    return """
    .epic-hero {
      background: linear-gradient(135deg, #9a3412 0%, #c2410c 45%, #ea580c 100%);
      color: #fff;
    }
    .epic-hero .muted { color: rgba(255,255,255,.82); }
    .epic-hero .route-stat strong { color: #fff7ed; }
    .epic-summary { margin-bottom: 16px; }
    .epic-summary-list { margin: 8px 0 12px; padding-left: 1.2rem; line-height: 1.6; }
    .epic-week-nav {
      display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 14px;
    }
    .epic-week-tab {
      border: 1px solid var(--line); background: #fff; border-radius: 14px;
      padding: 10px 14px; cursor: pointer; font-weight: 700; color: #334155;
      display: flex; flex-direction: column; align-items: flex-start; gap: 2px;
      min-width: 120px;
    }
    .epic-week-tab span { font-size: 0.75rem; font-weight: 600; color: #64748b; }
    .epic-week-tab.active {
      background: #9a3412; color: #fff; border-color: #9a3412;
    }
    .epic-week-tab.active span { color: rgba(255,255,255,.85); }
    .epic-week-grid {
      display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px;
      margin-bottom: 18px;
    }
    .epic-week-card {
      border: 1px solid var(--line); border-radius: 14px; padding: 14px 16px;
      background: linear-gradient(180deg, #fff7ed 0%, #fff 55%);
    }
    .epic-week-card h3 { margin: 4px 0 6px; font-size: 1.05rem; }
    .epic-stack { display: grid; gap: 14px; }
    .epic-day {
      border: 1px solid var(--line); border-radius: 16px; padding: 16px 18px;
      background: #fff; box-shadow: 0 1px 2px rgba(15,23,42,.04);
    }
    .epic-day-head {
      display: flex; justify-content: space-between; gap: 12px; align-items: flex-start;
      margin-bottom: 8px;
    }
    .epic-day-head h3 { margin: 4px 0 0; font-size: 1.15rem; }
    .epic-date {
      display: inline-block; font-size: 0.78rem; font-weight: 800; letter-spacing: .03em;
      color: #9a3412; background: #ffedd5; border-radius: 999px; padding: 3px 9px;
    }
    .epic-day-meta { text-align: right; }
    .epic-pill {
      display: inline-block; font-size: 0.75rem; font-weight: 700;
      background: #f1f5f9; color: #475569; border-radius: 999px; padding: 3px 8px;
      margin-bottom: 6px;
    }
    .epic-day-total { display: block; font-size: 1.2rem; color: #c2410c; }
    .epic-distance { margin: 8px 0 4px; }
    .epic-drive { margin: 0 0 10px; font-size: 0.9rem; }
    .epic-sub { margin: 14px 0 6px; font-size: 0.92rem; color: #475569; }
    .epic-flow { margin: 0 0 8px; padding-left: 1.2rem; line-height: 1.55; }
    .epic-places { margin: 0; padding-left: 1.1rem; line-height: 1.45; }
    .epic-place-note { font-size: 0.88rem; color: #475569; }
    .epic-spend {
      width: 100%; border-collapse: collapse; margin: 10px 0 8px; font-size: 0.92rem;
    }
    .epic-spend th, .epic-spend td {
      border-bottom: 1px solid var(--line); padding: 7px 8px; text-align: left;
    }
    .epic-spend .price { text-align: right; font-weight: 700; white-space: nowrap; }
    .epic-tip {
      margin: 10px 0; padding: 10px 12px; background: #fff7ed; border-left: 3px solid #ea580c;
      font-size: 0.9rem; line-height: 1.5;
    }
    .epic-media-grid {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px;
    }
    .epic-media {
      margin: 0; border: 1px solid var(--line); border-radius: 12px; overflow: hidden;
      background: #fafbfc;
    }
    .epic-thumb-link {
      position: relative; display: block; aspect-ratio: 16/9; background: #0f172a;
    }
    .epic-thumb { width: 100%; height: 100%; object-fit: cover; display: block; }
    .epic-play {
      position: absolute; left: 10px; bottom: 10px; background: rgba(0,0,0,.72); color: #fff;
      font-size: 0.72rem; font-weight: 800; padding: 4px 8px; border-radius: 999px;
    }
    .epic-media figcaption { padding: 8px 10px; font-size: 0.84rem; font-weight: 700; }
    .epic-media figcaption a { color: #9a3412; text-decoration: none; }
    .epic-embed-details { border-top: 1px solid var(--line); padding: 8px 10px 10px; }
    .epic-embed-details summary {
      cursor: pointer; font-size: 0.8rem; font-weight: 700; color: #475569;
    }
    .epic-embed-wrap { margin-top: 8px; position: relative; padding-top: 56.25%; }
    .epic-embed {
      position: absolute; inset: 0; width: 100%; height: 100%; border: 0; border-radius: 8px;
    }
    @media (max-width: 800px) {
      .epic-week-grid { grid-template-columns: 1fr; }
      .epic-day-head { flex-direction: column; }
      .epic-day-meta { text-align: left; }
    }
    """


def epic_scripts() -> str:
    return """
    (function() {
      const tabs = document.querySelectorAll('[data-epic-week-btn]');
      const days = document.querySelectorAll('.epic-day');
      const cards = document.querySelectorAll('[data-epic-week-card]');
      if (!tabs.length) return;
      function show(week) {
        tabs.forEach(t => {
          const on = t.dataset.epicWeekBtn === week;
          t.classList.toggle('active', on);
          t.setAttribute('aria-selected', on ? 'true' : 'false');
        });
        days.forEach(d => {
          d.hidden = !(week === 'all' || d.dataset.epicWeek === week);
        });
        cards.forEach(c => {
          c.hidden = !(week === 'all' || c.dataset.epicWeekCard === week);
        });
      }
      tabs.forEach(t => t.addEventListener('click', () => show(t.dataset.epicWeekBtn)));
      document.querySelectorAll('.epic-embed-details').forEach(det => {
        det.addEventListener('toggle', () => {
          if (!det.open) return;
          const iframe = det.querySelector('iframe[data-src]');
          if (iframe && !iframe.src) iframe.src = iframe.dataset.src;
        });
      });
    })();
    """
