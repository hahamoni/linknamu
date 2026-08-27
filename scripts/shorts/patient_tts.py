# -*- coding: utf-8 -*-
"""인내형 나레이션 생성기 — 쿼터가 풀릴 때마다 조금씩 채운다.

무료 티어 TTS는 일일 한도에 걸린 뒤에도 시간이 지나면 소량씩 다시 열린다.
이 스크립트는 자리표시(무음) 상태인 청크만 골라 재시도하고, 429가 나오면 길게 쉬었다가
다시 시도한다. 성공한 비트는 즉시 파일로 남으므로 중간에 죽어도 진행분이 보존된다.

사용:
  python3 scripts/shorts/patient_tts.py p02 p06 p05 --lang ko --minutes 240

인자: 편 코드들(ep-<코드>-beats.json 을 찾는다) / --lang / --minutes(총 실행 시간 상한)
"""
import json, subprocess, sys, time, wave
from pathlib import Path

MODELS = ["gemini-3.1-flash-tts-preview", "gemini-2.5-flash-preview-tts", "gemini-2.5-pro-preview-tts"]
CHUNK = 4
COOLDOWN = 420      # 429 후 대기 (초)
GAP = 30            # 성공 후 다음 호출까지


def is_placeholder(path):
    """무음(자리표시) 파일인지 — 앞 1초가 전부 0이면 자리표시."""
    if not path.exists():
        return True
    try:
        with wave.open(str(path)) as w:
            pcm = w.readframes(min(w.getnframes(), w.getframerate()))
        return all(b == 0 for b in pcm[:4000])
    except Exception:
        return True


def pending_chunks(ep_path, out_dir, lang, n_beats):
    todo = []
    for c in range(1, (n_beats + CHUNK - 1) // CHUNK + 1):
        beats = range((c - 1) * CHUNK + 1, min(c * CHUNK, n_beats) + 1)
        if any(is_placeholder(out_dir / f"beat{i:02d}_{lang}.wav") for i in beats):
            todo.append(c)
    return todo


def main():
    args = sys.argv[1:]
    lang = args[args.index("--lang") + 1] if "--lang" in args else "ko"
    limit_min = int(args[args.index("--minutes") + 1]) if "--minutes" in args else 180
    eps = [a for a in args if not a.startswith("--") and a not in (lang, str(limit_min))]
    deadline = time.time() + limit_min * 60
    mi = 0

    while time.time() < deadline:
        did_work = False
        for ep in eps:
            ep_path = Path(f"docs/shorts/ep-{ep}-beats.json")
            if not ep_path.exists():
                continue
            n_beats = len(json.loads(ep_path.read_text())["beats"])
            out_dir = ep_path.parent / f"ep-{ep}_output"
            todo = pending_chunks(ep_path, out_dir, lang, n_beats)
            if not todo:
                continue
            c = todo[0]
            model = MODELS[mi % len(MODELS)]
            print(f"[{time.strftime('%H:%M:%S')}] {ep} 청크 {c} ({model}) 남은청크 {len(todo)}", flush=True)
            r = subprocess.run([sys.executable, "scripts/shorts/chunked_tts.py", str(ep_path),
                                "--lang", lang, "--model", model, "--chunks", str(c)],
                               capture_output=True, text=True)
            out = r.stdout + r.stderr
            if "429" in out:
                print(f"  429 — {model} 대기", flush=True)
                mi += 1                       # 다음엔 다른 모델
                time.sleep(COOLDOWN if mi % len(MODELS) == 0 else 20)
            elif r.returncode == 0:
                print("  ✓ " + " / ".join(l.strip() for l in out.splitlines() if l.strip().startswith(lang)), flush=True)
                subprocess.run([sys.executable, "scripts/shorts/compress_silence.py"]
                               + [str(p) for p in sorted(out_dir.glob(f"beat*_{lang}.wav"))],
                               capture_output=True)
                did_work = True
                time.sleep(GAP)
            else:
                print("  ✗ 기타 오류:", out[-200:], flush=True)
                time.sleep(60)
            break                              # 한 번에 한 청크만, 다시 우선순위 계산
        else:
            print("모든 편 완료", flush=True)
            return
        if not did_work:
            continue
    print("시간 상한 도달", flush=True)


if __name__ == "__main__":
    main()
