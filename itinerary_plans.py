#!/usr/bin/env python3
"""Chicago 10-day + East Coast 3-day itinerary content for the travel page."""

from __future__ import annotations

from urllib.parse import quote_plus


def fmt_won(amount: int | None) -> str:
    if amount is None:
        return "-"
    return f"₩{amount:,}"


# Booked Airbnb — transport estimates are from this home base.
CHI_HOME = {
    "name": "숙소 (Hyde Park)",
    "address": "6115 South Langley Avenue, Chicago, IL 60637",
    "area": "Woodlawn · UChicago 인근",
}

# Clickable Chicago destinations → parking / Uber / CTA·Metra guidance.
# Fares are approximate KRW (family of 4, 2026 시즌 변동 가능).
def _maps(q: str) -> str:
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(q)}"


CHI_PLACES: dict[str, dict] = {
    "ord_pickup": {
        "name": "ORD 도착 · 렌트카 픽업",
        "address": "10000 W O'Hare Ave, Chicago, IL 60666",
        "drive_min": "공항 내 셔틀/워크",
        "parking": {
            "name": "렌트카 센터 (각 업체 픽업 구역)",
            "address": "O'Hare Rental Car Facility · 공항 안내 전광판/앱 확인",
            "note": "터미널 → Airport Transit System(ATS) 또는 업체 셔틀 → Rental Car Center. 별도 관광 주차 불필요.",
            "maps": _maps("O'Hare Rental Car Center"),
        },
        "uber": {
            "dropoff": "숙소로 이동 시",
            "address": CHI_HOME["address"],
            "fare": "ORD→숙소 편도 약 ₩55,000–80,000 (UberX) · XL ₩75,000–110,000",
            "note": "렌트 픽업이 목표면 우버 대신 렌트 셔틀. 우버 승차는 Terminal 픽업존.",
        },
        "transit": {
            "route": "CTA Blue Line (공항) → 시내 환승 (렌트 없을 때)",
            "steps": [
                "터미널 내 CTA Blue Line ‘O'Hare’역",
                "시내(Clark/Lake 등) 환승 후 Green/버스 → Hyde Park",
                "짐·아이 있으면 렌트/우버 권장",
            ],
            "fare": "CTA 1인 $2.50 · 4명 편도 약 ₩14,000 + Hyde Park 환승",
            "note": "귀국일 ORD 이동은 아래 ‘ORD 이동’ 카드 참고.",
        },
    },
    "home_checkin": {
        "name": "숙소 체크인",
        "address": CHI_HOME["address"],
        "drive_min": "—",
        "parking": {
            "name": "숙소 인근 노상/지정 주차",
            "address": "6115 S Langley Ave 주변 (구역 표지 확인)",
            "note": "거주 허가(permit) 구역·시간제 표지 확인. 가능하면 숙소 호스트 안내에 따르세요.",
            "maps": _maps(CHI_HOME["address"]),
        },
        "uber": {
            "dropoff": CHI_HOME["name"],
            "address": CHI_HOME["address"],
            "fare": "시내→숙소는 출발지에 따라 상이",
            "note": "하차 주소: 6115 S Langley Ave, Chicago",
        },
        "transit": {
            "route": "Metra Electric 59th / CTA #2·#6 + 도보",
            "steps": [
                "Metra Electric → 59th St (University of Chicago) 하차",
                "동쪽으로 Langley Ave 도보 약 10–15분",
                "또는 CTA 버스 정류장에서 하차 후 도보",
            ],
            "fare": "Metra/CTA 편도 1인 약 $2.50–6",
            "note": "짐 많으면 우버·렌트 권장.",
        },
    },
    "millennium": {
        "name": "Millennium Park · Cloud Gate",
        "address": "201 E Randolph St, Chicago, IL 60601",
        "drive_min": "약 25–40분",
        "parking": {
            "name": "Millennium Park Garage (Grant Park North)",
            "address": "5 S Columbus Dr, Chicago, IL 60601",
            "note": "Cloud Gate·콩 조형물 도보 5분. 종일 대략 $30–45. Grant Park South Garage(221 S Columbus)도 대안.",
            "maps": _maps("Millennium Park Garage 5 S Columbus Dr Chicago"),
        },
        "uber": {
            "dropoff": "Cloud Gate / The Bean",
            "address": "Millennium Park, 201 E Randolph St, Chicago, IL 60601",
            "fare": "편도 약 ₩40,000–55,000 (UberX) · 4명 XL 약 ₩55,000–75,000",
            "note": "Randolph St / Michigan Ave 인근 하차. 혼잡·행사 시 할증.",
        },
        "transit": {
            "route": "Metra Electric → Millennium 또는 CTA #6 Jackson Park Express",
            "steps": [
                "숙소 → Metra 59th St (도보/짧은 우버)",
                "Metra Electric northbound → Millennium Station",
                "도보 5분 Cloud Gate",
                "대안: CTA 버스 #6 → Michigan & Randolph",
            ],
            "fare": "Metra 편도 약 $4–6/인 · CTA $2.50/인 · 4명 왕복 대략 ₩55,000–85,000",
            "note": "Ventra 앱/카드. CTA는 만 7세 미만 보호자 동반 시 무료.",
        },
    },
    "art_institute": {
        "name": "Art Institute of Chicago",
        "address": "111 S Michigan Ave, Chicago, IL 60603",
        "drive_min": "약 25–40분",
        "parking": {
            "name": "Grant Park South Garage 또는 Millennium Park Garage",
            "address": "221 S Columbus Dr / 5 S Columbus Dr, Chicago",
            "note": "미술관 동편 지하·그랜트파크 주차장. 종일 약 $30–45. Michigan Ave 노상은 짧고 비쌈.",
            "maps": _maps("Grant Park South Garage Chicago"),
        },
        "uber": {
            "dropoff": "Art Institute of Chicago main entrance",
            "address": "111 S Michigan Ave, Chicago, IL 60603",
            "fare": "편도 약 ₩40,000–55,000 · XL ₩55,000–75,000",
            "note": "Michigan Ave 쪽 하차 후 계단/입구.",
        },
        "transit": {
            "route": "Metra → Millennium + 도보 또는 CTA Brown/Green/Orange/Pink → Adams/Wabash",
            "steps": [
                "Metra Electric → Millennium Station → 도보 8분",
                "또는 CTA Loop ‘Adams/Wabash’ 하차 → 도보 3분",
            ],
            "fare": "편도 CTA $2.50/인 · 4명 왕복 약 ₩28,000 + Hyde Park 접근비",
            "note": "아이 동반 시 Metra가 좌석·짐에 편할 수 있음.",
        },
    },
    "riverwalk": {
        "name": "Chicago Riverwalk",
        "address": "Chicago Riverwalk, Chicago, IL 60601",
        "drive_min": "약 25–40분",
        "parking": {
            "name": "Marina City / Wacker 인근 유료 주차장",
            "address": "300 N State St 인근 또는 233 E Wacker Dr garage",
            "note": "리버워크는 강변 보행로라 자차는 근처 건물 주차 후 도보. 종일 $35–55 흔함.",
            "maps": _maps("Chicago Riverwalk parking garage"),
        },
        "uber": {
            "dropoff": "Chicago Riverwalk · Michigan Ave bridge",
            "address": "401 N Michigan Ave, Chicago, IL 60611",
            "fare": "편도 약 ₩42,000–58,000 · XL ₩58,000–78,000",
            "note": "Michigan Ave Bridge / Wacker Dr 하차 후 계단으로 강변.",
        },
        "transit": {
            "route": "CTA Red Line → Grand 또는 Brown Line → State/Lake + 도보",
            "steps": [
                "Hyde Park에서 #6 또는 Metra→CTA 환승",
                "State/Lake · Clark/Lake · Grand(Red) 하차",
                "도보로 리버워크 진입",
            ],
            "fare": "CTA $2.50/인 · 4명 왕복 약 ₩28,000+",
            "note": "루프·매그마일 일정과 묶어 이동하면 환승 최소.",
        },
    },
    "navy_pier": {
        "name": "Navy Pier",
        "address": "600 E Grand Ave, Chicago, IL 60611",
        "drive_min": "약 30–45분",
        "parking": {
            "name": "Navy Pier Parking Garage",
            "address": "600 E Grand Ave, Chicago, IL 60611",
            "note": "피어 건물 주차장. 시간제·이벤트 시 할증. 종일 대략 $40–60. 저녁 야경은 만차 주의.",
            "maps": _maps("Navy Pier Parking Garage"),
        },
        "uber": {
            "dropoff": "Navy Pier main entrance",
            "address": "600 E Grand Ave, Chicago, IL 60611",
            "fare": "편도 약 ₩45,000–65,000 · XL ₩65,000–90,000",
            "note": "Grand Ave 입구 하차. 피어 끝 관람차·배 일정 확인.",
        },
        "transit": {
            "route": "CTA #2 / #29 / #65 버스 또는 Red Line Grand + 버스",
            "steps": [
                "시내까지 Metra/CTA 후",
                "버스 #2 Hyde Park Express(일부 시간) 또는 #29 State → Navy Pier",
                "Red Line Grand 하차 후 #65 등 환승",
            ],
            "fare": "CTA $2.50/인 · 4명 왕복 약 ₩28,000–40,000",
            "note": "밤늦은 귀가면 우버가 편함.",
        },
    },
    "shedd": {
        "name": "Shedd Aquarium",
        "address": "1200 S Lake Shore Dr, Chicago, IL 60605",
        "drive_min": "약 20–35분",
        "parking": {
            "name": "Museum Campus North Garage (Adler/Shedd)",
            "address": "1200 S Lake Shore Dr / Museum Campus, Chicago",
            "note": "수족관·Adler 공용 캠퍼스 주차. 종일 약 $30–40. 예약(온라인) 가능 시 유리.",
            "maps": _maps("Shedd Aquarium parking garage"),
        },
        "uber": {
            "dropoff": "Shedd Aquarium entrance",
            "address": "1200 S Lake Shore Dr, Chicago, IL 60605",
            "fare": "편도 약 ₩35,000–50,000 · XL ₩50,000–70,000",
            "note": "Museum Campus 드롭오프 존.",
        },
        "transit": {
            "route": "Metra → Roosevelt + 도보/버스 또는 CTA Roosevelt + #146/#130",
            "steps": [
                "Metra Electric → Museum Campus/11th St 또는 Roosevelt 인근",
                "CTA Red/Orange/Green Roosevelt → 버스 #146/#130 Museum Campus",
                "도보 시 Roosevelt에서 동쪽으로 15–20분",
            ],
            "fare": "CTA/Metra 편도 약 $2.50–6/인 · 4명 왕복 약 ₩45,000–70,000",
            "note": "Field·Adler와 같은 날이면 자차·하루 주차가 효율적.",
        },
    },
    "field_adler": {
        "name": "Field Museum / Adler Planetarium",
        "address": "1400 S Lake Shore Dr / 1300 S Lake Shore Dr, Chicago, IL 60605",
        "drive_min": "약 20–35분",
        "parking": {
            "name": "Museum Campus 주차장 (Field East / Adler)",
            "address": "1400 S Lake Shore Dr, Chicago, IL 60605",
            "note": "Field Museum East Garage 또는 Adler lot. Shedd와 하루 티켓·주차 공유하기 좋음. 약 $30–40.",
            "maps": _maps("Field Museum East Garage Chicago"),
        },
        "uber": {
            "dropoff": "Field Museum 또는 Adler Planetarium",
            "address": "1400 S Lake Shore Dr, Chicago, IL 60605",
            "fare": "편도 약 ₩35,000–50,000 · XL ₩50,000–70,000",
            "note": "두 곳 도보 이동 가능 · 한 번 하차 후 캠퍼스 워킹.",
        },
        "transit": {
            "route": "Shedd와 동일 · Museum Campus 버스",
            "steps": [
                "CTA Roosevelt + Museum Campus 버스",
                "또는 Metra + 도보",
            ],
            "fare": "CTA $2.50/인 · 4명 왕복 약 ₩28,000+",
            "note": "Adler는 캠퍼스 끝이라 도보 추가 10분.",
        },
    },
    "grant_park": {
        "name": "Grant Park",
        "address": "337 E Randolph St, Chicago, IL 60601",
        "drive_min": "약 25–40분",
        "parking": {
            "name": "Grant Park North / South Garage",
            "address": "25 N Michigan Ave 인근 · Columbus Dr 지하",
            "note": "Millennium과 동일 주차 인프라. 공원 산책이면 Millennium Garage 추천.",
            "maps": _maps("Grant Park North Garage Chicago"),
        },
        "uber": {
            "dropoff": "Grant Park / Buckingham Fountain",
            "address": "301 S Columbus Dr, Chicago, IL 60605",
            "fare": "편도 약 ₩40,000–55,000",
            "note": "분수(Buckingham) 기준으로 하차 지정 가능.",
        },
        "transit": {
            "route": "Metra Millennium 또는 CTA Loop",
            "steps": ["Millennium Station 하차 후 남쪽 Grant Park 산책"],
            "fare": "Metra/CTA 편도 약 $2.50–6/인",
            "note": "미술관·밀레니엄과 묶기 좋음.",
        },
    },
    "msi": {
        "name": "Museum of Science and Industry",
        "address": "5700 S Lake Shore Dr, Chicago, IL 60637",
        "drive_min": "약 8–15분",
        "parking": {
            "name": "MSI West Parking Lot / Garage",
            "address": "5700 S Lake Shore Dr, Chicago, IL 60637",
            "note": "박물관 서편 주차. 입장객 요금 대략 $25–30대. 숙소에서 매우 가까움.",
            "maps": _maps("Museum of Science and Industry parking"),
        },
        "uber": {
            "dropoff": "MSI main entrance",
            "address": "5700 S Lake Shore Dr, Chicago, IL 60637",
            "fare": "편도 약 ₩12,000–20,000 · XL ₩18,000–28,000",
            "note": "짧은 거리 · 날씨 나쁘면 우버가 편함.",
        },
        "transit": {
            "route": "도보·버스 #6 / #2 또는 Metra 55th-56th-57th",
            "steps": [
                "숙소에서 동쪽으로 Lake Shore 방면 도보 약 20–30분",
                "또는 CTA #6/#2 → MSI 정류장",
                "Metra 55th-56th-57th 하차 후 도보",
            ],
            "fare": "버스 $2.50/인 · 가까우면 도보 무료",
            "note": "가족·유모치면 짧은 우버/자차 추천.",
        },
    },
    "uchicago": {
        "name": "University of Chicago 캠퍼스",
        "address": "5801 S Ellis Ave, Chicago, IL 60637",
        "drive_min": "약 5–10분",
        "parking": {
            "name": "캠퍼스 유료 주차 / 주변 미터기",
            "address": "Ellis Ave · University Ave 일대",
            "note": "방문객 주차는 Campus North Garage 등. 짧은 산책이면 숙소 주차 후 도보가 나을 수 있음.",
            "maps": _maps("University of Chicago Campus North Parking"),
        },
        "uber": {
            "dropoff": "UChicago Main Quadrangle",
            "address": "5801 S Ellis Ave, Chicago, IL 60637",
            "fare": "편도 약 ₩8,000–15,000",
            "note": "대부분 도보 가능 거리.",
        },
        "transit": {
            "route": "도보 우선",
            "steps": ["숙소에서 캠퍼스까지 도보 약 15–25분", "필요 시 버스 #172/#171 캠퍼스 셔틀성 노선"],
            "fare": "도보 무료 · 버스 $2.50",
            "note": "근처 카페·서점(57th)과 함께.",
        },
    },
    "promontory": {
        "name": "Promontory Point",
        "address": "5491 S Shore Dr, Chicago, IL 60615",
        "drive_min": "약 10–15분",
        "parking": {
            "name": "Promontory Point / 인근 노상·롯",
            "address": "5491 S Shore Dr, Chicago, IL 60615",
            "note": "포인트 입구 소규모 주차. 주말 만차 시 MSI·호숫가 도로 대안. 무료/저가 구간 표지 확인.",
            "maps": _maps("Promontory Point Chicago parking"),
        },
        "uber": {
            "dropoff": "Promontory Point",
            "address": "5491 S Shore Dr, Chicago, IL 60615",
            "fare": "편도 약 ₩12,000–22,000",
            "note": "피크닉·호수 뷰.",
        },
        "transit": {
            "route": "버스 #6 또는 도보+짧은 우버",
            "steps": ["#6 Jackson Park Express → 55th/Lake Shore 인근", "도보로 포인트 진입"],
            "fare": "버스 $2.50/인",
            "note": "짐·아이 간식이면 자차/우버 편함.",
        },
    },
    "lp_zoo": {
        "name": "Lincoln Park Zoo",
        "address": "2001 N Clark St, Chicago, IL 60614",
        "drive_min": "약 35–55분",
        "parking": {
            "name": "Lincoln Park Zoo Parking Lots (North/South)",
            "address": "2001 N Clark St / Stockton Dr, Chicago, IL 60614",
            "note": "동물원 공식 주차. 대략 $20–35. 주말 오전 일찍 도착 권장. 거리 미터기는 제한적.",
            "maps": _maps("Lincoln Park Zoo parking"),
        },
        "uber": {
            "dropoff": "Lincoln Park Zoo East Gate / Café Brauer",
            "address": "2001 N Clark St, Chicago, IL 60614",
            "fare": "편도 약 ₩50,000–70,000 · XL ₩70,000–95,000",
            "note": "북쪽으로 거리 김 · 왕복 우버면 예산 크게 증가.",
        },
        "transit": {
            "route": "CTA Red Line → Fullerton/North/Clark + 버스 또는 #22/#36",
            "steps": [
                "시내까지 Metra/CTA 후 Red Line northbound",
                "Fullerton 또는 North/Clybourn 하차 후 버스·도보",
                "버스 #151/#156 등 Lake Shore/Stockton 방면",
            ],
            "fare": "CTA 환승 포함 편도 약 $2.50–5/인 · 4명 왕복 약 ₩45,000–70,000",
            "note": "가족·하루 일정이면 자차 하루 주차가 편한 편.",
        },
    },
    "lp_conservatory": {
        "name": "Lincoln Park Conservatory",
        "address": "2391 N Stockton Dr, Chicago, IL 60614",
        "drive_min": "약 35–55분",
        "parking": {
            "name": "Lincoln Park Zoo / Conservatory 인근 주차",
            "address": "Stockton Dr · Zoo South Lot",
            "note": "동물원 주차 후 도보 5–10분. 별도 소규모 롯 있음.",
            "maps": _maps("Lincoln Park Conservatory parking"),
        },
        "uber": {
            "dropoff": "Lincoln Park Conservatory",
            "address": "2391 N Stockton Dr, Chicago, IL 60614",
            "fare": "편도 약 ₩50,000–70,000",
            "note": "동물원과 같은 날 묶기.",
        },
        "transit": {
            "route": "동물원과 동일 동선",
            "steps": ["Lincoln Park Zoo에서 도보 이동"],
            "fare": "추가 교통비 없음(도보)",
            "note": "동물원 일정에 포함.",
        },
    },
    "north_ave_beach": {
        "name": "North Avenue Beach",
        "address": "1600 N Lake Shore Dr, Chicago, IL 60610",
        "drive_min": "약 35–50분",
        "parking": {
            "name": "North Avenue Beach 유료 롯 / 인근",
            "address": "1600 N Lake Shore Dr, Chicago, IL 60610",
            "note": "해변 시즌 유료 주차. 만차 시 Lincoln Park 쪽 주차 후 도보.",
            "maps": _maps("North Avenue Beach parking Chicago"),
        },
        "uber": {
            "dropoff": "North Avenue Beach",
            "address": "1600 N Lake Shore Dr, Chicago, IL 60610",
            "fare": "편도 약 ₩48,000–68,000",
            "note": "링컨파크 일정과 연계.",
        },
        "transit": {
            "route": "CTA #151 Sheridan 또는 Red Line + 도보",
            "steps": ["Red Line North/Clybourn 또는 Clark/Division 후 버스·도보", "#151 → North Ave Beach"],
            "fare": "CTA $2.50/인",
            "note": "수영·모래놀이 짐이면 자차/우버.",
        },
    },
    "arch_cruise": {
        "name": "Architecture River Cruise",
        "address": "Chicago's First Lady · 112 E Wacker Dr 또는 Wendella 하역장",
        "drive_min": "약 25–40분",
        "parking": {
            "name": "Wacker / Michigan 인근 주차장",
            "address": "233 E Wacker Dr · 155 N Michigan Ave garage 등",
            "note": "선사(First Lady, Wendella, Shoreline)마다 승선지가 다름 · 예약 확인서의 dock 주소로 주차. 종일 $35–55.",
            "maps": _maps("112 E Wacker Dr Chicago parking"),
        },
        "uber": {
            "dropoff": "예약 선사 승선 부두",
            "address": "예: 112 E Wacker Dr, Chicago, IL 60601",
            "fare": "편도 약 ₩42,000–58,000",
            "note": "출항 30–40분 전 도착. 우버가 주차 스트레스 적음.",
        },
        "transit": {
            "route": "CTA State/Lake · Clark/Lake + 도보",
            "steps": ["루프 역 하차 후 Wacker Dr 강변으로 도보 5–10분"],
            "fare": "CTA $2.50/인",
            "note": "예약 시간 엄수 · 겨울·바람 대비.",
        },
    },
    "loop": {
        "name": "The Loop 워킹",
        "address": "The Loop, Chicago, IL 60602",
        "drive_min": "약 25–40분",
        "parking": {
            "name": "Loop 공용 주차장 (예: Self Park / Grant Park)",
            "address": "200 N Dearborn · Millennium Garage 등",
            "note": "루프는 주차비 높음($40+). 가능하면 교외·하이드파크에서 대중교통·우버 권장.",
            "maps": _maps("Grant Park North Garage Chicago"),
        },
        "uber": {
            "dropoff": "Chicago Loop · State & Madison",
            "address": "1 N State St, Chicago, IL 60602",
            "fare": "편도 약 ₩40,000–55,000",
            "note": "도보 관광 중심 · 하차 후 워킹.",
        },
        "transit": {
            "route": "Metra Electric → Millennium / CTA Loop",
            "steps": ["Metra → Millennium Station", "또는 CTA로 Clark/Lake·Washington 하차"],
            "fare": "Metra/CTA 편도 약 $2.50–6/인",
            "note": "루프는 대중교통이 가장 효율적.",
        },
    },
    "willis": {
        "name": "Willis Tower Skydeck",
        "address": "233 S Wacker Dr, Chicago, IL 60606",
        "drive_min": "약 25–40분",
        "parking": {
            "name": "Self Park · 211 W Adams / 인근 타워 주차",
            "address": "211 W Adams St, Chicago, IL 60606",
            "note": "Skydeck 공식 제휴·인근 Self Park. 사전 요금 확인. 대략 $40–55.",
            "maps": _maps("Willis Tower parking 211 W Adams"),
        },
        "uber": {
            "dropoff": "Willis Tower Skydeck entrance",
            "address": "233 S Wacker Dr, Chicago, IL 60606",
            "fare": "편도 약 ₩40,000–55,000",
            "note": "Jackson Blvd 입구 쪽 하차 안내 따름.",
        },
        "transit": {
            "route": "CTA Brown/Orange/Pink/Purple → Quincy 또는 Clinton",
            "steps": ["Quincy역 하차 후 도보 3분", "Metra 이용 시 Union Station → 도보 10분"],
            "fare": "CTA $2.50/인",
            "note": "사전 입장권·보안 검색 줄 감안.",
        },
    },
    "hancock": {
        "name": "360 CHICAGO / John Hancock",
        "address": "875 N Michigan Ave, Chicago, IL 60611",
        "drive_min": "약 30–45분",
        "parking": {
            "name": "875 N Michigan Ave Building Garage / 인근",
            "address": "875 N Michigan Ave, Chicago, IL 60611",
            "note": "빌딩 지하·인근 유료 주차. Magnificent Mile 요금 높음($45–60). Water Tower Place garage 대안.",
            "maps": _maps("875 N Michigan Ave parking"),
        },
        "uber": {
            "dropoff": "360 CHICAGO",
            "address": "875 N Michigan Ave, Chicago, IL 60611",
            "fare": "편도 약 ₩45,000–65,000 · XL ₩65,000–85,000",
            "note": "매그마일 쇼핑과 같은 날 우버 왕복이 주차보다 쌀 수 있음.",
        },
        "transit": {
            "route": "CTA Red Line → Chicago 하차 + 도보",
            "steps": ["Red Line ‘Chicago’ 하차", "동쪽으로 Michigan Ave 도보 10분"],
            "fare": "CTA $2.50/인 · 4명 왕복 약 ₩28,000+",
            "note": "버스 #146/#151도 Michigan Ave 경유.",
        },
    },
    "water_tower": {
        "name": "Water Tower · 쇼핑",
        "address": "163 E Pearson St, Chicago, IL 60611",
        "drive_min": "약 30–45분",
        "parking": {
            "name": "Water Tower Place Garage",
            "address": "845 N Michigan Ave, Chicago, IL 60611",
            "note": "몰 이용 시 주차 검증(validation) 가능. 종일 $40–55대.",
            "maps": _maps("Water Tower Place parking garage"),
        },
        "uber": {
            "dropoff": "Chicago Water Tower / Water Tower Place",
            "address": "845 N Michigan Ave, Chicago, IL 60611",
            "fare": "편도 약 ₩45,000–65,000",
            "note": "360 CHICAGO와 도보권.",
        },
        "transit": {
            "route": "CTA Red Line Chicago + 도보",
            "steps": ["Red Line Chicago → Michigan Ave 도보"],
            "fare": "CTA $2.50/인",
            "note": "매그마일 일정과 통합.",
        },
    },
    "mag_mile_shops": {
        "name": "American Girl / Lego Store",
        "address": "American Girl 835 N Michigan · Lego 520 N Michigan",
        "drive_min": "약 30–45분",
        "parking": {
            "name": "Water Tower Place / 520 N Michigan 인근",
            "address": "845 N Michigan Ave 또는 520 N Michigan Ave",
            "note": "두 매장 도보 거리. Water Tower 주차 후 이동 추천.",
            "maps": _maps("Water Tower Place Chicago"),
        },
        "uber": {
            "dropoff": "Water Tower Place",
            "address": "845 N Michigan Ave, Chicago, IL 60611",
            "fare": "편도 약 ₩45,000–65,000",
            "note": "아이 쇼핑·짐이면 우버 왕복 고려.",
        },
        "transit": {
            "route": "CTA Red Line Chicago",
            "steps": ["Chicago역 하차 후 Michigan Ave 도보"],
            "fare": "CTA $2.50/인",
            "note": "영업시간 확인.",
        },
    },
    "oak_park": {
        "name": "Oak Park (Frank Lloyd Wright)",
        "address": "209 S Oak Park Ave / 951 Chicago Ave, Oak Park, IL 60302",
        "drive_min": "약 40–60분",
        "parking": {
            "name": "Oak Park 마을 공영·미터 / FLW Trust 방문객 주차",
            "address": "951 Chicago Ave, Oak Park, IL 60302 (Home & Studio 인근)",
            "note": "자차 데이트립에 적합. 마을 미터·garage. Home and Studio 투어 예약 필수.",
            "maps": _maps("Frank Lloyd Wright Home and Studio parking"),
        },
        "uber": {
            "dropoff": "Frank Lloyd Wright Home and Studio",
            "address": "951 Chicago Ave, Oak Park, IL 60302",
            "fare": "편도 약 ₩55,000–85,000 · 왕복·대기비 커서 비추천",
            "note": "당일 왕복이면 렌트카가 훨씬 유리.",
        },
        "transit": {
            "route": "CTA Green Line → Oak Park 또는 Harlem/Lake",
            "steps": [
                "Green Line westbound → Oak Park 하차",
                "도보/버스 short hop → Home & Studio·Unity Temple",
            ],
            "fare": "CTA $2.50/인 · 4명 왕복 약 ₩28,000",
            "note": "짐 없이 건축 투어만이면 Green Line도 가능.",
        },
    },
    "outlet": {
        "name": "교외 아울렛 / 지역 공원",
        "address": "예: Fashion Outlets of Chicago, 5220 Fashion Outlets Way, Rosemont, IL 60018",
        "drive_min": "약 40–55분 (Rosemont)",
        "parking": {
            "name": "아울렛·공원 무료/공용 주차",
            "address": "해당 시설 주차장",
            "note": "자차 추천. Rosemont 아울렛은 무료 주차. 지역 주립공원도 주차비 소액인 경우 많음.",
            "maps": _maps("Fashion Outlets of Chicago"),
        },
        "uber": {
            "dropoff": "목적 시설명",
            "address": "예약·검색한 주소",
            "fare": "편도 약 ₩55,000–90,000 · 왕복 부담 큼",
            "note": "근교는 렌트카가 원칙.",
        },
        "transit": {
            "route": "CTA Blue Line → Rosemont + 짧은 버스/우버",
            "steps": ["Blue Line Rosemont", "아울렛 셔틀·우버 연결"],
            "fare": "CTA $2.50 + 연결 우버",
            "note": "가족 쇼핑·짐이면 자차.",
        },
    },
    "home_evening": {
        "name": "저녁은 숙소 근처",
        "address": CHI_HOME["address"],
        "drive_min": "—",
        "parking": {
            "name": "숙소 주차",
            "address": CHI_HOME["address"],
            "note": "추가 이동 없음.",
            "maps": _maps(CHI_HOME["address"]),
        },
        "uber": {
            "dropoff": "숙소",
            "address": CHI_HOME["address"],
            "fare": "—",
            "note": "근처 식당은 도보·짧은 우버.",
        },
        "transit": {
            "route": "도보",
            "steps": ["53rd/57th St 식당가로 도보·버스"],
            "fare": "도보 또는 버스 $2.50",
            "note": "여유 저녁.",
        },
    },
    "revisit": {
        "name": "좋아하는 장소 재방문",
        "address": "일정에서 고른 목적지",
        "drive_min": "목적지에 따름",
        "parking": {
            "name": "해당 목적지 주차 안내 참고",
            "address": "재방문 장소의",
            "note": "밀레니엄·MSI·링컨파크 등 이미 열어본 카드의 주차 정보 재사용.",
            "maps": _maps("Chicago IL"),
        },
        "uber": {
            "dropoff": "선택 목적지",
            "address": "앱에서 장소명 검색",
            "fare": "하이드파크 기준 시내 ₩35,000–70,000대",
            "note": "왕복 예산 미리 잡기.",
        },
        "transit": {
            "route": "Metra Electric / CTA #6 · Red·Green",
            "steps": ["자주 쓰는 동선: Metra→Millennium 또는 #6→Michigan Ave"],
            "fare": "편도 $2.50–6/인",
            "note": "Ventra 잔액 충전.",
        },
    },
    "lakefront_picnic": {
        "name": "호숫가 피크닉",
        "address": "57th Street Beach / Promontory Point, Chicago, IL 60637",
        "drive_min": "약 8–15분",
        "parking": {
            "name": "57th Street Beach / Point 인근",
            "address": "5700 S Lake Shore Dr 일대",
            "note": "MSI·포인트와 공유 주차. 주말 오전 유리.",
            "maps": _maps("57th Street Beach Chicago"),
        },
        "uber": {
            "dropoff": "57th Street Beach",
            "address": "5700 S Lake Shore Dr, Chicago, IL 60637",
            "fare": "편도 약 ₩12,000–20,000",
            "note": "피크닉 짐이면 우버/자차.",
        },
        "transit": {
            "route": "도보 또는 버스 #6",
            "steps": ["숙소에서 호수 방면 도보", "#6 하차 후 도보"],
            "fare": "도보 무료 · 버스 $2.50",
            "note": "날씨·바람 챙기기.",
        },
    },
    "deep_dish": {
        "name": "시카고 딥디시 피자",
        "address": "예: Giordano's / Lou Malnati's (다중 지점)",
        "drive_min": "지점별 10–35분",
        "parking": {
            "name": "해당 지점 발렛·인근 롯",
            "address": "예약 지점 주소",
            "note": "시내 지점은 주차비 높음. Hyde Park·South Loop 지점 추천.",
            "maps": _maps("Lou Malnati's Hyde Park Chicago"),
        },
        "uber": {
            "dropoff": "예약한 피자 레스토랑",
            "address": "앱/예약 확인 주소",
            "fare": "근거리 ₩12,000–25,000 · 시내 ₩40,000–60,000",
            "note": "대기 길면 테이크아웃+숙소.",
        },
        "transit": {
            "route": "지점별 CTA/버스",
            "steps": ["예약 지점 기준으로 Google Maps 대중교통"],
            "fare": "CTA $2.50/인",
            "note": "주말 저녁 예약 권장.",
        },
    },
    "checkout": {
        "name": "숙소 체크아웃",
        "address": CHI_HOME["address"],
        "drive_min": "—",
        "parking": {
            "name": "숙소 주차 정리 후 ORD 이동",
            "address": CHI_HOME["address"],
            "note": "체크아웃 오전 11:00 · 짐 싣고 렌트 반납 동선 확보.",
            "maps": _maps(CHI_HOME["address"]),
        },
        "uber": {
            "dropoff": "ORD (렌트 없을 때)",
            "address": "Chicago O'Hare International Airport",
            "fare": "숙소→ORD 약 ₩55,000–80,000",
            "note": "렌트 반납이면 자차로 ORD.",
        },
        "transit": {
            "route": "비추천(짐) · 비상시 Metra+Blue",
            "steps": ["짐 있으면 우버/렌트"],
            "fare": "—",
            "note": "출국 당일은 여유 있게.",
        },
    },
    "ord_return": {
        "name": "ORD 이동 · 렌트 반납",
        "address": "O'Hare Rental Car Return, Chicago, IL 60666",
        "drive_min": "약 45–70분 (교통 따라)",
        "parking": {
            "name": "렌트카 반납 (Rental Car Return)",
            "address": "O'Hare Rental Car Center · Follow ‘Rental Car Return’ 표지",
            "note": "귀국편 ORD 06:00 출발이면 심야·새벽 이동. 반납 후 ATS로 터미널. 공항 장기주차 아님.",
            "maps": _maps("O'Hare Rental Car Return"),
        },
        "uber": {
            "dropoff": "ORD Terminal (렌트 없을 때)",
            "address": "Chicago O'Hare International Airport",
            "fare": "숙소→ORD 약 ₩55,000–85,000 · XL ₩75,000–110,000",
            "note": "새벽 비행이면 전날 밤 공항 호텔도 검토.",
        },
        "transit": {
            "route": "CTA Blue Line → O'Hare (짐·새벽엔 비추천)",
            "steps": [
                "시내까지 이동 후 Blue Line to O'Hare",
                "터미널 연결",
            ],
            "fare": "CTA $5 공항 요금대(정책 확인) · 4명+짐이면 우버/렌트",
            "note": "06:00 출발 → 공항 03:00대 도착 목표.",
        },
    },
    "airport_food": {
        "name": "공항 식사·쇼핑",
        "address": "ORD Terminals, Chicago, IL 60666",
        "drive_min": "터미널 내",
        "parking": {
            "name": "해당 없음 (보안 통과 후)",
            "address": "탑승 터미널",
            "note": "렌트 반납·체크인 후 터미널 식당가.",
            "maps": _maps("O'Hare Airport Terminal food court"),
        },
        "uber": {
            "dropoff": "—",
            "address": "터미널 내부",
            "fare": "—",
            "note": "이미 공항 도착 후.",
        },
        "transit": {
            "route": "터미널 도보",
            "steps": ["보안 검색 후 게이트 근처 식사"],
            "fare": "—",
            "note": "액체·수하물 규정 주의.",
        },
    },
}

# Map itinerary place labels → CHI_PLACES keys
CHI_PLACE_KEYS = {
    "ORD 도착 · 렌트카 픽업(9/27)": "ord_pickup",
    "숙소 체크인": "home_checkin",
    "Millennium Park · Cloud Gate": "millennium",
    "Art Institute of Chicago": "art_institute",
    "Chicago Riverwalk": "riverwalk",
    "Navy Pier (야경)": "navy_pier",
    "Shedd Aquarium": "shedd",
    "Field Museum 또는 Adler Planetarium": "field_adler",
    "Grant Park": "grant_park",
    "Museum of Science and Industry": "msi",
    "University of Chicago 캠퍼스": "uchicago",
    "Promontory Point": "promontory",
    "Lincoln Park Zoo (무료)": "lp_zoo",
    "Lincoln Park Conservatory": "lp_conservatory",
    "North Avenue Beach": "north_ave_beach",
    "Architecture River Cruise": "arch_cruise",
    "The Loop 워킹": "loop",
    "Willis Tower Skydeck (선택)": "willis",
    "360 CHICAGO / John Hancock": "hancock",
    "Water Tower · 쇼핑": "water_tower",
    "American Girl / Lego Store": "mag_mile_shops",
    "Oak Park (Frank Lloyd Wright) 또는": "oak_park",
    "Suburban outlet / 지역 공원": "outlet",
    "저녁은 숙소 근처": "home_evening",
    "좋아하는 장소 재방문": "revisit",
    "호숫가 피크닉": "lakefront_picnic",
    "시카고 딥디시 피자": "deep_dish",
    "숙소 체크아웃": "checkout",
    "ORD 이동": "ord_return",
    "공항 식사·쇼핑": "airport_food",
}


CHICAGO_10 = {
    "title": "시카고 10일 여행계획",
    "subtitle": "가족 4명(성인2·어린이2) · Hyde Park/UChicago 거점 · 대략 지출 포함",
    "days": [
        {
            "day": 1,
            "title": "도착 · 렌트 픽업 · 시내 첫인상",
            "places": ["ORD 도착 · 렌트카 픽업(9/27)", "숙소 체크인", "Millennium Park · Cloud Gate"],
            "tips": "공항에서 렌트 인수 후 숙소 이동 · 시차 적응 위주 · 장소 클릭 시 주차·우버·대중교통",
            "spend": [
                {"item": "시내 교통/주차", "amount": 60000},
                {"item": "식사", "amount": 120000},
                {"item": "간식·기타", "amount": 40000},
            ],
        },
        {
            "day": 2,
            "title": "미술관 · 강변",
            "places": ["Art Institute of Chicago", "Chicago Riverwalk", "Navy Pier (야경)"],
            "tips": "미술관은 어린이 할인/무료 요일 확인 · 각 장소 탭에서 이동수단 비교",
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
            "tips": "CityPASS/박물관 콤보권 비교 추천 · Museum Campus는 자차 하루 주차 효율",
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
            "tips": "무료 코스로 예산 절약 데이 · 거리는 멀어 자차·우버 비교",
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
            "tips": "ORD 렌트카로 근교 이동 · 주차비 확인",
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
            "tips": "공항 3시간 전 도착 권장 · 귀국편 06:00이면 심야 이동",
            "spend": [
                {"item": "공항 이동", "amount": 100000},
                {"item": "공항 식사", "amount": 120000},
                {"item": "잡비", "amount": 50000},
            ],
        },
    ],
    "budget_note": (
        "위 금액은 4명 기준 대략치(KRW)입니다. 일정 장소 이름을 누르면 "
        f"숙소({CHI_HOME['address']}) 기준 자차 주차·우버·대중교통 안내가 열립니다."
    ),
}

EAST_COAST_3 = {
    "title": "동부 3일 여행계획",
    "subtitle": "뉴욕 인 루트/별도 일정용 · 도시별 3일 코스 · 숙박(2박) 포함 대략 지출",
    "cities": [
        {
            "key": "nyc",
            "label": "뉴욕",
            "chip": "NYC 3일",
            "blurb": "맨해튼 핵심 · 교통은 지하철(MetroCard)+우버만 · 렌트카 없음 · 시카고 이동은 국내선",
            "lodging": {
                "nights": 2,
                "per_night": 550_000,
                "amount": 1_100_000,
                "note": "맨해튼/미드타운 가족실·Apt · 세금·수수료 포함 가정",
                "area": "Times Square · Midtown 인근",
                "price_source": "Booking.com",
                "price_source_detail": "Booking.com Midtown 검색 기준 2박 예산대(성인2·아동7·8세)",
                "price_source_url": (
                    "https://www.booking.com/searchresults.html?"
                    "ss=Midtown+Manhattan+Times+Square&checkin=2026-09-23&checkout=2026-09-25"
                    "&group_adults=2&group_children=2&age=7&age=8&no_rooms=1&selected_currency=KRW"
                ),
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
                "note": "National Mall / Downtown 호텔·Apt · 세금 포함 가정",
                "area": "National Mall · Downtown DC",
                "price_source": "Booking.com",
                "price_source_detail": "Booking.com Downtown DC 검색 기준 2박 예산대(성인2·아동7·8세)",
                "price_source_url": (
                    "https://www.booking.com/searchresults.html?"
                    "ss=Washington+DC+Downtown&checkin=2026-09-23&checkout=2026-09-25"
                    "&group_adults=2&group_children=2&age=7&age=8&no_rooms=1&selected_currency=KRW"
                ),
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
                "note": "Downtown / Back Bay 가족실 · 세금 포함 가정",
                "area": "Downtown · Back Bay",
                "price_source": "Booking.com",
                "price_source_detail": "Booking.com Back Bay 검색 기준 2박 예산대(성인2·아동7·8세)",
                "price_source_url": (
                    "https://www.booking.com/searchresults.html?"
                    "ss=Boston+Back+Bay&checkin=2026-09-23&checkout=2026-09-25"
                    "&group_adults=2&group_children=2&age=7&age=8&no_rooms=1&selected_currency=KRW"
                ),
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
    "budget_note": "동부 3일은 숙박 2박 대략치를 Day1·Day2에 포함합니다(가족 4명). 뉴욕 교통은 대중교통·우버만 반영합니다. 뉴욕→시카고 국내선·ORD 렌트카는 항공권·렌트카 탭에서 따로 선택하세요.",
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


def _render_day_places(places: list[str], *, clickable: bool = False) -> str:
    bits = []
    for p in places or []:
        key = CHI_PLACE_KEYS.get(p) if clickable else None
        if key and key in CHI_PLACES:
            bits.append(
                f'<li><button type="button" class="chi-place-btn" data-chi-place="{key}">'
                f"{p}<span class=\"chi-place-go\">이동수단 →</span></button></li>"
            )
        else:
            bits.append(f"<li>{p}</li>")
    return "".join(bits)


def _render_day_card(day: dict, accent: str = "", *, chi_places: bool = False) -> str:
    places = _render_day_places(day.get("places") or [], clickable=chi_places)
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
      <ul class="itin-places{" chi-places-clickable" if chi_places else ""}">{places}</ul>
      {tip_html}
      <table class="itin-spend">
        <thead><tr><th>지출 항목</th><th>대략</th></tr></thead>
        <tbody>{spend_rows}</tbody>
      </table>
    </article>"""


def _chi_mode_panel(mode_key: str, title: str, body: dict, place: dict) -> str:
    if mode_key == "parking":
        maps = body.get("maps") or _maps(body.get("address") or place.get("address") or "")
        return f"""
        <div class="chi-mode-panel" data-chi-mode-panel="parking" hidden>
          <p class="chi-mode-lead"><strong>추천 주차</strong> · 숙소에서 자차 {place.get('drive_min', '')}</p>
          <p><strong>{body.get('name', '')}</strong></p>
          <p class="muted">주소: {body.get('address', '')}</p>
          <p>{body.get('note', '')}</p>
          <p class="muted">목적지: {place.get('address', '')}</p>
          <p><a class="chi-maps-link" href="{maps}" target="_blank" rel="noopener noreferrer">Google 지도에서 주차 찾기</a></p>
        </div>"""
    if mode_key == "uber":
        maps = _maps(body.get("address") or place.get("address") or "")
        return f"""
        <div class="chi-mode-panel" data-chi-mode-panel="uber" hidden>
          <p class="chi-mode-lead"><strong>우버 하차</strong> · {body.get('dropoff', '')}</p>
          <p class="muted">주소: {body.get('address', '')}</p>
          <p><strong>대략 요금</strong> {body.get('fare', '')}</p>
          <p>{body.get('note', '')}</p>
          <p class="muted">출발 기준: {CHI_HOME['address']}</p>
          <p><a class="chi-maps-link" href="{maps}" target="_blank" rel="noopener noreferrer">하차 주소 지도</a></p>
        </div>"""
    # transit
    steps = "".join(f"<li>{s}</li>" for s in (body.get("steps") or []))
    return f"""
    <div class="chi-mode-panel" data-chi-mode-panel="transit" hidden>
      <p class="chi-mode-lead"><strong>대중교통</strong> · {body.get('route', '')}</p>
      <ol class="chi-transit-steps">{steps}</ol>
      <p><strong>대략 요금</strong> {body.get('fare', '')}</p>
      <p>{body.get('note', '')}</p>
      <p class="muted">Ventra 카드/앱 · CTA 기본 $2.50/인 · 만 7세 미만은 보호자 동반 시 CTA 무료인 경우가 많습니다.</p>
    </div>"""


def render_chicago_transport_modal() -> str:
    blocks = []
    for key, place in CHI_PLACES.items():
        parking = place.get("parking") or {}
        uber = place.get("uber") or {}
        transit = place.get("transit") or {}
        dest_maps = _maps(place.get("address") or "")
        blocks.append(f"""
        <article class="chi-place-detail" data-chi-detail="{key}" hidden>
          <h3 id="chi-transport-title-{key}">{place['name']}</h3>
          <p class="muted">목적지 주소: {place.get('address', '')} ·
            <a href="{dest_maps}" target="_blank" rel="noopener noreferrer">지도</a>
          </p>
          <div class="chi-mode-switch" role="tablist" aria-label="이동수단">
            <button type="button" class="chi-mode-tab active" data-chi-mode="parking" aria-selected="true">🚗 자차·주차</button>
            <button type="button" class="chi-mode-tab" data-chi-mode="uber" aria-selected="false">🚕 우버</button>
            <button type="button" class="chi-mode-tab" data-chi-mode="transit" aria-selected="false">🚇 대중교통</button>
          </div>
          {_chi_mode_panel("parking", "자차", parking, place)}
          {_chi_mode_panel("uber", "우버", uber, place)}
          {_chi_mode_panel("transit", "대중교통", transit, place)}
        </article>""")
    return f"""
    <div id="chi-transport-modal" class="nyc-modal chi-transport-modal" hidden role="dialog" aria-modal="true"
      aria-labelledby="chi-transport-modal-title">
      <div class="nyc-modal-backdrop" data-chi-close></div>
      <div class="nyc-modal-panel">
        <header class="nyc-modal-head">
          <div>
            <p class="date-kicker">FROM HYDE PARK</p>
            <h2 id="chi-transport-modal-title">목적지 이동 안내</h2>
            <p class="muted">숙소 {CHI_HOME['address']} 기준 · 요금은 대략치(시즌·혼잡·환율 변동)</p>
          </div>
          <button type="button" class="nyc-modal-close" data-chi-close aria-label="닫기">×</button>
        </header>
        <div id="chi-transport-body">
          {''.join(blocks)}
        </div>
        <footer class="nyc-modal-foot">
          <button type="button" class="nyc-modal-secondary" data-chi-close>닫기</button>
        </footer>
      </div>
    </div>
    """


def render_chicago_plan() -> str:
    plan = CHICAGO_10
    days_html = "".join(_render_day_card(d, chi_places=True) for d in plan["days"])
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
    <p class="flight-hint muted">장소 이름(이동수단 →)을 누르면 <strong>자차 주차 · 우버 · 지하철/버스</strong> 안내가 각각 표시됩니다.</p>
    <div class="itin-stack">{days_html}</div>
    {render_chicago_transport_modal()}
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

def _booking_search_url(hotel_query: str) -> str:
    return (
        "https://www.booking.com/searchresults.html?"
        f"ss={quote_plus(hotel_query)}&checkin={NYC_HOTEL_CHECKIN}&checkout={NYC_HOTEL_CHECKOUT}"
        "&group_adults=2&group_children=2&age=7&age=8&no_rooms=1&selected_currency=KRW"
    )


def _kayak_hotel_url(hotel_query: str) -> str:
    return (
        f"https://www.kayak.co.kr/hotels/{quote_plus(hotel_query)}/"
        f"{NYC_HOTEL_CHECKIN}/{NYC_HOTEL_CHECKOUT}/2adults/children-7-8?sort=price_a"
    )


# Curated family picks for Midtown.
# price = Booking.com search-based 2-night KRW total for 2 adults + children 7–8.
# price_source = site used for the displayed figure (always Booking.com here).
_PRICE_SRC = "Booking.com"
_PRICE_SRC_DETAIL = (
    f"Booking.com 검색 기준 · {NYC_HOTEL_CHECKIN}→{NYC_HOTEL_CHECKOUT} · "
    "성인2·아동7·8세 · 세금·수수료 별도일 수 있음"
)
NYC_HOTEL_RECS = [
    {
        "id": "broadwayts",
        "name": "Broadway at Times Square Hotel",
        "stars": 3,
        "area": "Times Square · 47th St",
        "price": 780_000,
        "price_note": "2박 총액 · 세금·수수료 별도일 수 있음",
        "price_source": _PRICE_SRC,
        "price_source_detail": _PRICE_SRC_DETAIL,
        "badge": "최저가대",
        "conditions": [
            "객실이 작을 수 있음 · 4인은 더블+롤어웨이/패밀리룸 확인",
            "조식 미포함인 경우 많음",
            "리뷰에서 소음·청결 편차 있음 · 최근 후기 확인",
            "무료 취소 요금제 선택 권장",
        ],
        "why": "예산을 최대한 낮출 때. 위치는 좋지만 시설·객실 크기는 타협.",
        "query": "Broadway at Times Square Hotel",
    },
    {
        "id": "rownyc",
        "name": "Row NYC",
        "stars": 4,
        "area": "Times Square · 8th Ave",
        "price": 860_000,
        "price_note": "2박 총액 · 프로모션 잦음",
        "price_source": _PRICE_SRC,
        "price_source_detail": _PRICE_SRC_DETAIL,
        "badge": "특가 후보",
        "conditions": [
            "타임스스퀘어 바로 옆 · 도보 동선 최고",
            "패밀리/퀸+소파 배치 가능한 객실 있는지 확인",
            "리조트피·도시세 포함 여부 총액으로 비교",
            "소음 대비 가급적 높은 층·안쪽 객실",
        ],
        "why": "할인 나올 때 가성비가 좋고 위치가 확실합니다.",
        "query": "Row NYC Times Square",
    },
    {
        "id": "fairfield",
        "name": "Fairfield by Marriott New York Manhattan/Times Square",
        "stars": 3,
        "area": "Midtown West · near Times Square",
        "price": 900_000,
        "price_note": "2박 총액 · 브랜드 저가형",
        "price_source": _PRICE_SRC,
        "price_source_detail": _PRICE_SRC_DETAIL,
        "badge": "실속",
        "conditions": [
            "Marriott 계열이라 기대치가 비교적 안정적",
            "무료 Wi-Fi · 일부 요금 조식 포함",
            "4인실/롤어웨이 가능 여부 예약 시 확인",
            "객실 크기는 미드타운 평균 수준",
        ],
        "why": "너무 저렴한 무명 호텔보다 브랜드 안정성을 원할 때 좋은 중간.",
        "query": "Fairfield Inn Suites New York Manhattan Times Square",
    },
    {
        "id": "edison",
        "name": "Hotel Edison Times Square",
        "stars": 3,
        "area": "Theater District · 47th St",
        "price": 940_000,
        "price_note": "2박 총액 · 클래식 미드타운",
        "price_source": _PRICE_SRC,
        "price_source_detail": _PRICE_SRC_DETAIL,
        "badge": "저렴+위치",
        "conditions": [
            "브로드웨이·타임스스퀘어 도보권",
            "퀸 2베드 등 가족 배치 객실 확인",
            "건물이 오래되어 객실 편차 있음",
            "조식은 보통 별도",
        ],
        "why": "위치 대비 가격이 괜찮은 편. 시설보다 동선·예산을 중시할 때.",
        "query": "Hotel Edison Times Square",
    },
    {
        "id": "hiexpress",
        "name": "Holiday Inn Express New York City Times Square",
        "stars": 3,
        "area": "Times Square South",
        "price": 980_000,
        "price_note": "2박 총액 · 조식 포함 요금 많음",
        "price_source": _PRICE_SRC,
        "price_source_detail": _PRICE_SRC_DETAIL,
        "badge": "조식 실속",
        "conditions": [
            "익스프레스 조식 포함인 경우가 많아 식비 절약",
            "어린이 조식 무료/할인 정책 확인",
            "패밀리룸·연결객실 재고 제한적일 수 있음",
            "무료 취소 마감일 요금제별 상이",
        ],
        "why": "아이 둘과 조식을 호텔에서 해결하고 싶을 때 가성비 좋음.",
        "query": "Holiday Inn Express New York City Times Square",
    },
    {
        "id": "newyorker",
        "name": "The New Yorker, A Wyndham Hotel",
        "stars": 4,
        "area": "Midtown South · Penn Station 인근",
        "price": 1_050_000,
        "price_note": "2박 총액 · 스위트/소파베드 옵션",
        "price_source": _PRICE_SRC,
        "price_source_detail": _PRICE_SRC_DETAIL,
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
        "id": "parkcentral",
        "name": "Park Central Hotel New York",
        "stars": 4,
        "area": "7th Ave · Central Park South 인근",
        "price": 1_180_000,
        "price_note": "2박 총액 · Twin/Queen 가족실 기준",
        "price_source": _PRICE_SRC,
        "price_source_detail": _PRICE_SRC_DETAIL,
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
        "id": "msocial",
        "name": "M Social Hotel New York Times Square",
        "stars": 4,
        "area": "Times Square · Theater District",
        "price": 1_250_000,
        "price_note": "2박 총액 · 시즌·객실타입별 변동",
        "price_source": _PRICE_SRC,
        "price_source_detail": _PRICE_SRC_DETAIL,
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
        "id": "homewood",
        "name": "Homewood Suites Midtown Manhattan / Times Square-South",
        "stars": 3,
        "area": "Midtown · Times Square South",
        "price": 1_420_000,
        "price_note": "2박 총액 · 키친ette 스위트",
        "price_source": _PRICE_SRC,
        "price_source_detail": _PRICE_SRC_DETAIL,
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
        "price_note": "2박 총액 · 연결객실/패밀리 패키지",
        "price_source": _PRICE_SRC,
        "price_source_detail": _PRICE_SRC_DETAIL,
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
for _h in NYC_HOTEL_RECS:
    q = _h.get("query") or _h["name"]
    _h["price_source_url"] = _booking_search_url(q)
    _h["price_check_urls"] = {
        "Booking.com에서 확인": _booking_search_url(q),
        "KAYAK에서 확인": _kayak_hotel_url(q),
    }
NYC_HOTEL_RECS.sort(key=lambda h: h.get("price") or 10**12)


def _render_east_lodging_card(city: dict) -> str:
    lodging = city.get("lodging") or {}
    if not lodging:
        return ""
    nights = lodging.get("nights", 2)
    per_night = lodging.get("per_night")
    amount = lodging.get("amount") or (per_night * nights if per_night else 0)
    area = lodging.get("area") or ""
    note = lodging.get("note") or ""
    src = lodging.get("price_source") or "Booking.com"
    src_detail = lodging.get("price_source_detail") or ""
    src_url = lodging.get("price_source_url") or "#"
    src_html = (
        f'<p class="nyc-price-source">출처: '
        f'<a href="{src_url}" target="_blank" rel="noopener noreferrer"><strong>{src}</strong></a></p>'
        + (f'<p class="muted nyc-price-source-detail">{src_detail}</p>' if src_detail else "")
    )

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
              {src_html}
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
          <h3>{city['label']} 숙박</h3>
          <p class="muted">{area}</p>
        </div>
        <div class="east-lodging-price">
          <strong>{fmt_won(amount)}</strong>
          <span class="muted">{nights}박 · 1박 약 {fmt_won(per_night)}</span>
          {src_html}
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
        src = h.get("price_source") or "가격 출처 미상"
        src_detail = h.get("price_source_detail") or ""
        src_url = h.get("price_source_url") or (h.get("price_check_urls") or {}).get("Booking.com") or "#"
        check_urls = h.get("price_check_urls") or {}
        check_links = "".join(
            f'<a href="{url}" target="_blank" rel="noopener noreferrer">{name}</a>'
            for name, url in check_urls.items()
        )
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
              <p class="nyc-price-source">
                출처: <a href="{src_url}" target="_blank" rel="noopener noreferrer"><strong>{src}</strong></a>
              </p>
              <p class="muted nyc-price-source-detail">{src_detail}</p>
              <p class="nyc-price-check">{check_links}</p>
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
            <p class="muted" style="margin:4px 0 0;">날짜·인원(성인2·아동7·8세)이 들어간 링크로 바로 이동합니다. 표시 금액의 출처는 각 호텔 카드에 적혀 있습니다.</p>
          </div>
          {area_sites}
        </section>
        <p class="muted nyc-modal-note">
          카드 금액의 출처는 각 호텔에 <strong>Booking.com</strong>으로 표시됩니다(검색 링크 포함).
          결제 직전 총액은 Booking.com·KAYAK 등에서 다시 확인해 주세요.
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
          <span class="muted">NYC 교통</span>
          <strong>지하철 + 우버</strong>
          <span class="muted">렌트 없음 · CHI는 국내선</span>
        </div>
      </div>
    </section>
    <p class="flight-hint muted">{plan['budget_note']}</p>
    <div class="route-switch east-switch" role="tablist">{''.join(tabs)}</div>
    {''.join(panels)}
    {render_nyc_hotel_modal()}
    """
