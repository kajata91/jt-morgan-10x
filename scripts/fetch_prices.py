#!/usr/bin/env python3
# JT Morgan 10X — 전 종목 시세 수집기
# 네이버 모바일 API에서 코스피·코스닥 전 종목의 최신가(장 마감 후 = 종가)를 받아 prices.js 생성.
# GitHub Actions가 평일 16:50 KST에 실행 → 대시보드의 '내 종목'·주전·추가 추천 현재가 자동 갱신.
import json, ssl, time, sys, datetime, urllib.request

CTX = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0 (TenverBot; +https://kajata91.github.io/jt-morgan-10x/)"}

def fetch(market):
    items, page = {}, 1
    while page <= 60:
        url = f"https://m.stock.naver.com/api/stocks/marketValue/{market}?page={page}&pageSize=100"
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, context=CTX, timeout=20) as r:
            data = json.load(r)
        stocks = data.get("stocks") or []
        if not stocks:
            break
        for s in stocks:
            try:
                code = s["itemCode"]
                name = s["stockName"]
                price = int(str(s["closePrice"]).replace(",", ""))
                items[code] = {"n": name, "p": price, "m": market}
            except (KeyError, ValueError):
                continue
        total = data.get("totalCount") or 0
        if total and page * 100 >= int(total):
            break
        page += 1
        time.sleep(0.15)
    return items

def main():
    items = {}
    for mkt in ("KOSPI", "KOSDAQ"):
        got = fetch(mkt)
        print(f"{mkt}: {len(got)} stocks", file=sys.stderr)
        items.update(got)
    if len(items) < 500:
        print("ERROR: too few stocks fetched — aborting to keep last good prices.js", file=sys.stderr)
        sys.exit(1)
    kst = datetime.timezone(datetime.timedelta(hours=9))
    as_of = datetime.datetime.now(kst).strftime("%Y-%m-%d %H:%M KST")
    payload = {"asOf": as_of, "count": len(items), "items": items}
    js = "// 자동 생성 파일 — scripts/fetch_prices.py (수동 편집 금지)\nconst TENVER_PRICES = " + \
         json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n"
    out = __file__.rsplit("/scripts/", 1)[0] + "/prices.js"
    with open(out, "w", encoding="utf-8") as f:
        f.write(js)
    print(f"OK: {len(items)} stocks -> prices.js ({as_of})", file=sys.stderr)

if __name__ == "__main__":
    main()
