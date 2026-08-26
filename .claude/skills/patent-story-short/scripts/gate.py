# -*- coding: utf-8 -*-
"""비트 대본 게이트 — 20편 실측 분석(docs/shorts/winning-pattern-analysis.md)에서 역산한 기준.

사용:  python3 gate.py episode.json
episode.json 형식:
{
  "title": "...",
  "cover_ko": "...", "cover_en": "...",
  "beats": [
    {"ko": "...", "en": "...", "visual": "인물|클립|문서|그래픽"},
    ...
  ]
}
"""
import re, sys, json

# ── 기존 시리즈 게이트에서 계승 (faceless-mystery-short) ─────────────────
BAN = ["소름","충격","미스터리한","섬뜩","기묘한","기이한","놀랍게도","무서운","공포","경악","믿기 힘든","전율"]
BAN_END = ["구독","좋아요","팔로우","채널"]   # 45K 헤디 편의 엔딩 — 승자는 안 한다

KO_RATE, EN_RATE = 5.5, 2.8   # 음절/초, 단어/초

# 실측 역산 기준
BEATS = (12, 16)              # 승자 씬 수 13~20을 40초 내로 환산
KO_BEAT = (6, 21)             # 비트당 1.1~3.8초  (승자 씬 1.7~3.5초 + 여유)
KO_TOTAL = (165, 250)         # 총 30~45초
EN_BEAT = (4, 11)
EN_TOTAL = (84, 126)
DOC_POS = (0.55, 0.80)        # 문서 비트 위치 — 실측 66~75% 지점
DOC_KO_MAX = 19               # 문서 비트 ≤ 3.5초
PERSON_MIN = 0.5              # 인물 비주얼 비중 ≥ 50%

_D = "영일이삼사오육칠팔구"
def _read4(n):
    out = ""
    for val, unit in ((1000,"천"),(100,"백"),(10,"십")):
        d, n = divmod(n, val)
        if d: out += ("" if d == 1 else _D[d]) + unit
    if n: out += _D[n]
    return out

def num2ko(tok):
    if "." in tok:
        a, b = tok.split(".", 1)
        return num2ko(a) + "점" + "".join(_D[int(c)] for c in b)
    n = int(tok.replace(",", ""))
    if n == 0: return "영"
    out = ""
    for val, unit in ((10**8,"억"),(10**4,"만")):
        d, n = divmod(n, val)
        if d: out += ("" if d == 1 else _read4(d)) + unit
    if n: out += _read4(n)
    return out

def spoken_syl(s):
    t = re.sub(r"\d[\d,]*(?:\.\d+)?", lambda m: num2ko(m.group()), s)
    return sum(1 for ch in t if '가' <= ch <= '힣')

def toks(s): return len(re.findall(r"[A-Za-z0-9\-']+", s))

NATIVE_UNIT = ["시","개","명","살","마리","권","자루","병","그루","척","채",
               "벌","켤레","군데","가지","줄","판","기","자","대","통"]
_COMPOUND = "간|월|대|절|각|기|리|반|속|계|장|점|당"
_NATIVE_RE = re.compile(r"(\d[\d,]*)\s*(" + "|".join(NATIVE_UNIT) + r")(?!" + _COMPOUND + r")")
_COMMA_RE = re.compile(r"\d{1,3}(?:,\d{3})+")

def number_risks(s):
    out = []
    for m in _COMMA_RE.finditer(s):
        out.append((m.group(), "쉼표에서 끊어 읽음 — 한글로 풀어 쓸 것"))
    for m in _NATIVE_RE.finditer(s):
        n = int(m.group(1).replace(",", ""))
        if n < 100:
            out.append((m.group(), f"고유어 단위 '{m.group(2)}' — {n}은 고유어로 읽어야 한다. 한글로 쓸 것"))
    return out

# ── 새 검사 — 실측 법칙 ──────────────────────────────────────────────────
_NEG = re.compile(r"(아니|않|없|지만|그러나|아닌)")

def hook_ok(ko):
    """법칙 3: 질문형이거나, 한 문장에 통념+반박(부정어)이 함께 있어야 한다."""
    return ("?" in ko) or bool(_NEG.search(ko))

def check(ep):
    fails, warns = [], []
    beats = ep["beats"]
    n = len(beats)
    print("=" * 74)
    print(f"■ {ep.get('title','(무제)')}  — 비트 {n}개")

    c = ep.get("cover_ko", "")
    print(f"  커버(한) {c!r} {len(c)}자  {'OK' if 10 <= len(c) <= 16 else '⚠︎ FAIL(10~16자)'}")
    if not (10 <= len(c) <= 16): fails.append("커버 길이")
    if ep.get("cover_en"): print(f"  커버(영) {ep['cover_en']!r}")

    if not (BEATS[0] <= n <= BEATS[1]):
        fails.append(f"비트 수 {n} (기준 {BEATS[0]}~{BEATS[1]})")

    # 법칙 2·3: 1비트 = 인물 + 훅 문형
    if beats and beats[0].get("visual") != "인물":
        fails.append(f"1비트 비주얼이 '{beats[0].get('visual')}' — 첫 3초는 인물이어야 한다 (법칙 2)")
    if beats and not hook_ok(beats[0]["ko"]):
        fails.append("1비트가 질문도 통념+반박도 아니다 (법칙 3)")

    # 법칙 4: 문서 비트
    doc_idx = [i for i, b in enumerate(beats) if b.get("visual") == "문서"]
    if len(doc_idx) == 0:
        warns.append("문서 비트 0개 — 증거 비트 하나를 넣는 것이 승자 패턴 (법칙 4)")
    elif len(doc_idx) > 1:
        fails.append(f"문서 비트 {len(doc_idx)}개 — 정확히 1개 (법칙 4)")
    else:
        pos = doc_idx[0] / max(n - 1, 1)
        if not (DOC_POS[0] <= pos <= DOC_POS[1]):
            warns.append(f"문서 비트 위치 {pos:.0%} — 60~75% 지점이 실측 패턴 (법칙 4)")
        dsyl = spoken_syl(beats[doc_idx[0]]["ko"])
        if dsyl > DOC_KO_MAX:
            fails.append(f"문서 비트 {dsyl}음절 — 문서는 화면에 3초대까지만 (법칙 4)")

    # 법칙 2: 인물 비중
    person = sum(1 for b in beats if b.get("visual") == "인물")
    if n and person / n < PERSON_MIN:
        fails.append(f"인물 비주얼 {person}/{n} ({person/n:.0%}) — 50% 이상 (법칙 2)")

    # 법칙 5: 엔딩
    last = beats[-1]["ko"] if beats else ""
    if any(b in last for b in BAN_END):
        fails.append("마지막 비트에 구독·좋아요·채널 — 금지 (법칙 5)")
    has_payoff = bool(re.search(r"\d", last)) or any(q in last for q in ("「", "”", "\"", "'", "?")) \
                 or bool(re.search(r"[영일이삼사오육칠팔구십백천만억]", last))
    if not has_payoff:
        warns.append("마지막 비트에 숫자·인용·질문이 없다 — 페이오프 착지 확인 (법칙 5)")

    # 길이·숫자·금지어 (비트별)
    tot_ko = tot_en = 0
    for i, b in enumerate(beats, 1):
        ko, en = b["ko"], b.get("en", "")
        ks, es = spoken_syl(ko), toks(en)
        tot_ko += ks; tot_en += es
        marks = []
        if not (KO_BEAT[0] <= ks <= KO_BEAT[1]): marks.append(f"한 {ks}음절 이탈({KO_BEAT[0]}~{KO_BEAT[1]})")
        if en and not (EN_BEAT[0] <= es <= EN_BEAT[1]): marks.append(f"영 {es}단어 이탈({EN_BEAT[0]}~{EN_BEAT[1]})")
        ban = [w for w in BAN if w in ko]
        if ban: marks.append(f"금지어{ban}")
        for _t, _w in number_risks(ko):
            marks.append(f"숫자 {_t!r}: {_w}")
        flag = "⚠︎ " if marks else "OK "
        if marks and any("이탈" in m or "금지어" in m or "숫자" in m for m in marks):
            fails.extend(f"{i}비트: {m}" for m in marks)
        print(f"   {flag}{i:2d} [{b.get('visual','?'):2s}] 한 {ks:2d}음절({ks/KO_RATE:.1f}s)"
              + (f" · 영 {es:2d}단어({es/EN_RATE:.1f}s)" if en else "")
              + ("   " + " / ".join(marks) if marks else ""))

    ko_dur, en_dur = tot_ko / KO_RATE, tot_en / EN_RATE
    print(f"      합계 — 한 {tot_ko}음절 ≈ {ko_dur:.1f}s / 영 {tot_en}단어 ≈ {en_dur:.1f}s   (기준 30~45s)")
    if not (KO_TOTAL[0] <= tot_ko <= KO_TOTAL[1]):
        fails.append(f"한국어 총 {tot_ko}음절 (기준 {KO_TOTAL[0]}~{KO_TOTAL[1]})")
    if tot_en and not (EN_TOTAL[0] <= tot_en <= EN_TOTAL[1]):
        fails.append(f"영어 총 {tot_en}단어 (기준 {EN_TOTAL[0]}~{EN_TOTAL[1]})")

    print("-" * 74)
    for w in warns: print(f"  ⚠︎ 확인: {w}")
    for f in fails: print(f"  ✗ FAIL: {f}")
    print(f"  결과: {'통과 — 사람 체크리스트(§7)로' if not fails else f'불통과 {len(fails)}건 — 대본을 고친다. 생성은 그 다음.'}")
    return not fails

if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as f:
        ok = check(json.load(f))
    sys.exit(0 if ok else 1)
