#!/usr/bin/env python3
# JT Morgan 10X — DART 공시 감시기 (무인증 기간 검색 기반)
# 종목별로 DART 상세검색(detailSearch.ax, 고유번호+기간)을 돌려 최근 N일 공시를 추린다.
# companyRSS는 최근 며칠치만 내려와 7일 점검·공백 소급에서 누락이 생겨 폐기(2026-11-20 확인).
# DART OpenAPI 키 없이 작동(제목·링크·접수일) — 원문 자동 검증은 키 확보 후 승격 예정.
# 사용: python3 scripts/dart_watch.py              (최근 7일)
#       python3 scripts/dart_watch.py --days 30    (기간 지정)
#       python3 scripts/dart_watch.py --name 종목명 [--days 90]  (단일 종목)
import json, os, re, ssl, sys, time, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

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

SEARCH = "https://dart.fss.or.kr/dsab007/detailSearch.ax"
MAX_ROWS = 100

def fetch(url, data=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "Mozilla/5.0 (TenverBot)"})
    with urllib.request.urlopen(req, context=CTX, timeout=20) as r:
        return r.read()

def pull(name, crp, since):
    """종목 하나의 since(그 날 포함) 이후 공시 [(접수일, 종목, 제목, 링크)]를 돌려준다.
    제출인이 회사가 아니면(대량보유 신고자 등) 제목 뒤에 <제출인>을 붙인다."""
    form = {"currentPage": 1, "maxResults": MAX_ROWS, "maxLinks": 10, "sort": "date", "series": "desc",
            "textCrpCik": crp, "startDate": f"{since:%Y%m%d}", "endDate": f"{datetime.now(KST):%Y%m%d}",
            "option": "corp", "businessCode": "all", "typesOfBusiness": "all",
            "corporationType": "all", "closingAccountsMonth": "all"}
    page = fetch(SEARCH, urllib.parse.urlencode(form).encode()).decode("utf-8", "replace")
    out = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.S):
        m = re.search(r"rcpNo=(\d+)", tr)
        tds = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", td)).strip() for td in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if not m or len(tds) < 5:
            continue
        dt = datetime.strptime(tds[4], "%Y.%m.%d").replace(tzinfo=KST)
        by = "" if tds[3].replace(" ", "") == name.replace(" ", "") else f" <{tds[3]}>"
        out.append((dt, name, tds[2] + by, f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={m.group(1)}"))
    if len(out) >= MAX_ROWS:
        print(f"! {name}: {MAX_ROWS}건 상한 도달 — 더 오래된 공시가 잘렸을 수 있음", file=sys.stderr)
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
        print(f"- [{dt:%m/%d}] ◆{name} | {title}\n  {link}")
    if not hits:
        print("- 관리 종목 신규 공시 없음")
    for e in errs:
        print(f"! 조회 실패 — {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
