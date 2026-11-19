#!/usr/bin/env python3
# JT Morgan 10X — DART 공시 감시기 (무인증 companyRSS 기반)
# 종목별 DART RSS(companyRSS.xml?crpCd=고유번호)를 돌며 최근 N일 공시를 추린다.
# todayRSS(전체 최근공시)는 빈 채널로 확인돼 폐기 — 종목별 조회가 확정 라인.
# DART OpenAPI 키 없이 작동(제목·링크·시각) — 원문 자동 검증은 키 확보 후 승격 예정.
# 사용: python3 scripts/dart_watch.py              (최근 7일)
#       python3 scripts/dart_watch.py --days 30    (기간 지정)
#       python3 scripts/dart_watch.py --name 에스앤디 [--days 90]  (단일 종목)
import json, os, ssl, sys, time, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

# 감시 명단은 코드에 적지 않는다 — 비공개 형제 저장소(tenver-core)의 원장에서 읽는다.
LEDGER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                      "tenver-core", "ledger", "positions.json")

def load_corp():
    """원장에서 {종목명: DART 고유번호}를 만든다 — 제외 종목을 뺀 전 구분 + 게이트 감시(watch_only)."""
    with open(LEDGER, encoding="utf-8") as f:
        led = json.load(f)
    corp = {p["name"]: p["dart"] for p in led["positions"] if p.get("dart") and p["tier"] != "제외"}
    corp.update({w["name"]: w["dart"] for w in led.get("watch_only", [])})
    return corp

CORP = load_corp()

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

    if only and only not in CORP:
        print(f"미등록 종목: {only} — 원장(tenver-core/ledger/positions.json)에 dart 고유번호를 추가하세요", file=sys.stderr)
        sys.exit(1)
    targets = {only: CORP[only]} if only else CORP

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
