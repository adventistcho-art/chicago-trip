#!/usr/bin/env python3
"""US trip payment + discount tips tab (NYC + Chicago family itinerary)."""

from __future__ import annotations


def render_tips_tab() -> str:
    """HTML for the 결제·할인 팁 tab (next to 여행비)."""
    return f"""
    <section class="route-hero card tips-hero">
      <div class="route-hero-copy">
        <p class="route-kicker">PAY · SAVE · PREP</p>
        <h2>결제·할인 팁</h2>
        <p class="muted">트래블로그 · 트래블월렛(트래블페이) · 신용카드 · 뉴욕·시카고 사전예약·할인</p>
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
        <li><strong>실물 카드 발급·활성화</strong> — 트래블월렛/트래블로그 앱 설치 → 카드 수령(배송 또는 GS25 등) → 앱에서 등록·ON</li>
        <li><strong>USD 미리 충전</strong> — 출국 2~3일 전 계좌 연동·충전 테스트(오픈뱅킹 연동 직후 12~24시간 제한 가능)</li>
        <li><strong>해외원화결제(DCC) 차단</strong> — 가져갈 <em>모든</em> 신용카드·체크카드에 각각 신청(카드 1장당 1회)</li>
        <li><strong>해외결제·ATM 한도</strong> — 카드사 앱에서 해외사용 허용·일일한도 상향</li>
        <li><strong>비상 카드 1장</strong> — 주력(트래블월렛/로그) + 신용카드 백업, 가능하면 VISA·Mastercard 브랜드를 나눠 둠</li>
        <li><strong>패스·입장권 선예약</strong> — CityPASS/Go City, Shedd·Skydeck·건축 크루즈, NYC 페리·박물관 타임슬롯</li>
      </ol>
      <p class="muted tips-footnote">※ 수수료·한도·우대율은 수시로 바뀝니다. 출국 전 각 앱·카드사 공지로 최종 확인하세요.</p>
    </section>

    <section class="card tips-section">
      <h3>결제수단 한눈에</h3>
      <p class="muted" style="margin-top:0;">미국은 카드 결제 비중이 매우 높습니다. <strong>USD 충전형 선불</strong>을 주력으로, 신용카드는 호텔 보증·비상용으로 쓰는 조합이 안전합니다.</p>
      <div class="tips-compare">
        <article class="tips-compare-item">
          <h4>트래블월렛 <span class="tips-tag">트래블페이</span></h4>
          <p class="muted">트래블페이가 운영하는 VISA 선불카드. 앱에 원화를 넣고 USD로 환전·충전.</p>
          <ul>
            <li>USD·JPY·EUR 등 주요 통화 환전 수수료 우대(상시 0% 구간)</li>
            <li>미국 가맹점·컨택리스(탭) 결제에 강함 · NYC 지하철 OMNY 탭 가능 후기 다수</li>
            <li>잔액 부족 시 <strong>결제 거절</strong> → 앱에서 미리 넉넉히 충전</li>
            <li>ATM 무료 출금은 월 한도 있음(초과 시 수수료) · 현금은 소액만</li>
            <li>편의점 즉시발급 또는 배송 · 반드시 앱에서 실물카드 활성화</li>
          </ul>
          <p class="tips-reco">이 일정 추천: <strong>주력 결제 카드</strong> (식당·교통·입장권·쇼핑)</p>
        </article>
        <article class="tips-compare-item">
          <h4>트래블로그 <span class="tips-tag">하나카드</span></h4>
          <p class="muted">하나카드 해외특화 체크/선불형. Mastercard·UnionPay·VISA 선택 발급.</p>
          <ul>
            <li>지원 통화 폭이 넓고(다수 통화 우대), 잔액 부족 시 <strong>자동 환전 결제</strong>에 유리</li>
            <li>제휴 ATM 출금 한도가 상대적으로 넉넉한 편 → 현금이 필요할 때 백업</li>
            <li>귀국 후 외화→원화 재환전 시 수수료(예: 1%대) 확인 · 쓸 만큼만 충전</li>
            <li>브랜드를 트래블월렛(VISA)과 다르게 가져가면 가맹점 거절 리스크↓</li>
          </ul>
          <p class="tips-reco">이 일정 추천: <strong>보조·ATM·비상</strong> (주력과 브랜드 분리)</p>
        </article>
        <article class="tips-compare-item">
          <h4>신용카드</h4>
          <p class="muted">호텔·렌트카 보증, 항공·온라인 예약, 고액 결제 백업.</p>
          <ul>
            <li>해외이용수수료(보통 1~1.5%+브랜드 수수료) 있는 카드가 많음 → 일상결제는 선불 USD가 유리한 경우 많음</li>
            <li>렌트카·호텔은 <strong>신용 보증</strong>을 요구하는 경우가 많아 신용카드 1장은 필수에 가깝음</li>
            <li>출국 전: 해외사용 ON · DCC 차단 · 한도 확인 · 분실신고 방법 메모</li>
            <li>결제 화면에서 반드시 <strong>USD(현지통화)</strong> 선택 · KRW/원화결제 거절</li>
            <li>팁(팁 문화): 식당은 보통 영수증에 팁 칸 · 15~20% 수준을 카드에 합산하는 경우 많음</li>
          </ul>
          <p class="tips-reco">이 일정 추천: <strong>보증·비상·온라인</strong> (평소 결제는 트래블월렛)</p>
        </article>
      </div>
    </section>

    <section class="card tips-section">
      <h3>미국 결제 실전 팁</h3>
      <div class="tips-grid">
        <div>
          <h4>DCC 피하기</h4>
          <p>POS·ATM에서 “원화로 결제할까요?” → <strong>No / USD / Local currency</strong>. 원화 선택 시 3~5%대 불리한 환율이 붙는 경우가 많습니다.</p>
        </div>
        <div>
          <h4>칩·탭·사인</h4>
          <p>대부분 칩 삽입 또는 컨택리스 탭. 사인/ZIP 요청 시 ZIP은 숙소 우편번호 또는 카드사 안내 따름. 현금만 받는 곳은 드묾.</p>
        </div>
        <div>
          <h4>ATM</h4>
          <p>공항·관광지 사설 ATM은 수수료가 큰 편. 시중은행(Chase, Bank of America, Citi 등) ATM 우선. 출금은 소액·필요할 때만.</p>
        </div>
        <div>
          <h4>세금·팁</h4>
          <p>표시가에 세일즈택스 미포함인 경우가 많음. 식당·우버 앱·배달은 팁 별도. 박물관·패스트푸드는 팁 부담이 적습니다.</p>
        </div>
        <div>
          <h4>가족·아이</h4>
          <p>아동(7·8세) 입장료·패스 연령 구간을 미리 확인. 일부 박물관은 Chicago 주민 할인/무료 요일이 있으나 여행객은 해당 없을 수 있음.</p>
        </div>
        <div>
          <h4>분실 대비</h4>
          <p>카드·여권·숙소 주소를 사진으로 백업. 앱에서 카드 OFF. 숙소·렌트 계약서 이메일 보관.</p>
        </div>
      </div>
    </section>

    <section class="card tips-section">
      <h3>뉴욕 3일 — 할인·미리 할 일</h3>
      <p class="muted" style="margin-top:0;">동부 일정: 미드타운·센트럴파크 · AMNH/MoMA · 자유의 여신 페리 · 브루클린 브릿지</p>
      <ul class="tips-bullets">
        <li><strong>교통: OMNY</strong> — 지하철·버스는 카드/폰 탭 결제(별도 MetroCard 불필요인 경우가 많음). 주간 상한(주 단위 fare capping) 정책 확인 후 같은 카드로 탭하면 유리할 수 있음.</li>
        <li><strong>Statue of Liberty / Ferry</strong> — 공식 페리·크루즈는 주말·오후 슬롯이 빨리 찹니다. 출국 전 날짜·시간 예약.</li>
        <li><strong>AMNH · MoMA · Empire State</strong> — 공식 사이트/앱 타임드 엔트리. 당일 현장은 대기·매진 리스크.</li>
        <li><strong>Central Park Zoo</strong> — 온라인 티켓이 줄·가격에 유리한 편. 날씨 좋은 날로.</li>
        <li><strong>9/11 Memorial</strong> — 야외 메모리얼은 무료. 뮤지엄 입장은 별도·예약 권장.</li>
        <li><strong>CityPASS / Go City NYC</strong> — 전망대+박물관을 몰아서 볼 때만 손익 계산. 3일이면 개별 예약이 더 싼 경우도 많음.</li>
        <li><strong>세금환급(Tax Free)</strong> — 일부 매장·절차 조건이 까다롭고 수수료가 있어, 소액 기념품은 기대하지 않는 편이 낫습니다.</li>
        <li><strong>뉴욕→시카고 국내선</strong> — 기내 반입·위탁 규정, TSA PreCheck 없으면 공항 여유 있게.</li>
      </ul>
    </section>

    <section class="card tips-section">
      <h3>시카고 10일 — 할인·미리 할 일</h3>
      <p class="muted" style="margin-top:0;">일정: Art Institute · Shedd/Field · MSI · Lincoln Park Zoo(무료) · Architecture Cruise · Skydeck/360 · 근교</p>
      <ul class="tips-bullets">
        <li><strong>Chicago CityPASS / Go City</strong> — Shedd·Skydeck·건축 크루즈·MSI·Art Institute를 묶으면 개별 합보다 저렴한 경우가 많음. 구매 직후 앱에서 <em>타임슬롯 예약</em>(Shedd·Skydeck 필수에 가까움).</li>
        <li><strong>Architecture River Cruise</strong> — 주말·오전 인기. CityPASS 포함 여부와 별도로 시간 선점.</li>
        <li><strong>Lincoln Park Zoo</strong> — 입장 무료(기부 선택). 예산 절약 데이로 활용.</li>
        <li><strong>Art Institute</strong> — 아동 요금·온라인 티켓 확인. CityPASS 시 패스 입장 동선 따름.</li>
        <li><strong>Museum Campus (Shedd·Field·Adler)</strong> — 주차비 높음. 렌트카면 주차 앱/요금 미리 보거나 CTA·우버 병행.</li>
        <li><strong>Willis Tower Skydeck / 360 CHICAGO</strong> — 일몰·주말 슬롯 선예약. 둘 다 할 필요는 없음(하나만 선택 추천).</li>
        <li><strong>CTA Ventra</strong> — 단기면 카드 탭·Ventra 앱. 렌트카 위주면 시내만 필요할 때 이용.</li>
        <li><strong>렌트카 편도 NYC→ORD</strong> — 보증은 신용카드, 일일 결제는 트래블월렛 가능 여부 업체마다 다름. 연료·톨·주차 영수증 보관.</li>
        <li><strong>귀국편 ORD 06:00대</strong> — 전날 밤 숙소 근처 정리, 렌트 반납 시각을 비행 전에 맞춰 여유 확보.</li>
      </ul>
    </section>

    <section class="card tips-section">
      <h3>이 여행에 맞는 추천 조합</h3>
      <ol class="tips-checklist">
        <li><strong>주력:</strong> 트래블월렛(USD 충전) — 식당·교통 탭·티켓·쇼핑</li>
        <li><strong>보조:</strong> 트래블로그(다른 브랜드) — ATM·결제 거절 시 백업</li>
        <li><strong>신용 1장:</strong> 호텔·렌트 보증, 항공 부가서비스, 비상</li>
        <li><strong>현금:</strong> 소액만(팁·가판대·비상). 미국 대도시는 카드로 대부분 해결</li>
        <li><strong>패스:</strong> 시카고는 CityPASS vs 개별 입장 손익을 일정 탭 동선 기준으로 비교 후 구매 → 바로 예약</li>
      </ol>
      <p class="muted tips-footnote">관련 일정은 <a href="#" data-goto="east-plan">동부 3일</a> · <a href="#" data-goto="chi-plan">시카고 10일</a> · <a href="#" data-goto="cars">렌트카</a> 탭을 함께 보세요.</p>
    </section>
    """


def tips_styles() -> str:
    return """
    .tips-hero .route-stat strong { font-size: 1.25rem; }
    .tips-section h3 { margin: 0 0 10px; }
    .tips-section h4 { margin: 0 0 6px; font-size: 1.02rem; }
    .tips-checklist { margin: 0; padding-left: 1.2rem; line-height: 1.55; }
    .tips-checklist li { margin: 0 0 10px; }
    .tips-bullets { margin: 8px 0 0; padding-left: 1.2rem; line-height: 1.55; }
    .tips-bullets li { margin: 0 0 10px; }
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
    }
    .tips-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px 18px;
      margin-top: 8px;
    }
    .tips-grid p { margin: 0; font-size: 0.92rem; line-height: 1.45; color: var(--muted, #5b6470); }
    .tips-grid h4 { color: var(--ink, #1a1f24); }
    @media (max-width: 900px) {
      .tips-compare, .tips-grid { grid-template-columns: 1fr; }
    }
    """
