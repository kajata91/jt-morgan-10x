#!/usr/bin/env python3
# JT Morgan 10X — 데이터 잠금 도구
# 로컬 원본 data.js(공개 저장소에 올리지 않음)를 AES-256-GCM으로 암호화해 data.enc.js 생성.
# 열쇠는 app/.tenver_key 파일(1줄, gitignore 됨). 대시보드는 비밀번호 입력 시에만 복호화된다.
import base64, json, os, secrets, sys
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 비공개 형제 저장소(~/Projects/tenver-core)가 있으면 원본·키를 거기서 읽는다. 없으면 구 구조(APP 안).
CORE = os.path.join(os.path.dirname(APP), "tenver-core")
SRC_DIR = os.path.join(CORE, "dashboard-src") if os.path.isdir(CORE) else APP
KEY_DIR = CORE if os.path.isdir(CORE) else APP
ITER = 300_000

def main():
    key_path = os.path.join(KEY_DIR, ".tenver_key")
    if not os.path.exists(key_path):
        print("ERROR: .tenver_key 파일이 없습니다 (비밀번호 1줄).", file=sys.stderr); sys.exit(1)
    passphrase = open(key_path, encoding="utf-8").read().strip()
    if len(passphrase) < 8:
        print("ERROR: 비밀번호는 8자 이상이어야 합니다.", file=sys.stderr); sys.exit(1)
    src = os.path.join(SRC_DIR, "data.js")
    plaintext = open(src, encoding="utf-8").read().encode("utf-8")
    # 헌터스(tenver-core/hunters) 정산 요약이 있으면 같은 암호문에 싣는다 → 대시보드 HUNTERS 탭
    hunters = os.path.join(SRC_DIR, "hunters.json")
    if os.path.exists(hunters):
        h = json.load(open(hunters, encoding="utf-8"))
        plaintext += ("\nwindow.HUNTERS_DATA = " + json.dumps(h, ensure_ascii=False) + ";\n").encode("utf-8")

    salt = secrets.token_bytes(16)
    iv = secrets.token_bytes(12)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER)
    key = kdf.derive(passphrase.encode("utf-8"))
    ct = AESGCM(key).encrypt(iv, plaintext, None)

    payload = {
        "v": 1, "iter": ITER,
        "salt": base64.b64encode(salt).decode(),
        "iv": base64.b64encode(iv).decode(),
        "ct": base64.b64encode(ct).decode(),
    }
    hint_path = os.path.join(KEY_DIR, ".tenver_hint")  # 선택: 비밀번호 힌트(평문 노출 — 비밀번호를 유추시키지 않는 문구만)
    if os.path.exists(hint_path):
        hint = open(hint_path, encoding="utf-8").read().strip()
        if hint:
            payload["hint"] = hint
    out = os.path.join(APP, "data.enc.js")
    with open(out, "w", encoding="utf-8") as f:
        f.write("// 자동 생성 — scripts/encrypt_data.py (원본 data.js는 로컬 전용)\n")
        f.write("const TENVER_DATA_ENC = " + json.dumps(payload) + ";\n")
    print(f"OK: data.js ({len(plaintext):,}B) -> data.enc.js (AES-256-GCM, PBKDF2 {ITER:,}회)", file=sys.stderr)

if __name__ == "__main__":
    main()
