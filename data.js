// ============================================================
// JT Morgan 10X — 텐버의 피 (데이터 파일)
// 이 파일은 텐버가 스카우트/점검을 실행할 때마다 갱신한다.
// 화면(index.html)은 이 파일만 읽어서 그린다.
// ============================================================
const TENVER_DATA = {
  version: "v0.1",
  updatedAt: "2026-07-02 18:30",
  updateNote: "제1차 스카우트 반영 · 강령 제정 완료 · 기준가 ★표시 종목은 다음 점검 시 확정",

  // 기능 5: 시장 시세 (텐버가 점검 시 갱신)
  market: [
    { name: "KOSPI",  value: "8,303.41", change: "-7.7% (7/2 장중)", dir: "down", note: "7/1 종가 기준" },
    { name: "KOSDAQ", value: "929.35",   change: "-7.0% (7/2 장중)", dir: "down", note: "매도 사이드카 발동" },
    { name: "시장 국면", value: "경계", change: "AI 버블 경고 보도", dir: "warn", note: "민스키 국면 판정 예정" },
    { name: "온도계", value: "미측정", change: "다음 점검 시 가동", dir: "flat", note: "강령 모듈 0" }
  ],

  alert: "⚠️ 2026-07-02 코스피 급락(-7.7%) 직후 국면 — 강령 급락일 프로토콜 적용 중. 아래 주전 10은 강령 제정 이전 선발로 전면 재심사 대기.",

  // 기능 1 + 9: 주전 10종목 (기준가 → 목표가 10배, 달성률)
  // basePrice: 2026-07-01 종가(★는 잠정), currentPrice: 최근 점검 시 갱신(null이면 미갱신)
  main10: [
    { name: "네오셈",           code: "253590", sector: "AI·반도체",   basePrice: 11750, targetPrice: 117500, currentPrice: null, confidence: "상",   thesis: "세계 최초 CXL 검사장비 상용화 + 흑자", starred: false },
    { name: "아이쓰리시스템",   code: "214430", sector: "방산·우주",   basePrice: 60900, targetPrice: 609000, currentPrice: null, confidence: "상",   thesis: "국내 유일 군용 적외선 센서 — K방산 수출 레버리지", starred: true },
    { name: "에이프릴바이오",   code: "397030", sector: "바이오",      basePrice: 34950, targetPrice: 349500, currentPrice: null, confidence: "상",   thesis: "누적 1.2조 기술수출 + 4년 개발자금 확보", starred: true },
    { name: "에이직랜드",       code: "445090", sector: "AI·반도체",   basePrice: 23850, targetPrice: 238500, currentPrice: null, confidence: "중상", thesis: "TSMC VCA 국내 유일 — 매출 +242%", starred: false },
    { name: "필옵틱스",         code: "161580", sector: "AI·반도체",   basePrice: 36550, targetPrice: 365500, currentPrice: null, confidence: "중상", thesis: "유리기판 TGV 장비 풀라인업", starred: false },
    { name: "큐로셀",           code: "372320", sector: "바이오",      basePrice: 30100, targetPrice: 301000, currentPrice: null, confidence: "중",   thesis: "국산 1호 CAR-T 품목허가 완료", starred: true },
    { name: "넥스트바이오메디컬", code: "389650", sector: "의료기기",  basePrice: 39900, targetPrice: 399000, currentPrice: null, confidence: "중",   thesis: "메드트로닉 판권 + 흑자전환 예고", starred: true },
    { name: "아이씨티케이",     code: "456010", sector: "보안반도체",  basePrice: 17950, targetPrice: 179500, currentPrice: null, confidence: "중",   thesis: "PUF 보안칩 빅테크 공급 가시화", starred: false },
    { name: "나노신소재",       code: "121600", sector: "2차전지 소재", basePrice: 49300, targetPrice: 493000, currentPrice: null, confidence: "중",   thesis: "CNT 도전재 글로벌 선두 — 턴어라운드 확인", starred: false },
    { name: "하이젠알앤엠",     code: "160190", sector: "로봇",        basePrice: 19170, targetPrice: 191700, currentPrice: null, confidence: "중",   thesis: "휴머노이드 1대당 액추에이터 25~60개", starred: true }
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
    { date: "2026-07-02", title: "텐버 강령 제정", body: "투자 고전 17권을 4개 학파 2라운드로 정독 → 03 Philosophy(신념 11개조·절대 원칙 8·6모듈 파이프라인) 완성. 기존 주전 10은 강령 기준 전면 재심사 대상으로 지정." },
    { date: "2026-07-02", title: "제1차 스카우트 (창단)", body: "리서치 요원 4명 병렬 조사로 23개 후보 발굴 → 주전 10 / 후보 10 선발. 전 종목 정상 거래 확인. 반성: ★종목 기준가 미확정, DART 원문 검증 미완." },
    { date: "2026-07-02", title: "시장 급변 기록", body: "코스피 -7.7% 급락, 코스닥 매도 사이드카. 'AI 버블 붕괴' 경고 보도. 급락일 프로토콜에 따라 신규 결정 보류, 사기 폭로 계절 대비 회계 재점검 예정." }
  ],

  disclaimer: "본 화면의 모든 내용은 투자 참고 자료이며 투자 권유가 아닙니다. 예측이 아닌 근거 기반 리서치이며, 최종 판단과 책임은 투자자 본인에게 있습니다. — 텐버 강령 제2장 7조"
};
