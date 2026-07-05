#!/usr/bin/env python3
# JT Morgan 10X — TOP GUNS 당일 랭킹 수집기 (한국·미국 상승률 상위)
# 네이버 API에서 당일(최근 거래일) 상승률 랭킹을 받아 topguns.js 생성.
# 초소형 잡주 제외를 위해 시총 필터 적용: KR 1,000억+, US $1B+.
# GitHub Actions가 fetch_prices.py 직후 실행 → 대시보드 TOP GUNS 카드 자동 갱신.
import json, ssl, time, sys, datetime, urllib.request

CTX = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0 (TenverBot; +https://kajata91.github.io/jt-morgan-10x/)"}

def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, context=CTX, timeout=20) as r:
        return json.load(r)

def num(v):
    try:
        return float(str(v).replace(",", ""))
    except (ValueError, TypeError):
        return 0.0

ETP_WORDS = ("KODEX", "TIGER", "RISE", "PLUS", "ACE", "SOL", "KIWOOM", "HANARO", "WON",
             "레버리지", "인버스", "ETN", "채권", "선물", "스팩", "단일종목", "TOP10", "액티브")

def fetch_kr(limit=12, min_cap_eok=1000):
    rows = []
    for mkt in ("KOSPI", "KOSDAQ"):
        d = get_json(f"https://m.stock.naver.com/api/stocks/up/{mkt}?page=1&pageSize=40")
        for s in d.get("stocks") or []:
            name = s.get("stockName") or ""
            if any(w in name for w in ETP_WORDS):  # ETF·ETN·스팩 제외 — 개별 종목만
                continue
            cap = num(s.get("marketValue"))  # 억원
            if cap < min_cap_eok:
                continue
            rows.append({
                "name": s.get("stockName"), "code": s.get("itemCode"), "mkt": mkt,
                "price": num(s.get("closePrice")), "pct": num(s.get("fluctuationsRatio")),
                "cap": cap,
            })
        time.sleep(0.15)
    rows.sort(key=lambda r: -r["pct"])
    rows = rows[:limit]
    for r in rows:  # PER·PBR 보강 (랭킹 종목만)
        try:
            d = get_json(f"https://m.stock.naver.com/api/stock/{r['code']}/integration")
            info = {t.get("code"): t.get("value") for t in d.get("totalInfos") or []}
            r["per"] = info.get("per") or "—"
            r["pbr"] = info.get("pbr") or "—"
        except Exception:
            r["per"] = r["pbr"] = "—"
        time.sleep(0.12)
    return rows

def fetch_us(limit=12, min_cap_man_usd=100000):  # 10만 만USD = $1B
    rows = []
    for exch in ("NASDAQ", "NYSE"):
        d = get_json(f"https://api.stock.naver.com/stock/exchange/{exch}/up?page=1&pageSize=25")
        for s in d.get("stocks") or []:
            cap = num(s.get("marketValue"))  # 만 USD
            if cap < min_cap_man_usd:
                continue
            ind = s.get("industryCodeType") or {}
            rows.append({
                "name": s.get("stockName"), "nameEng": s.get("stockNameEng"),
                "sym": s.get("symbolCode"), "exch": exch,
                "price": num(s.get("closePrice")), "pct": num(s.get("fluctuationsRatio")),
                "capB": round(cap / 100000.0, 1),  # $B
                "sector": ind.get("industryGroupKor") or "—",
            })
        time.sleep(0.15)
    rows.sort(key=lambda r: -r["pct"])
    return rows[:limit]

def main():
    kst = datetime.timezone(datetime.timedelta(hours=9))
    as_of = datetime.datetime.now(kst).strftime("%Y-%m-%d %H:%M KST")
    payload = {"asOf": as_of}
    try:
        payload["kr"] = fetch_kr()
        print(f"KR top: {len(payload['kr'])}", file=sys.stderr)
    except Exception as e:
        print(f"WARN kr fail: {e}", file=sys.stderr)
        payload["kr"] = []
    try:
        payload["us"] = fetch_us()
        print(f"US top: {len(payload['us'])}", file=sys.stderr)
    except Exception as e:
        print(f"WARN us fail: {e}", file=sys.stderr)
        payload["us"] = []
    if not payload["kr"] and not payload["us"]:
        print("ERROR: both markets empty — keep last good topguns.js", file=sys.stderr)
        sys.exit(1)
    js = "// 자동 생성 파일 — scripts/fetch_topguns.py (수동 편집 금지)\nconst TENVER_TOPGUNS = " + \
         json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n"
    out = __file__.rsplit("/scripts/", 1)[0] + "/topguns.js"
    with open(out, "w", encoding="utf-8") as f:
        f.write(js)
    print(f"OK -> topguns.js ({as_of})", file=sys.stderr)

if __name__ == "__main__":
    main()
