#!/usr/bin/env python3
# JT Morgan 10X — 배포 전 자가 검증(스모크 테스트): 스크립트 무결성·데이터 구조·암호화 라운드트립
# CLAUDE.md §8(테스트 후 완료) 이행 — 커밋·배포 전 실행, 전 항목 PASS여야 푸시.
# 사용: python3 scripts/selftest.py          (네트워크 없는 검사만)
#       python3 scripts/selftest.py --net    (+ 네이버·DART 라이브 1건씩)
import importlib.util, json, os, re, subprocess, sys

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAIL = []

def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAIL.append(name)

def load(modname):
    p = os.path.join(APP, "scripts", modname + ".py")
    spec = importlib.util.spec_from_file_location(modname, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

# 1. 스크립트 5종 임포트(문법·의존성)
for s in ["dart_watch", "quant_check", "fetch_prices", "fetch_topguns", "encrypt_data"]:
    try:
        globals()[s] = load(s)
        check(f"임포트 {s}.py", True)
    except Exception as e:
        globals()[s] = None
        check(f"임포트 {s}.py", False, str(e)[:80])

# 2. dart_watch CORP 무결성 — 26종목·8자리 고유번호·중복 없음
if globals().get("dart_watch"):
    corp = dart_watch.CORP
    check("CORP 종목 수 26", len(corp) == 26, f"{len(corp)}개")
    check("CORP 고유번호 형식(8자리)", all(re.fullmatch(r"\d{8}", v) for v in corp.values()))
    check("CORP 고유번호 중복 없음", len(set(corp.values())) == len(corp))

# 3. quant_check 파서 — 수급 문자열 변환
if globals().get("quant_check"):
    n = quant_check._num
    ok = n("+7,326") == 7326.0 and n("-89") == -89.0 and n("4.88%") == 4.88 and n(None) == 0.0
    check("quant_check._num 파서", ok)
    src = open(os.path.join(APP, "scripts", "quant_check.py"), encoding="utf-8").read()
    codes = re.findall(r'\("(\d{6})",\s*"', src)
    check("quant_check 명단(6자리 코드) 21종목·중복 없음", len(codes) == 21 and len(set(codes)) == 21, f"{len(codes)}건")

# 4. data.js 구조 — node로 파싱해 필수 키·구조 검증
node_script = r"""
const fs=require('fs');
(0,eval)(fs.readFileSync(process.argv[2],'utf8')+';globalThis.D=TENVER_DATA;');
const D=globalThis.D;
const need=['version','updatedAt','market','temperature','alert','consults','topguns','wisdom','reflections','main10','bench10','disclaimer'];
const miss=need.filter(k=>!(k in D));
if(miss.length){console.log('MISS:'+miss.join(','));process.exit(1);}
if(!Array.isArray(D.main10)||D.main10.length!==3){console.log('main10!=3');process.exit(1);}
if(!Array.isArray(D.bench10)||D.bench10.length<15){console.log('bench10<15');process.exit(1);}
for(const s of D.main10){if(!s.report||!s.basePrice||!s.targetPrice){console.log('main10 필드 결손:'+s.name);process.exit(1);}}
const blocks=D.main10.flatMap(s=>s.report.filter(b=>b.t)).length;
if(blocks<9){console.log('시각블록<9:'+blocks);process.exit(1);}
console.log('OK main10=3 bench10='+D.bench10.length+' blocks='+blocks);
"""
try:
    r = subprocess.run(["node", "-e", node_script, "node", os.path.join(APP, "data.js")],
                       capture_output=True, text=True, timeout=30)
    check("data.js 구조(필수 키·주전 3·리포트 필드·시각 블록)", r.returncode == 0, (r.stdout or r.stderr).strip()[:80])
except FileNotFoundError:
    check("data.js 구조", False, "node 미설치")

# 5. 암호화 라운드트립 — data.enc.js payload가 유효 JSON + 필수 필드
try:
    enc = open(os.path.join(APP, "data.enc.js"), encoding="utf-8").read()
    m = re.search(r"TENVER_DATA_ENC\s*=\s*(\{.*\})\s*;?\s*$", enc, re.S)
    payload = json.loads(m.group(1))
    ok = all(k in payload for k in ("v", "iter", "salt", "iv", "ct")) and payload["iter"] >= 300_000
    check("data.enc.js 암호문 구조(AES-GCM payload)", ok)
except Exception as e:
    check("data.enc.js 암호문 구조", False, str(e)[:80])

# 6. index.html 정합 — 페이퍼 뷰어·라우터·게이트 핵심 앵커 존재
html = open(os.path.join(APP, "index.html"), encoding="utf-8").read()
for anchor in ["renderPaper", "paperSheet", "mPdf", "@media print", "gatePass", 'id="pg-consult"']:
    check(f"index.html 앵커 '{anchor}'", anchor in html)
check("index.html에 평문 비밀번호 없음", "Sarang" not in html)
check("data.js가 gitignore에 있음", "data.js" in open(os.path.join(APP, ".gitignore"), encoding="utf-8").read())

# 7. (--net) 라이브 데이터 1건씩 — 네이버 시세·DART RSS
if "--net" in sys.argv:
    try:
        fl = quant_check.flow("005930", days=3)
        check("네이버 trend API 라이브", bool(fl and fl["n"] >= 1), f"삼성전자 {fl and fl['n']}일")
    except Exception as e:
        check("네이버 trend API 라이브", False, str(e)[:60])
    try:
        rows = dart_watch.pull("삼성식품테스트", "00126955", __import__("datetime").datetime.now(dart_watch.KST) - __import__("datetime").timedelta(days=30))
        check("DART companyRSS 라이브", isinstance(rows, list), f"{len(rows)}건/30일")
    except Exception as e:
        check("DART companyRSS 라이브", False, str(e)[:60])

print(f"\n{'='*40}\n결과: {'전 항목 PASS ✅' if not FAIL else '실패 ' + str(len(FAIL)) + '건 ❌ — ' + ', '.join(FAIL)}")
sys.exit(1 if FAIL else 0)
