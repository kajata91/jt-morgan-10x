// ============================================================
// JT Morgan 10X — 텐버의 피 (데이터 파일)
// 이 파일은 텐버가 스카우트/점검을 실행할 때마다 갱신한다.
// 화면(index.html)은 이 파일만 읽어서 그린다.
// ============================================================
const TENVER_DATA = {
  version: "v0.2",
  updatedAt: "2026-07-02 17:40",
  updateNote: "시장 온도계 첫 측정 반영(경계) · 강령 기준 재심사 진행 중 · 종목 현재가는 재심사 완료 시 갱신",

  // 기능 5: 시장 시세 (텐버가 점검 시 갱신)
  market: [
    { name: "KOSPI",   value: "7,648.09", change: "-7.89% (7/2 종가)", dir: "down", note: "8,000선 붕괴 · 매도 사이드카" },
    { name: "KOSDAQ",  value: "866.72",   change: "-6.74% (7/2 종가)", dir: "down", note: "900선 붕괴" },
    { name: "원/달러", value: "1,552.3",  change: "17년 만의 원화 최약세권", dir: "down", note: "7/2 기준" },
    { name: "외국인",  value: "-150.7조", change: "연초 이후 누적 순매도", dir: "down", note: "6월에만 -48.6조" },
    { name: "시장 온도", value: "경계",   change: "도취 말기 → 경색 진입", dir: "warn", note: "2026-07-02 측정" }
  ],

  // 시장 온도계 (강령 모듈 0) — score: 0(패닉/바닥) ~ 100(도취/과열)
  temperature: {
    label: "경계",
    score: 72,
    asOf: "2026-07-02",
    zones: ["패닉", "침체", "중립", "경계", "도취"],
    summary: "신용융자 사상 최대(38.6조)·IPO 따따블 광풍·PBR 2.3 역사적 상단(도취 증거)과 중앙그룹 2.8조 회생·스프레드 확대·서킷브레이커 3회(경색 증거)가 중첩. 민스키 국면: 도취 말기→경색 진입. 막스 약세장 1~2단계 초입.",
    rules: [
      "신규 편입 요구수익 +50% 상향",
      "강요 매도 신호 1/3 점등 — 칼날 잡기 자격 미달",
      "급락일 프로토콜: 신규 결정 24시간 냉각",
      "방어 모드: 보유 전 종목 회계 재점검"
    ]
  },

  // 코스피 확인 지점 추이 (확인된 값만 연결한 개략 — 전체 일별 데이터 아님)
  kospiTrend: {
    note: "확인된 지점만 연결한 개략 추이 (일별 전체 데이터 아님)",
    points: [
      { label: "6/8",  value: 7477, note: "서킷브레이커 · 장중" },
      { label: "6/11", value: 7764, note: "종가" },
      { label: "6월중순", value: 9000, note: "9천선 터치 · 장중" },
      { label: "7/1",  value: 8303, note: "종가" },
      { label: "7/2",  value: 7648, note: "종가 -7.89%" }
    ]
  },

  alert: "⚠️ 강령 기준 전면 재심사 진행 중 (심사 요원 4명 가동) — 아래 주전 10은 재심사 완료 전 잠정 명단입니다. 시장 온도 '경계' 판정에 따라 방어 모드가 발동되었습니다.",

  // 기능 1 + 9: 주전 10종목
  main10: [
    { name: "네오셈",             code: "253590", sector: "AI·반도체",    basePrice: 11750, targetPrice: 117500, currentPrice: null, confidence: "상",   thesis: "세계 최초 CXL 검사장비 상용화 + 흑자", starred: false },
    { name: "아이쓰리시스템",     code: "214430", sector: "방산·우주",    basePrice: 60900, targetPrice: 609000, currentPrice: null, confidence: "상",   thesis: "국내 유일 군용 적외선 센서 — K방산 수출 레버리지", starred: true },
    { name: "에이프릴바이오",     code: "397030", sector: "바이오",       basePrice: 34950, targetPrice: 349500, currentPrice: null, confidence: "상",   thesis: "누적 1.2조 기술수출 + 4년 개발자금 확보", starred: true },
    { name: "에이직랜드",         code: "445090", sector: "AI·반도체",    basePrice: 23850, targetPrice: 238500, currentPrice: null, confidence: "중상", thesis: "TSMC VCA 국내 유일 — 매출 +242%", starred: false },
    { name: "필옵틱스",           code: "161580", sector: "AI·반도체",    basePrice: 36550, targetPrice: 365500, currentPrice: null, confidence: "중상", thesis: "유리기판 TGV 장비 풀라인업", starred: false },
    { name: "큐로셀",             code: "372320", sector: "바이오",       basePrice: 30100, targetPrice: 301000, currentPrice: null, confidence: "중",   thesis: "국산 1호 CAR-T 품목허가 완료", starred: true },
    { name: "넥스트바이오메디컬", code: "389650", sector: "의료기기",     basePrice: 39900, targetPrice: 399000, currentPrice: null, confidence: "중",   thesis: "메드트로닉 판권 + 흑자전환 예고", starred: true },
    { name: "아이씨티케이",       code: "456010", sector: "보안반도체",   basePrice: 17950, targetPrice: 179500, currentPrice: null, confidence: "중",   thesis: "PUF 보안칩 빅테크 공급 가시화", starred: false },
    { name: "나노신소재",         code: "121600", sector: "2차전지 소재", basePrice: 49300, targetPrice: 493000, currentPrice: null, confidence: "중",   thesis: "CNT 도전재 글로벌 선두 — 턴어라운드 확인", starred: false },
    { name: "하이젠알앤엠",       code: "160190", sector: "로봇",         basePrice: 19170, targetPrice: 191700, currentPrice: null, confidence: "중",   thesis: "휴머노이드 1대당 액추에이터 25~60개", starred: true }
  ],

  // 기능 4: 후보 10종목
  bench10: [
    { name: "태성",        code: "323280", note: "유리기판 습식장비 — 시총 선반영 부담" },
    { name: "예스티",      code: "122640", note: "고압수소어닐링 — PER 과열" },
    { name: "칩스앤미디어", code: "094360", note: "비디오·NPU IP 로열티 복리 모델" },
    { name: "쎄트렉아이",   code: "099320", note: "국내 유일 위성 수출 — 체급 허들" },
    { name: "에스피지",     code: "058610", note: "정밀감속기 3종 양산 — 3~5배 시나리오" },
    { name: "오스코텍",     code: "039200", note: "렉라자 로열티 — 지배구조 분쟁" },
    { name: "원텍",        code: "336570", note: "미용의료기기 영업이익률 33%" },
    { name: "비에이치아이", code: "083650", note: "수주잔고 2.4조 — 체급 상단" },
    { name: "성광벤드",     code: "014620", note: "미국 LNG 피팅 — 사이클주" },
    { name: "에스비비테크", code: "389500", note: "하모닉 감속기 국산화 — 고위험" }
  ],

  // 기능 2: 텐버 업무 일지 (최신순)
  journal: [
    { date: "2026-07-02", title: "시장 온도계 첫 측정 — '경계'", body: "민스키 국면 '도취 말기→경색 진입' 판정. 신용융자 사상 최대·IPO 광풍(도취)과 중앙그룹 회생·스프레드 확대(경색) 중첩. 외국인 연초 이후 150조 순매도 vs 개인 매수. 강요 매도 신호 1/3 — 칼날 잡기 자격 미달. 신규 편입 요구수익 +50%." },
    { date: "2026-07-02", title: "강령 기준 전면 재심사 개시", body: "주전 10·후보 10 전체를 6모듈 파이프라인(생애주기→해자→거부권 체크리스트→10배 분해식)으로 재심사 중. 심사 요원 4명 + 온도계 요원 1명 가동." },
    { date: "2026-07-02", title: "텐버 강령 제정 · 대시보드 v0.2", body: "투자 고전 17권 통섭으로 03 Philosophy 완성. 대시보드를 사이드바·게이지·차트를 갖춘 프로토타입으로 개편. GitHub Pages 배포 완료." }
  ],

  disclaimer: "본 화면의 모든 내용은 투자 참고 자료이며 투자 권유가 아닙니다. 예측이 아닌 근거 기반 리서치이며, 최종 판단과 책임은 투자자 본인에게 있습니다. — 텐버 강령 제2장 7조"
};
