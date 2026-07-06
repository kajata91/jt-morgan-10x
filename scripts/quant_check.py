#!/usr/bin/env python3
# JT Morgan 10X — 정량 검사 도구 (유동성·시세 이력)
# 강령 모듈 3 보강: GIC 블랙록 렌즈의 $50M 유동성 테스트를 정밀 수치로 자동화.
# 데이터: FinanceDataReader(네이버 기반, 1순위) — 실패 시 해당 종목 "불확실" 표기.
import sys, datetime
import FinanceDataReader as fdr

USD_KRW = 1552  # 환율 (수동 갱신)
TEST_USD = 50_000_000  # $50M 기관 포지션 테스트
PART = 0.20  # 시장 참여율 상한 20%

def check(code, name, days=60):
    end = datetime.date.today()
    start = end - datetime.timedelta(days=days * 2)
    try:
        df = fdr.DataReader(code, start.isoformat(), end.isoformat())
        if df is None or len(df) < 10:
            return {"code": code, "name": name, "err": "데이터 부족"}
        df = df.tail(days)
        adv = float((df["Close"] * df["Volume"]).mean())  # 일평균 거래대금(원)
        last = float(df["Close"].iloc[-1])
        hi52, lo52 = None, None
        try:
            y = fdr.DataReader(code, (end - datetime.timedelta(days=370)).isoformat(), end.isoformat())
            hi52, lo52 = float(y["Close"].max()), float(y["Close"].min())
        except Exception:
            pass
        pos = TEST_USD * USD_KRW
        days_needed = pos / (adv * PART) if adv > 0 else None
        return {"code": code, "name": name, "last": last, "adv_bil": adv / 1e8,
                "days50m": days_needed, "hi52": hi52, "lo52": lo52}
    except Exception as e:
        return {"code": code, "name": name, "err": str(e)[:60]}

def main():
    targets = [  # 2026-07-06 재설정 명단 (주전 4 / 정찰 2 / 후보 14 / 투기 1)
        ("214430", "아이쓰리시스템(주전)"), ("445090", "에이직랜드(주전)"),
        ("389650", "넥스트바이오메디컬(주전)"), ("260970", "에스앤디(주전)"),
        ("053610", "프로텍(정찰)"), ("308430", "셀비온(정찰)"),
        ("094360", "칩스앤미디어"), ("039200", "오스코텍"), ("083650", "비에이치아이"),
        ("397030", "에이프릴바이오"), ("372320", "큐로셀"), ("253590", "네오셈"), ("121600", "나노신소재"),
        ("484590", "삼양컴텍"), ("448710", "코츠테크놀로지"), ("272110", "케이엔제이"), ("092870", "엑시콘"),
        ("338220", "뷰노"), ("099190", "아이센스"), ("451760", "컨텍"),
        ("456010", "아이씨티케이(투기)"),
    ]
    print(f"# 유동성 정밀 검사 — 60일 평균 거래대금 기준, $50M={TEST_USD*USD_KRW/1e8:.0f}억원, 참여율 {PART:.0%}")
    print(f"{'종목':<16} {'현재가':>10} {'일평균대금(억)':>12} {'$50M소요(일)':>12} {'52주 고/저 대비':>18}")
    for code, name in targets:
        r = check(code, name)
        if "err" in r:
            print(f"{name:<16} 불확실 — {r['err']}")
            continue
        hilo = ""
        if r["hi52"]:
            hilo = f"고점-{(1 - r['last'] / r['hi52']) * 100:.0f}% / 저점+{(r['last'] / r['lo52'] - 1) * 100:.0f}%"
        print(f"{r['name']:<16} {r['last']:>10,.0f} {r['adv_bil']:>12.1f} {r['days50m']:>12.0f} {hilo:>18}")

if __name__ == "__main__":
    main()
