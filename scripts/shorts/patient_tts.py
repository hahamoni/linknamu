# -*- coding: utf-8 -*-
"""인내형 나레이션 생성기 — 쿼터가 풀릴 때마다 조금씩 채운다.

무료 티어 TTS는 일일 한도에 걸린 뒤에도 시간이 지나면 소량씩 다시 열린다.
이 스크립트는 자리표시(무음) 상태인 청크만 골라 재시도하고, 429가 나오면 길게 쉬었다가
다시 시도한다. 성공한 비트는 즉시 파일로 남으므로 중간에 죽어도 진행분이 보존된다.

사용:
  python3 scripts/shorts/patient_tts.py p02 p06 p05 --lang ko --minutes 240
  python3 scripts/shorts/patient_tts.py p01:en:1,2 p02 --lang ko --minutes 240

인자: 편 대상들 / --lang(기본 언어) / --minutes(총 실행 시간 상한)

편 대상은 두 가지 형태다.
  p02          자리표시(무음) 청크를 자동으로 찾아 채운다.
  p01:en:1,2   p01 영어의 1·2청크를 자리표시 여부와 관계없이 다시 만든다.
               대본을 고쳤는데 파일엔 예전 음성이 멀쩡히 들어 있어 자동 탐지가
               못 잡는 경우를 위한 것. 성공하면 그 청크는 다시 시도하지 않는다.
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


def parse_target(tok, default_lang):
    """편 인자를 (코드, 언어, 지정청크|None) 로 푼다.

    'p02'          → 자리표시 청크를 자동 탐지 (기본)
    'p01:en:1,2'   → p01 영어의 1·2청크를 자리표시 여부와 무관하게 다시 만든다.
                     대본이 바뀌었는데 파일엔 예전 음성이 멀쩡히 들어 있는 경우
                     (무음이 아니라서 자동 탐지가 못 잡는다) 를 위한 것.
    """
    parts = tok.split(":")
    code = parts[0]
    lang = parts[1] if len(parts) > 1 and parts[1] else default_lang
    forced = [int(x) for x in parts[2].split(",")] if len(parts) > 2 and parts[2] else None
    return code, lang, forced


def main():
    args = sys.argv[1:]
    default_lang = args[args.index("--lang") + 1] if "--lang" in args else "ko"
    limit_min = int(args[args.index("--minutes") + 1]) if "--minutes" in args else 180
    skip = {default_lang, str(limit_min)}
    targets = [parse_target(a, default_lang) for a in args
               if not a.startswith("--") and a not in skip]
    deadline = time.time() + limit_min * 60
    forced_done = set()
    mi = 0

    while time.time() < deadline:
        did_work = False
        for ep, lang, forced in targets:
            ep_path = Path(f"docs/shorts/ep-{ep}-beats.json")
            if not ep_path.exists():
                continue
            n_beats = len(json.loads(ep_path.read_text())["beats"])
            out_dir = ep_path.parent / f"ep-{ep}_output"
            if forced:
                todo = [c for c in forced if (ep, lang, c) not in forced_done]
            else:
                todo = pending_chunks(ep_path, out_dir, lang, n_beats)
            if not todo:
                continue
            c = todo[0]
            model = MODELS[mi % len(MODELS)]
            tag = f"{ep}/{lang}" + ("(지정)" if forced else "")
            print(f"[{time.strftime('%H:%M:%S')}] {tag} 청크 {c} ({model}) 남은청크 {len(todo)}", flush=True)
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
                if forced:
                    forced_done.add((ep, lang, c))   # 지정 청크는 한 번만 다시 만든다
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
