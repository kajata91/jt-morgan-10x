#!/usr/bin/env python3
# JT Morgan 10X — DART 공시 감시기 (무인증 companyRSS 기반)
# 종목별 DART RSS(companyRSS.xml?crpCd=고유번호)를 돌며 최근 N일 공시를 추린다.
# todayRSS(전체 최근공시)는 빈 채널로 확인돼 폐기 — 종목별 조회가 확정 라인.
# DART OpenAPI 키 없이 작동(제목·링크·시각) — 원문 자동 검증은 키 확보 후 승격 예정.
# 사용: python3 scripts/dart_watch.py              (최근 7일)
#       python3 scripts/dart_watch.py --days 30    (기간 지정)
#       python3 scripts/dart_watch.py --name 에스앤디 [--days 90]  (단일 종목)
import ssl, sys, time, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

# 2026-07-07 명단 (원장과 동기 — 재설정 시 갱신) — DART 고유번호는 RSS 채널명 역검증 완료
CORP = {
    # 주전 3
    "아이쓰리시스템": "00612489", "넥스트바이오메디컬": "01385050", "에스앤디": "00560849",
    # 정찰석 2
    "프로텍": "00325112", "셀비온": "01275489",
    # 후보 15 (0번 에이직랜드 포함)
    "에이직랜드": "01540453", "칩스앤미디어": "00579971", "오스코텍": "00263654",
    "비에이치아이": "00409788", "에이프릴바이오": "01375822", "큐로셀": "01492651",
    "네오셈": "01170865", "나노신소재": "00439965", "삼양컴텍": "00141583",
    "코츠테크놀로지": "00959210", "케이엔제이": "00769158", "엑시콘": "00611736",
    "뷰노": "01344202", "아이센스": "00550994", "컨텍": "01685251",
    # 투기 1
    "아이씨티케이": "01373709",
    # 관심 이벤트 감시 (재심 대기·게이트 관련)
    "삼양식품": "00126955",   # 에스앤디 내재화 게이트
    "에스티아이": "00298340", "듀켐바이오": "00867034", "티앤엘": "00608440",
    "한중엔시에스": "00474588",
}

KST = timezone(timedelta(hours=9))
CTX = ssl.create_default_context()

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (TenverBot)"})
    with urllib.request.urlopen(req, context=CTX, timeout=20) as r:
        return r.read()

def pull(name, crp, since):
    """종목 하나의 RSS에서 since 이후 공시 [(dt, 종목, 제목, 링크)]를 돌려준다.
    제목 앞 괄호는 '제출인' 표기라 제3자(대량보유 신고 법인 등)일 수 있음 — 종목명 태그 필수."""
    root = ET.fromstring(fetch(f"https://dart.fss.or.kr/api/companyRSS.xml?crpCd={crp}"))
    out = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        try:
            dt = parsedate_to_datetime(pub).astimezone(KST)
        except Exception:
            continue
        if dt >= since:
            out.append((dt, name, title, link))
    return out

def main():
    args = sys.argv[1:]
    days = 7
    if "--days" in args:
        days = int(args[args.index("--days") + 1])
    only = args[args.index("--name") + 1] if "--name" in args else None

    targets = {only: CORP[only]} if only else CORP
    if only and only not in CORP:
        print(f"미등록 종목: {only} — CORP 딕셔너리에 고유번호를 추가하세요", file=sys.stderr)
        sys.exit(1)

    since = datetime.now(KST) - timedelta(days=days)
    hits, errs = [], []
    for name, crp in targets.items():
        try:
            hits += pull(name, crp, since)
        except Exception as e:
            errs.append(f"{name}: {e}")
        time.sleep(0.2)  # 예의상 간격

    hits.sort(reverse=True)
    print(f"# DART 공시 감시 — 최근 {days}일, {len(targets)}종목 중 신규 {len(hits)}건 ({datetime.now(KST):%Y-%m-%d %H:%M} KST)")
    for dt, name, title, link in hits:
        print(f"- [{dt:%m/%d %H:%M}] ◆{name} | {title}\n  {link}")
    if not hits:
        print("- 관리 종목 신규 공시 없음")
    for e in errs:
        print(f"! 조회 실패 — {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
