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

def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, context=CTX, timeout=20) as r:
        return json.load(r)

def num(v):
    return float(str(v).replace(",", ""))

def fetch_market():
    """KOSPI·KOSDAQ 지수 + 원/달러 환율 + 연중 종가 범위 → 대시보드 시장 스트립 자동 갱신용."""
    mkt = {}
    year = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y")
    for idx in ("KOSPI", "KOSDAQ"):
        d = get_json(f"https://m.stock.naver.com/api/index/{idx}/basic")
        c = num(d["closePrice"])
        lo = hi = c
        page = 1
        while page <= 5:  # pageSize 한도 60 — 5페이지 = 300거래일, 연초까지 충분
            rows = get_json(f"https://m.stock.naver.com/api/index/{idx}/price?pageSize=60&page={page}")
            stop = False
            for row in rows:
                if str(row.get("localTradedAt", "")) < f"{year}-01-01":
                    stop = True
                    break
                v = num(row["closePrice"])
                lo, hi = min(lo, v), max(hi, v)
            if stop or len(rows) < 60:
                break
            page += 1
            time.sleep(0.15)
        mkt[idx.lower()] = {
            "c": c,
            "chg": num(d["compareToPreviousClosePrice"]),
            "pct": num(d["fluctuationsRatio"]),
            "lo": lo, "hi": hi,
            "at": str(d.get("localTradedAt", ""))[:16].replace("T", " "),
        }
    fx = get_json("https://m.stock.naver.com/front-api/marketIndex/productDetail"
                  "?category=exchange&reutersCode=FX_USDKRW")["result"]
    mkt["usdkrw"] = {"c": num(fx["closePrice"]), "chg": num(fx["fluctuations"]), "pct": num(fx["fluctuationsRatio"])}
    return mkt

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
    try:  # 시장 지표는 부가 기능 — 실패해도 종목 시세는 배포
        market = fetch_market()
        market["asOf"] = as_of
        js += "const TENVER_MARKET = " + json.dumps(market, ensure_ascii=False, separators=(",", ":")) + ";\n"
        print(f"market: KOSPI {market['kospi']['c']:,.2f} / KOSDAQ {market['kosdaq']['c']:,.2f} / USDKRW {market['usdkrw']['c']:,.1f}", file=sys.stderr)
    except Exception as e:
        print(f"WARN: market fetch failed ({e}) — stock prices only", file=sys.stderr)
    out = __file__.rsplit("/scripts/", 1)[0] + "/prices.js"
    with open(out, "w", encoding="utf-8") as f:
        f.write(js)
    print(f"OK: {len(items)} stocks -> prices.js ({as_of})", file=sys.stderr)

if __name__ == "__main__":
    main()
