# -*- coding: utf-8 -*-
"""내부 무음 압축 — TTS가 넣는 돌발 장침묵(0.9초 초과)을 0.6초로 줄인다.

사용: python3 scripts/shorts/compress_silence.py docs/shorts/ep-p01_output/beat*.wav
바뀐 파일만 '이전 → 이후' 길이를 출력하고 제자리 덮어쓰기. 앞뒤 무음은 건드리지 않는다.
"""
import struct, sys, wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from chunked_tts import silence_runs
from generate import save_wav

MAX_SIL = 0.9
KEEP = 0.6


def compress(path):
    with wave.open(str(path)) as w:
        rate = w.getframerate()
        pcm = w.readframes(w.getnframes())
    samples = struct.unpack(f"<{len(pcm)//2}h", pcm)
    runs, _ = silence_runs(samples, rate)
    voiced = [r for r in runs if not r[0]]
    if not voiced:
        return
    lo = voiced[0][1]
    hi = voiced[-1][1] + voiced[-1][2]
    keep = int(rate * KEEP)
    out, pos = [], 0
    for silent, start, length in runs:
        if silent and start > lo and start + length < hi and length > rate * MAX_SIL:
            out.append(samples[pos:start + keep])
            pos = start + length
    if not out:
        return
    out.append(samples[pos:])
    flat = [s for seg in out for s in seg]
    before = len(samples) / rate
    dur = save_wav(path, struct.pack(f"<{len(flat)}h", *flat), rate)
    print(f"{path.name}: {before:.2f}s → {dur:.2f}s")


for a in sys.argv[1:]:
    compress(Path(a))
