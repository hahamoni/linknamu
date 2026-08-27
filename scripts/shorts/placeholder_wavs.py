# -*- coding: utf-8 -*-
"""나레이션 자리표시용 무음 wav 생성 — TTS 없이 편집 스펙을 검증하기 위한 드라이런.

사용: python3 scripts/shorts/placeholder_wavs.py docs/shorts/ep-p02-beats.json --lang ko

음절 수(한) 또는 단어 수(영)에서 실측 발화속도로 길이를 추정해 무음 wav를 만든다.
실측 기준(P01 v3): 한국어 5.5음절/초, 영어 2.6단어/초, 비트당 앞뒤 여백 0.35초.
이 wav로 assemble.py를 돌리면 비주얼 흐름·자막 타이밍을 미리 볼 수 있고,
쿼터가 회복되면 같은 파일명으로 진짜 나레이션을 덮어쓰면 그대로 최종본이 된다.
"""
import json, re, sys, wave
from pathlib import Path

KO_RATE, EN_RATE, PAD = 5.5, 2.6, 0.35
RATE = 24000

_D = "영일이삼사오육칠팔구"


def syl(s):
    return sum(1 for ch in s if "가" <= ch <= "힣")


def words(s):
    return len(re.findall(r"[A-Za-z0-9\-']+", s))


def main():
    args = sys.argv[1:]
    ep_path = Path(args[0])
    lang = args[args.index("--lang") + 1] if "--lang" in args else "ko"
    ep = json.loads(ep_path.read_text())
    out = ep_path.parent / (ep_path.stem.replace("-beats", "") + "_output")
    out.mkdir(exist_ok=True)
    total = 0.0
    for i, b in enumerate(ep["beats"], 1):
        n = syl(b["ko"]) if lang == "ko" else words(b["en"])
        dur = n / (KO_RATE if lang == "ko" else EN_RATE) + PAD
        frames = int(dur * RATE)
        p = out / f"beat{i:02d}_{lang}.wav"
        with wave.open(str(p), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
            w.writeframes(b"\x00\x00" * frames)
        total += frames / RATE
        print(f"  {i:02d} {dur:5.2f}s  ({n}{'음절' if lang=='ko' else '단어'})")
    print(f"자리표시 {len(ep['beats'])}개 · 총 {total:.1f}s → {out}/")
    print("주의: 무음입니다. TTS 쿼터 회복 후 같은 경로에 진짜 나레이션을 덮어쓰세요.")


if __name__ == "__main__":
    main()
