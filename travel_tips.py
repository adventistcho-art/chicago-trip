#!/usr/bin/env python3
"""US trip payment + discount tips tab (NYC + Chicago family itinerary)."""

from __future__ import annotations

import html


def _e(s: str) -> str:
    return html.escape(s, quote=True)


def _link(label: str, url: str, note: str = "") -> str:
    note_html = f' <span class="muted">· {_e(note)}</span>' if note else ""
    return (
        f'<a class="tips-ext" href="{_e(url)}" target="_blank" rel="noopener noreferrer">'
        f"{_e(label)} ↗</a>{note_html}"
    )


def _day_block(city: str, day: int, title: str, blurb: str, links: list[tuple[str, str, str]], prep: str) -> str:
    items = "".join(
        f"<li><strong>{_e(name)}</strong><br>{_link('공식/예약', url, note)}</li>"
        for name, url, note in links
    )
    return f"""
    <article class="tips-day">
      <div class="tips-day-head">
        <span class="tips-day-badge">{_e(city)} Day {day}</span>
        <h4>{_e(title)}</h4>
      </div>
      <p class="muted tips-day-blurb">{_e(blurb)}</p>
      <ul class="tips-day-links">{items}</ul>
      <p class="tips-day-prep"><strong>미리</strong> {_e(prep)}</p>
    </article>
    """


def _modals() -> list[dict]:
    return [
        {
            "id": "tip-wallet",
            "title": "트래블월렛 (트래블페이) 상세",
            "body": f"""
          <p>트래블페이가 운영하는 <strong>VISA 선불카드</strong>입니다. 앱에 원화를 넣고 <strong>USD로 환전·충전</strong>한 뒤, 미국 가맹점에서 현지통화(USD)로 결제합니다.</p>
          <h4>이 일정에서 쓰기 좋은 이유</h4>
          <ul>
            <li>뉴욕·시카고는 카드(특히 VISA) 가맹점이 매우 넓음</li>
            <li>지하철 OMNY·버스·편의점·식당에서 컨택리스(탭) 결제 후기가 많음</li>
            <li>주요 통화(USD 등) 환전 수수료 우대 구간이 있어 일상 결제에 유리한 경우가 많음</li>
          </ul>
          <h4>꼭 알아둘 점</h4>
          <ul>
            <li><strong>잔액 부족 = 결제 거절</strong>. 자동 충전이 없거나 제한적일 수 있으니 출국 전·여행 중 앱에서 여유 있게 충전</li>
            <li>계좌 연동 직후 12~24시간은 오픈뱅킹 제한이 걸릴 수 있음 → <strong>출국 2~3일 전</strong> 연동·충전 테스트</li>
            <li>실물 카드는 배송 또는 편의점 수령 후 앱에서 <strong>등록(활성화) ON</strong>해야 ATM·결제가 됨</li>
            <li>ATM 무료 출금은 <strong>월 한도</strong>가 있는 편(초과 시 수수료). 미국은 현금 비중이 낮아 소액만 인출</li>
            <li>귀국 후 남은 USD는 앱에서 원화로 되돌릴 때 환율 스프레드가 있을 수 있음 → 쓸 만큼만 충전</li>
          </ul>
          <h4>신청·관리</h4>
          <p>앱스토어/플레이스토어에서 “트래블월렛” 검색 → 본인인증 → 카드 신청. 공식 안내·수수료는 앱 공지가 최신입니다.</p>
          <p class="tips-modal-links">{_link("트래블월렛 안내(검색)", "https://www.google.com/search?q=%ED%8A%B8%EB%9E%98%EB%B8%94%EC%9B%94%EB%A0%9B+%EC%B9%B4%EB%93%9C+%EC%8B%A0%EC%B2%AD")}</p>
        """,
        },
        {
            "id": "tip-travelog",
            "title": "트래블로그 (하나카드) 상세",
            "body": f"""
          <p>하나카드의 해외특화 카드로, <strong>Mastercard / UnionPay / VISA</strong> 중 선택 발급하는 경우가 많습니다. 지원 통화가 넓고, 잔액이 부족할 때 <strong>자동 환전 결제</strong>에 유리한 편입니다.</p>
          <h4>이 일정에서의 역할</h4>
          <ul>
            <li>주력(트래블월렛·VISA)이 거절될 때 <strong>다른 브랜드 백업</strong></li>
            <li>현금이 필요할 때 ATM 출금 한도가 상대적으로 넉넉한 편</li>
            <li>미국만 다니면 월렛이 주력이고, 로그는 “안 되는 순간”용으로 충분</li>
          </ul>
          <h4>주의</h4>
          <ul>
            <li>귀국 후 외화→원화 재환전 시 <strong>수수료(예: 1%대)</strong>가 붙는 구조가 흔함 → 과충전 피하기</li>
            <li>제휴 ATM이 아닌 사설 ATM은 기기 수수료가 따로 붙을 수 있음</li>
            <li>발급·우대율·한도는 상품/이벤트에 따라 달라지니 하나카드·트래블로그 앱에서 확인</li>
          </ul>
          <p class="tips-modal-links">{_link("트래블로그 안내(검색)", "https://www.google.com/search?q=%ED%8A%B8%EB%9E%98%EB%B8%94%EB%A1%9C%EA%B7%B8+%ED%95%98%EB%82%98%EC%B9%B4%EB%93%9C")}</p>
        """,
        },
        {
            "id": "tip-credit",
            "title": "신용카드 · 미국 여행에서 꼭 필요한 이유",
            "body": """
          <p>일상 식비·교통은 선불 USD가 유리한 경우가 많지만, <strong>호텔·렌트카는 신용 보증</strong>을 요구하는 업체가 많습니다. 이 일정(에어비앤비 + 편도 렌트 NYC→ORD)에서도 신용카드 1장은 사실상 필수입니다.</p>
          <h4>출국 전 설정</h4>
          <ul>
            <li>카드사 앱에서 <strong>해외사용 허용</strong> · 일한도/1회한도 확인</li>
            <li><strong>해외원화결제(DCC) 차단</strong> — 가져갈 카드마다 각각 신청</li>
            <li>분실 시 앱·고객센터 번호 메모 / 가족 공유</li>
          </ul>
          <h4>현장에서</h4>
          <ul>
            <li>결제 단말에서 <strong>USD / Local currency</strong> 선택 (원화·KRW 거절)</li>
            <li>식당은 영수증에 tip 칸 → 보통 15~20%를 카드에 합산</li>
            <li>렌트카 카운터는 보증 한도가 잡혀 있을 수 있음 → 한도 여유 확보</li>
            <li>해외이용수수료(카드사+브랜드)가 붙는 상품이 많음 → 고액·일상은 월렛 우선 검토</li>
          </ul>
        """,
        },
        {
            "id": "tip-dcc",
            "title": "DCC(해외 원화결제) 피하기",
            "body": """
          <p>해외 가게·ATM이 “한국 원화로 결제할까요?”라고 물을 때 <strong>Yes/KRW</strong>를 고르면, 불리한 환율+수수료(대략 3~5%대)가 붙는 <strong>DCC</strong>가 적용되는 경우가 많습니다.</p>
          <h4>올바른 선택</h4>
          <ul>
            <li>화면/영수증: <strong>USD</strong>, <strong>Local currency</strong>, <strong>without conversion</strong></li>
            <li>거절할 말: Korean Won, KRW, Convert to KRW</li>
          </ul>
          <h4>예방</h4>
          <ul>
            <li>국내 카드사 앱 → “해외원화결제 차단 / DCC 차단” 등록 (카드 <em>한 장마다</em>)</li>
            <li>차단해 두면 원화 청구 시도 자체가 거절되어 실수를 막음</li>
            <li>선불(월렛/로그)도 잔액 부족으로 원화 계좌를 끌어쓰는 순간엔 주의</li>
          </ul>
        """,
        },
        {
            "id": "tip-pass",
            "title": "시카고 CityPASS vs Go City",
            "body": f"""
          <p>가족 4명(성인2·아동7·8세)이 Shedd·Skydeck·크루즈·MSI·Art Institute를 여러 곳 보면 <strong>패스가 개별 합보다 저렴</strong>한 경우가 많습니다. 반대로 2~3곳만 보면 개별 티켓이 나을 수 있습니다.</p>
          <h4>CityPASS (시카고)</h4>
          <ul>
            <li>핵심 명소 묶음(예: Shedd·Skydeck 포함 + 선택 명소) · 유효기간 수일</li>
            <li>구매 후 <strong>My CityPASS 앱</strong>에서 타임슬롯 예약 — Shedd·Skydeck는 사실상 필수</li>
          </ul>
          <h4>Go City</h4>
          <ul>
            <li>Explorer(몇 곳 선택) / All-Inclusive(일수제) 등 형태가 다름</li>
            <li>크루즈·전망대 등 폭넓은 목록 · 앱에서 사전 예약 필요한 곳 많음</li>
          </ul>
          <h4>이 일정 팁</h4>
          <ul>
            <li>10일 중 박물관·전망대를 몰아서 볼 날(2·3·4·6·7일)을 먼저 정한 뒤 패스 손익 계산</li>
            <li>패스 사자마자 Skydeck·Shedd·크루즈 슬롯부터 잡기</li>
            <li>Lincoln Park Zoo는 무료라 패스와 무관 — 예산 절약 데이로 활용</li>
          </ul>
          <p class="tips-modal-links">
            {_link("Chicago CityPASS", "https://www.citypass.com/chicago")}
            {_link("Go City Chicago", "https://gocity.com/en/chicago")}
          </p>
        """,
        },
        {
            "id": "tip-omny",
            "title": "뉴욕 교통 OMNY · 시카고 CTA",
            "body": f"""
          <h4>뉴욕 — OMNY</h4>
          <ul>
            <li>지하철·버스 개찰구에 <strong>카드/스마트폰 탭</strong> (별도 MetroCard가 필수는 아닌 경우가 많음)</li>
            <li>같은 결제수단으로 탭하면 주간 요금 상한(fare capping) 혜택이 적용될 수 있음 — 공식 OMNY 안내 확인</li>
            <li>트래블월렛·모바일 월렛 탭 가능 여부를 출국 전 후기로 한 번 더 확인</li>
          </ul>
          <h4>시카고 — CTA / Ventra</h4>
          <ul>
            <li>렌트카 위주면 시내 구간만 CTA·우버 병행</li>
            <li>Ventra 앱 또는 컨택리스 탭 · 공항↔시내는 상황에 따라 우버/렌트가 편할 수 있음</li>
          </ul>
          <p class="tips-modal-links">
            {_link("OMNY 공식", "https://omny.info/")}
            {_link("CTA / Ventra", "https://www.transitchicago.com/")}
          </p>
        """,
        },
    ]


def _modal_html(m: dict) -> str:
    return f"""
    <div class="tips-modal" id="{_e(m['id'])}" hidden>
      <div class="tips-modal-backdrop" data-tips-close></div>
      <div class="tips-modal-panel" role="dialog" aria-modal="true" aria-labelledby="{_e(m['id'])}-title">
        <div class="tips-modal-head">
          <h2 id="{_e(m['id'])}-title">{_e(m['title'])}</h2>
          <button type="button" class="tips-modal-close" data-tips-close aria-label="닫기">×</button>
        </div>
        <div class="tips-modal-body">{m['body']}</div>
        <div class="tips-modal-foot">
          <button type="button" class="tips-modal-secondary" data-tips-close>닫기</button>
        </div>
      </div>
    </div>
    """


def render_tips_tab() -> str:
    nyc_days = [
        _day_block(
            "NYC",
            1,
            "미드타운 · 센트럴파크",
            "타임스퀘어 → 록펠러 → 센트럴파크·동물원. 걷거나 지하철 1~2정거장.",
            [
                ("Times Square", "https://www.timessquarenyc.org/", "안내·이벤트"),
                ("Rockefeller Center / Top of the Rock", "https://www.rockefellercenter.com/", "전망대 예약"),
                ("Central Park", "https://www.centralparknyc.org/", "지도·동선"),
                ("Central Park Zoo", "https://centralparkzoo.com/", "온라인 티켓"),
            ],
            "동물원·록펠러 전망대는 날짜·시간 예약. OMNY용 카드/폰 탭 준비.",
        ),
        _day_block(
            "NYC",
            2,
            "박물관 · 5번가",
            "자연사박물관 또는 MoMA + 5번가 산책 · Empire State는 선택.",
            [
                ("AMNH (자연사박물관)", "https://www.amnh.org/", "타임드 엔트리"),
                ("MoMA", "https://www.moma.org/", "티켓·시간"),
                ("Empire State Building", "https://www.esbnyc.com/", "전망대 예약"),
                ("NYC CityPASS (손익 비교용)", "https://www.citypass.com/new-york", "3일이면 개별이 쌀 수도"),
            ],
            "박물관·전망대는 공식 사이트에서 슬롯 구매. 당일 현장은 대기·매진 리스크.",
        ),
        _day_block(
            "NYC",
            3,
            "다운타운 · 자유의 여신",
            "페리·월스트리트·9/11 · 브루클린 브릿지 산책.",
            [
                ("Statue of Liberty (NPS)", "https://www.nps.gov/stli/", "입장 정보"),
                ("Statue City Cruises (공식 페리)", "https://www.statuecitycruises.com/", "선예약 필수에 가까움"),
                ("9/11 Memorial & Museum", "https://www.911memorial.org/", "야외 메모리얼 무료·뮤지엄 예약"),
                ("Brooklyn Bridge", "https://www.nyc.gov/html/dot/html/infrastructure/brooklyn-bridge.shtml", "도보 동선"),
            ],
            "페리·크라운 예약은 주말·오후가 빨리 참. 출국 전 날짜 확정.",
        ),
    ]

    chi_days = [
        _day_block(
            "CHI",
            1,
            "도착 · 렌트 · 밀레니엄파크",
            "ORD 렌트 픽업 → 숙소 체크인 → Cloud Gate.",
            [
                ("O'Hare (ORD)", "https://www.flychicago.com/ohare/home/pages/default.aspx", "터미널·교통"),
                ("Millennium Park / Cloud Gate", "https://www.chicago.gov/city/en/depts/dca/supp_info/millennium_park.html", "무료 공원"),
                ("Chicago CityPASS", "https://www.citypass.com/chicago", "패스 구매·비교"),
            ],
            "렌트 보증용 신용카드·보험 확인. 시차 적응 위주.",
        ),
        _day_block(
            "CHI",
            2,
            "미술관 · 강변",
            "Art Institute + Riverwalk + Navy Pier 야경.",
            [
                ("Art Institute of Chicago", "https://www.artic.edu/", "티켓·아동요금"),
                ("Chicago Riverwalk", "https://www.chicago.gov/city/en/depts/dcd/supp_info/chicago_riverwalk.html", "산책"),
                ("Navy Pier", "https://navypier.org/", "야경·패밀리"),
            ],
            "미술관 온라인 티켓. CityPASS 사용 시 패스 입장 절차 확인.",
        ),
        _day_block(
            "CHI",
            3,
            "박물관 캠퍼스",
            "Shedd · Field 또는 Adler · Grant Park.",
            [
                ("Shedd Aquarium", "https://www.sheddaquarium.org/", "타임슬롯 필수에 가까움"),
                ("Field Museum", "https://www.fieldmuseum.org/", "티켓"),
                ("Adler Planetarium", "https://www.adlerplanetarium.org/", "선택"),
                ("Go City Chicago", "https://gocity.com/en/chicago", "패스 대안"),
            ],
            "Shedd는 패스 구매 직후 예약. 주차비 높음 → CTA/우버 검토.",
        ),
        _day_block(
            "CHI",
            4,
            "하이드파크 · MSI",
            "숙소 근처 MSI · UChicago 캠퍼스 · Promontory Point.",
            [
                ("Museum of Science and Industry", "https://www.msichicago.org/", "가족·체험"),
                ("University of Chicago", "https://www.uchicago.edu/", "캠퍼스 산책"),
            ],
            "MSI 온라인 티켓/패스. 아이들 체력 고려해 여유 일정.",
        ),
        _day_block(
            "CHI",
            5,
            "링컨파크 · 동물원",
            "입장 무료 동물원으로 예산 절약 데이.",
            [
                ("Lincoln Park Zoo", "https://www.lpzoo.org/", "무료 입장(기부 선택)"),
                ("Lincoln Park Conservatory", "https://www.chicago.gov/city/en/depts/dca/supp_info/lincoln_park_conservatory.html", "온실"),
            ],
            "예약 부담 적음. 피크닉·아이스크림 예산만.",
        ),
        _day_block(
            "CHI",
            6,
            "건축 크루즈 · 루프",
            "강 크루즈 + 워킹 · Skydeck는 선택.",
            [
                ("Shoreline Sightseeing (Architecture Cruise)", "https://www.shorelinesightseeing.com/", "시간 선점"),
                ("Chicago Architecture Center", "https://www.architecture.org/", "투어·크루즈 정보"),
                ("Skydeck Chicago (Willis Tower)", "https://theskydeck.com/", "타임슬롯"),
            ],
            "주말·오전 크루즈·스카이덱 먼저 예약. 전망대는 Skydeck vs 360 중 하나만.",
        ),
        _day_block(
            "CHI",
            7,
            "매그니피션트 마일",
            "360 CHICAGO · 쇼핑 · 키즈 스토어.",
            [
                ("360 CHICAGO", "https://www.360chicago.com/", "전망대 예약"),
                ("Magnificent Mile", "https://www.themagnificentmile.com/", "쇼핑 안내"),
                ("American Girl Chicago", "https://www.americangirl.com/stores/chicago", "예약·웨이팅"),
            ],
            "전망대 중복 피하기. 쇼핑 예산 상한 정하기.",
        ),
        _day_block(
            "CHI",
            8,
            "근교 데이트립",
            "Oak Park(라이트) 또는 아울렛·공원.",
            [
                ("Frank Lloyd Wright Trust (Oak Park)", "https://flwright.org/", "투어 예약"),
                ("Chicago Premium Outlets", "https://www.premiumoutlets.com/outlet/chicago", "선택"),
            ],
            "렌트카 유류·톨·주차 확인. 투어는 온라인 예약.",
        ),
        _day_block(
            "CHI",
            9,
            "여유 · 재방문",
            "좋아하는 곳 재방문 · 딥디시 · 짐 정리.",
            [
                ("Choose Chicago (공식 관광)", "https://www.choosechicago.com/", "이벤트·팁"),
                ("Giordano's / 딥디시 참고", "https://giordanos.com/", "웨이팅·테이크아웃"),
            ],
            "귀국 전날 여유. 세탁·짐·렌트 반납 시각 점검.",
        ),
        _day_block(
            "CHI",
            10,
            "출국 · ORD",
            "체크아웃 → 렌트 반납 → 출국.",
            [
                ("O'Hare Airport", "https://www.flychicago.com/ohare/home/pages/default.aspx", "보안·터미널"),
                ("TSA 대기시간", "https://www.tsa.gov/", "여유 있게"),
            ],
            "귀국편이 이르면 전날 밤 정리. 공항 3시간 전 목표.",
        ),
    ]

    modals = "".join(_modal_html(m) for m in _modals())

    return f"""
    <section class="route-hero card tips-hero">
      <div class="route-hero-copy">
        <p class="route-kicker">PAY · SAVE · PREP</p>
        <h2>결제·할인 팁</h2>
        <p class="muted">요약은 카드로, 자세한 설명은 ‘자세히’ 모달 · 일정별 공식 사이트 바로가기</p>
      </div>
      <div class="route-stats">
        <div class="route-stat">
          <span class="muted">이 일정</span>
          <strong>NYC → CHI</strong>
          <span class="muted">9/24~10/10 · 가족 4명</span>
        </div>
      </div>
    </section>

    <section class="card tips-section">
      <h3>출국 전 체크리스트</h3>
      <ol class="tips-checklist">
        <li><strong>실물 카드 발급·활성화</strong> — 월렛/로그 앱 → 수령 → 앱에서 등록 ON
          <button type="button" class="tips-more" data-tips-open="tip-wallet">월렛 자세히</button>
          <button type="button" class="tips-more" data-tips-open="tip-travelog">로그 자세히</button>
        </li>
        <li><strong>USD 미리 충전</strong> — 출국 2~3일 전 계좌 연동·충전 테스트(연동 직후 제한 가능)</li>
        <li><strong>해외원화결제(DCC) 차단</strong> — 가져갈 카드마다 각각 신청
          <button type="button" class="tips-more" data-tips-open="tip-dcc">DCC 자세히</button>
        </li>
        <li><strong>해외결제·ATM 한도</strong> — 카드사 앱에서 해외사용 허용·한도 상향
          <button type="button" class="tips-more" data-tips-open="tip-credit">신용 자세히</button>
        </li>
        <li><strong>패스·입장권</strong> — CityPASS/Go City, Shedd·Skydeck·크루즈, NYC 페리
          <button type="button" class="tips-more" data-tips-open="tip-pass">패스 비교</button>
        </li>
      </ol>
      <p class="muted tips-footnote">※ 수수료·한도·우대율은 수시로 바뀝니다. 출국 전 각 앱·카드사 공지로 최종 확인하세요.</p>
    </section>

    <section class="card tips-section">
      <h3>결제수단 요약</h3>
      <p class="muted" style="margin-top:0;">미국은 카드 비중이 높습니다. <strong>USD 선불 주력 + 신용 보증</strong> 조합을 권합니다. 칸이 좁아 요약만 두고, 상세는 모달로 엽니다.</p>
      <div class="tips-compare">
        <article class="tips-compare-item">
          <h4>트래블월렛 <span class="tips-tag">트래블페이</span></h4>
          <p class="muted">VISA 선불 · USD 충전 · 미국 일상결제 주력.</p>
          <ul>
            <li>탭 결제·가맹점 커버리지 강점</li>
            <li>잔액 부족 시 거절 → 미리 충전</li>
            <li>ATM 무료는 월 한도 있음</li>
          </ul>
          <p class="tips-reco">추천: <strong>주력</strong>
            <button type="button" class="tips-more" data-tips-open="tip-wallet">자세히</button>
          </p>
        </article>
        <article class="tips-compare-item">
          <h4>트래블로그 <span class="tips-tag">하나카드</span></h4>
          <p class="muted">브랜드 선택형 · 자동환전·ATM 백업.</p>
          <ul>
            <li>월렛과 브랜드를 다르게</li>
            <li>현금 인출·거절 대비</li>
            <li>재환전 수수료 확인</li>
          </ul>
          <p class="tips-reco">추천: <strong>보조</strong>
            <button type="button" class="tips-more" data-tips-open="tip-travelog">자세히</button>
          </p>
        </article>
        <article class="tips-compare-item">
          <h4>신용카드</h4>
          <p class="muted">호텔·렌트 보증 · 비상·온라인.</p>
          <ul>
            <li>편도 렌트·숙소 보증에 필요</li>
            <li>DCC 차단·해외사용 ON</li>
            <li>팁 15~20% 카드 합산 흔함</li>
          </ul>
          <p class="tips-reco">추천: <strong>보증 1장</strong>
            <button type="button" class="tips-more" data-tips-open="tip-credit">자세히</button>
          </p>
        </article>
      </div>
      <div class="tips-quick-actions">
        <button type="button" class="tips-more solid" data-tips-open="tip-dcc">DCC(원화결제) 피하기</button>
        <button type="button" class="tips-more solid" data-tips-open="tip-omny">NYC OMNY · CHI CTA</button>
        <button type="button" class="tips-more solid" data-tips-open="tip-pass">시카고 패스 비교</button>
      </div>
    </section>

    <section class="card tips-section">
      <h3>미국 결제 실전 (짧게)</h3>
      <div class="tips-grid">
        <div>
          <h4>통화 선택</h4>
          <p>POS·ATM에서 <strong>USD</strong>만. KRW 제안은 거절.
            <button type="button" class="tips-more" data-tips-open="tip-dcc">왜?</button>
          </p>
        </div>
        <div>
          <h4>칩·탭</h4>
          <p>대부분 칩/탭. ZIP 요청 시 숙소 우편번호 또는 카드사 안내.</p>
        </div>
        <div>
          <h4>ATM</h4>
          <p>은행 ATM 우선. 공항·관광지 사설기 수수료 주의. 현금은 소액.</p>
        </div>
        <div>
          <h4>세금·팁</h4>
          <p>표시가+세일즈택스. 식당·우버는 팁 별도(대략 15~20%).</p>
        </div>
        <div>
          <h4>아동 요금</h4>
          <p>7·8세는 패스/티켓 아동 구간 확인. 주민 무료일은 여행객 제외인 경우 많음.</p>
        </div>
        <div>
          <h4>분실</h4>
          <p>앱에서 카드 OFF. 여권·숙소·렌트 서류 사진 백업.</p>
        </div>
      </div>
    </section>

    <section class="card tips-section">
      <div class="tips-section-head">
        <h3>뉴욕 3일 — 일정별 사이트</h3>
        <a href="#" data-goto="east-plan" class="tips-goto">동부 일정 탭 →</a>
      </div>
      <p class="muted" style="margin-top:0;">각 Day에서 예약·안내로 바로 갈 수 있는 공식 링크입니다. (새 탭)</p>
      <div class="tips-day-grid">
        {''.join(nyc_days)}
      </div>
    </section>

    <section class="card tips-section">
      <div class="tips-section-head">
        <h3>시카고 10일 — 일정별 사이트</h3>
        <a href="#" data-goto="chi-plan" class="tips-goto">시카고 일정 탭 →</a>
      </div>
      <p class="muted" style="margin-top:0;">패스가 필요한 날(2·3·4·6·7)은 링크에서 티켓·타임슬롯을 먼저 잡으세요.</p>
      <p class="tips-inline-links">
        {_link("CityPASS Chicago", "https://www.citypass.com/chicago")}
        {_link("Go City Chicago", "https://gocity.com/en/chicago")}
        {_link("Choose Chicago", "https://www.choosechicago.com/")}
        <button type="button" class="tips-more" data-tips-open="tip-pass">패스 비교 모달</button>
      </p>
      <div class="tips-day-grid chi">
        {''.join(chi_days)}
      </div>
    </section>

    <section class="card tips-section">
      <h3>이 여행 추천 조합</h3>
      <ol class="tips-checklist">
        <li><strong>주력:</strong> 트래블월렛(USD) — 식당·교통 탭·티켓·쇼핑</li>
        <li><strong>보조:</strong> 트래블로그(다른 브랜드) — ATM·결제 거절 시</li>
        <li><strong>신용 1장:</strong> 호텔·렌트 보증, 항공 부가, 비상</li>
        <li><strong>현금:</strong> 소액만. 대도시는 카드로 대부분 해결</li>
        <li><strong>패스:</strong> 시카고 명소 5곳+면 CityPASS/Go City 손익 비교 → 구매 즉시 슬롯 예약</li>
      </ol>
      <p class="muted tips-footnote">
        <a href="#" data-goto="east-plan">동부 3일</a> ·
        <a href="#" data-goto="chi-plan">시카고 10일</a> ·
        <a href="#" data-goto="cars">렌트카</a> ·
        <a href="#" data-goto="misc-plan">여행비</a>
      </p>
    </section>

    {modals}
    """


def tips_styles() -> str:
    return """
    .tips-hero .route-stat strong { font-size: 1.25rem; }
    .tips-section h3 { margin: 0 0 10px; }
    .tips-section h4 { margin: 0 0 6px; font-size: 1.02rem; }
    .tips-section-head {
      display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between;
      gap: 8px; margin-bottom: 4px;
    }
    .tips-section-head h3 { margin: 0; }
    .tips-goto { font-size: 0.88rem; font-weight: 700; color: var(--budget, #0d7a5f); text-decoration: none; }
    .tips-checklist { margin: 0; padding-left: 1.2rem; line-height: 1.55; }
    .tips-checklist li { margin: 0 0 10px; }
    .tips-footnote { margin: 14px 0 0; }
    .tips-compare {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
      margin-top: 14px;
    }
    .tips-compare-item {
      padding: 14px 14px 12px;
      border: 1px solid rgba(0,0,0,.08);
      border-radius: 12px;
      background: rgba(255,255,255,.55);
    }
    .tips-compare-item ul { margin: 8px 0 10px; padding-left: 1.1rem; line-height: 1.45; font-size: 0.92rem; }
    .tips-compare-item li { margin-bottom: 6px; }
    .tips-tag {
      display: inline-block;
      margin-left: 6px;
      padding: 2px 8px;
      font-size: 0.72rem;
      font-weight: 700;
      border-radius: 999px;
      background: rgba(13,122,95,.12);
      color: var(--budget, #0d7a5f);
      vertical-align: middle;
    }
    .tips-reco {
      margin: 0;
      font-size: 0.9rem;
      padding-top: 8px;
      border-top: 1px dashed rgba(0,0,0,.1);
      display: flex; flex-wrap: wrap; gap: 8px; align-items: center;
    }
    .tips-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px 18px;
      margin-top: 8px;
    }
    .tips-grid p { margin: 0; font-size: 0.92rem; line-height: 1.45; color: var(--muted, #5f6773); }
    .tips-grid h4 { color: var(--text, #14171c); }
    .tips-more {
      border: 1px solid #bfdbfe;
      background: #eff6ff;
      color: #1d4ed8;
      border-radius: 999px;
      padding: 3px 10px;
      font-size: 0.78rem;
      font-weight: 700;
      cursor: pointer;
      margin-left: 6px;
      vertical-align: middle;
    }
    .tips-more.solid {
      margin: 0;
      padding: 8px 14px;
      font-size: 0.84rem;
      background: #0d7a5f;
      border-color: #0d7a5f;
      color: #fff;
    }
    .tips-quick-actions {
      display: flex; flex-wrap: wrap; gap: 8px;
      margin-top: 16px;
    }
    .tips-day-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 12px;
    }
    .tips-day-grid.chi {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .tips-day {
      border: 1px solid var(--line, #e2e7ef);
      border-radius: 14px;
      padding: 12px 14px;
      background: #fafbfc;
    }
    .tips-day-badge {
      display: inline-block;
      font-size: 0.72rem;
      font-weight: 800;
      letter-spacing: .02em;
      padding: 2px 8px;
      border-radius: 999px;
      background: #e0f2fe;
      color: #075985;
    }
    .tips-day-head h4 { margin: 6px 0 4px; font-size: 1rem; }
    .tips-day-blurb { margin: 0 0 8px; font-size: 0.86rem; }
    .tips-day-links {
      margin: 0;
      padding-left: 1.1rem;
      font-size: 0.88rem;
      line-height: 1.45;
    }
    .tips-day-links li { margin-bottom: 8px; }
    .tips-day-prep {
      margin: 10px 0 0;
      font-size: 0.84rem;
      padding-top: 8px;
      border-top: 1px dashed rgba(0,0,0,.1);
      color: #334155;
    }
    .tips-ext {
      color: #1d4ed8;
      font-weight: 700;
      text-decoration: none;
      border-bottom: 1px solid rgba(29,78,216,.25);
    }
    .tips-ext:hover { border-bottom-color: #1d4ed8; }
    .tips-inline-links {
      display: flex; flex-wrap: wrap; gap: 10px 14px;
      align-items: center;
      margin: 8px 0 0;
    }
    .tips-modal {
      position: fixed; inset: 0; z-index: 90;
      display: flex; align-items: flex-start; justify-content: center;
      padding: 4vh 16px 24px; overflow-y: auto;
    }
    .tips-modal[hidden] { display: none !important; }
    .tips-modal-backdrop {
      position: fixed; inset: 0;
      background: rgba(15, 23, 42, .55);
      backdrop-filter: blur(2px);
    }
    .tips-modal-panel {
      position: relative; z-index: 1;
      width: min(720px, 100%);
      background: #fff;
      border-radius: 20px;
      padding: 22px 22px 16px;
      box-shadow: 0 24px 60px rgba(15, 23, 42, .28);
      margin-bottom: 24px;
    }
    .tips-modal-head {
      display: flex; justify-content: space-between; gap: 12px;
      align-items: flex-start; margin-bottom: 10px;
    }
    .tips-modal-head h2 { margin: 0; font-size: 1.3rem; }
    .tips-modal-close {
      border: none; background: #f1f5f9; width: 40px; height: 40px;
      border-radius: 999px; font-size: 1.4rem; line-height: 1;
      cursor: pointer; color: #334155; flex-shrink: 0;
    }
    .tips-modal-body { font-size: 0.95rem; line-height: 1.55; color: #1e293b; }
    .tips-modal-body h4 { margin: 16px 0 6px; font-size: 1.02rem; }
    .tips-modal-body ul { margin: 0 0 8px; padding-left: 1.2rem; }
    .tips-modal-body li { margin-bottom: 6px; }
    .tips-modal-body p { margin: 0 0 10px; }
    .tips-modal-links {
      display: flex; flex-wrap: wrap; gap: 12px;
      margin-top: 14px !important;
    }
    .tips-modal-foot {
      display: flex; justify-content: flex-end;
      margin-top: 16px; padding-top: 12px;
      border-top: 1px solid var(--line, #e2e7ef);
    }
    .tips-modal-secondary {
      border: 1px solid var(--line, #e2e7ef);
      background: #fff; border-radius: 999px;
      padding: 8px 16px; font-weight: 600; cursor: pointer;
    }
    body.tips-modal-open { overflow: hidden; }
    @media (max-width: 900px) {
      .tips-compare, .tips-grid, .tips-day-grid, .tips-day-grid.chi {
        grid-template-columns: 1fr;
      }
    }
    """


def tips_scripts() -> str:
    return """
    (function() {
      function openTipsModal(id) {
        const modal = document.getElementById(id);
        if (!modal) return;
        document.querySelectorAll('.tips-modal').forEach(m => { m.hidden = true; });
        modal.hidden = false;
        document.body.classList.add('tips-modal-open');
        const closeBtn = modal.querySelector('.tips-modal-close');
        if (closeBtn) closeBtn.focus();
      }
      function closeTipsModal() {
        document.querySelectorAll('.tips-modal').forEach(m => { m.hidden = true; });
        document.body.classList.remove('tips-modal-open');
      }
      document.querySelectorAll('[data-tips-open]').forEach(btn => {
        btn.addEventListener('click', () => openTipsModal(btn.getAttribute('data-tips-open')));
      });
      document.querySelectorAll('[data-tips-close]').forEach(el => {
        el.addEventListener('click', closeTipsModal);
      });
      document.addEventListener('keydown', e => {
        if (e.key === 'Escape') closeTipsModal();
      });
    })();
    """
