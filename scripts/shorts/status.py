# -*- coding: utf-8 -*-
"""편별 진행 상황을 한 화면에 — 지금 어디까지 왔는지 확인용.

    python3 scripts/shorts/status.py
    python3 scripts/shorts/status.py --lang en
"""
import json
import signal
import sys
import wave
from pathlib import Path

# `| head` 로 잘라 볼 때 BrokenPipeError 역추적이 뜨지 않게 한다.
try:
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
except (AttributeError, ValueError):
    pass

DOCS = Path(__file__).resolve().parents[2] / "docs" / "shorts"


def is_placeholder(p):
    if not p.exists():
        return True
    try:
        with wave.open(str(p)) as w:
            pcm = w.readframes(min(w.getnframes(), w.getframerate()))
        return all(b == 0 for b in pcm[:4000])
    except Exception:
        return True


def main():
    lang = sys.argv[sys.argv.index("--lang") + 1] if "--lang" in sys.argv else "ko"
    eps = sorted(p.stem[3:-6] for p in DOCS.glob("ep-*-beats.json"))
    done = total = 0
    print(f"\n  편   나레이션({lang})        완성본")
    print("  " + "─" * 46)
    for ep in eps:
        n = len(json.loads((DOCS / f"ep-{ep}-beats.json").read_text())["beats"])
        out = DOCS / f"ep-{ep}_output"
        real = sum(0 if is_placeholder(out / f"beat{i:02d}_{lang}.wav") else 1
                   for i in range(1, n + 1))
        final = out / f"ep-{ep}_{lang}.mp4"
        bar = "█" * round(real / n * 14) + "·" * (14 - round(real / n * 14))
        mark = "✓ 완성" if final.exists() else ("· 조립 대기" if real == n else "")
        print(f"  {ep.upper()}  {bar} {real:>2}/{n}   {mark}")
        total += n
        done += real
    print("  " + "─" * 46)
    pct = done / total * 100 if total else 0
    print(f"  전체 {done}/{total} 비트 ({pct:.0f}%)\n")
    if done < total:
        print("  쿼터가 열려 있으면:  bash scripts/shorts/run_daily.sh\n")


if __name__ == "__main__":
    main()
