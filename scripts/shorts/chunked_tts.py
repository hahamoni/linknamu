# -*- coding: utf-8 -*-
"""묶음 TTS + 무음 분할 — 무료 티어 일일 쿼터 대응 (비트별 28호출 → 언어당 4호출).

사용:
  python3 scripts/shorts/chunked_tts.py docs/shorts/ep-p01-beats.json --lang ko --model gemini-2.5-flash-preview-tts
  python3 scripts/shorts/chunked_tts.py ... --chunks 2,3   # 특정 청크만 재생성

여러 비트를 한 요청으로 합성하고(문장 사이 1초 침묵 지시), 내부 무음의 최장 구간에서
분할해 beatNN_<lang>.wav 로 저장한다. 분할 경계가 비트 수보다 적으면 해당 청크는
건너뛰고 종료코드 2 — generate.py --beats N --lang <lang> --resume 으로 비트별 폴백.
표준 라이브러리만 사용.
"""
import json, struct, sys, time, wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generate import load_key, tts, save_wav, syl

CHUNK = 4          # 청크당 비트 수
MIN_GAP_MS = 300   # 분할 후보로 인정하는 내부 무음 최소 길이
PAD_MS = 120       # 분할 후 각 세그먼트 앞뒤에 남길 무음
RMS_THR = 300      # 20ms 창 RMS 무음 판정 임계값

STYLE = {
    "ko": ("차분하고 낮은 다큐멘터리 나레이션 톤으로, 늘어지지 않는 적당한 템포로 "
           "또렷하게 읽어주세요. 각 문장이 끝나면 1초간 조용히 쉬었다가 다음 문장을 읽어주세요.\n\n"),
    "en": ("Read in a calm, low documentary narration tone at a steady, unhurried but "
           "not slow pace. After each sentence, stay silent for one second before the next.\n\n"),
}


def silence_runs(samples, rate):
    """20ms 창 RMS 기준 (무음 여부, 시작 샘플, 길이 샘플) 런 목록."""
    win = rate // 50
    flags = []
    for i in range(0, len(samples) - win, win):
        rms = (sum(s * s for s in samples[i:i + win]) / win) ** 0.5
        flags.append((i, rms < RMS_THR))
    runs, start, cur = [], 0, None
    for i, silent in flags:
        if silent != cur:
            if cur is not None:
                runs.append((cur, start, i - start))
            cur, start = silent, i
    runs.append((cur, start, len(samples) - start))
    return runs, win


def split_chunk(pcm, rate, n):
    """n개 세그먼트로 분할. 성공 시 [pcm...], 실패 시 None."""
    samples = struct.unpack(f"<{len(pcm)//2}h", pcm)
    runs, win = silence_runs(samples, rate)
    voiced = [r for r in runs if not r[0]]
    if not voiced:
        return None
    lo, hi = voiced[0][1], voiced[-1][1] + voiced[-1][2]
    inner = [r for r in runs if r[0] and r[1] > lo and r[1] + r[2] < hi
             and r[2] >= rate * MIN_GAP_MS // 1000]
    if len(inner) < n - 1:
        return None
    cuts = sorted(sorted(inner, key=lambda r: -r[2])[:n - 1], key=lambda r: r[1])
    bounds = [0] + [r[1] + r[2] // 2 for r in cuts] + [len(samples)]
    pad = rate * PAD_MS // 1000
    out = []
    for a, b in zip(bounds, bounds[1:]):
        seg = samples[a:b]
        sruns, _ = silence_runs(seg, rate)
        sv = [r for r in sruns if not r[0]]
        if not sv:
            return None
        s = max(0, sv[0][1] - pad)
        e = min(len(seg), sv[-1][1] + sv[-1][2] + pad)
        out.append(struct.pack(f"<{e-s}h", *seg[s:e]))
    return out


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    ep_path = Path(args[0])
    ep = json.loads(ep_path.read_text())
    lang = args[args.index("--lang") + 1]
    model = args[args.index("--model") + 1]
    only = None
    if "--chunks" in args:
        only = {int(x) for x in args[args.index("--chunks") + 1].split(",")}
    out = ep_path.parent / (ep_path.stem.replace("-beats", "") + "_output")
    out.mkdir(exist_ok=True)
    key = load_key()
    voice = "Charon"

    beats = ep["beats"]
    chunks = [beats[i:i + CHUNK] for i in range(0, len(beats), CHUNK)]
    failed = []
    for ci, chunk in enumerate(chunks, 1):
        if only and ci not in only:
            continue
        base = (ci - 1) * CHUNK
        text = STYLE[lang] + "\n\n".join(b[lang] for b in chunk)
        print(f"· 청크 {ci} (비트 {base+1}–{base+len(chunk)}) 합성 중…")
        pcm, rate = tts(key, model, voice, text)
        segs = split_chunk(pcm, rate, len(chunk))
        if segs is None:
            print(f"  ✗ 분할 실패 — 경계 부족. 비트별 폴백 필요: --beats "
                  + ",".join(str(base + j + 1) for j in range(len(chunk))))
            failed.append(ci)
            continue
        for j, seg in enumerate(segs):
            i = base + j + 1
            dur = save_wav(out / f"beat{i:02d}_{lang}.wav", seg, rate)
            note = ""
            if lang == "ko":
                s = syl(chunk[j][lang])
                note = f"  {s/dur:.1f}음절/s" if dur else ""
            print(f"  {lang} {i:02d}  {dur:5.2f}s{note}")
        time.sleep(2)
    if failed:
        sys.exit(2)


if __name__ == "__main__":
    main()
