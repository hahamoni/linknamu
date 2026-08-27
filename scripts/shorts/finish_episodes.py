# -*- coding: utf-8 -*-
"""쿼터가 열리면 알아서 끝까지 간다 — 나레이션 → 무음 압축 → 조립까지 무인 실행.

`patient_tts.py`는 나레이션만 채운다. 이 스크립트는 그 위에서 한 편이 다 채워질 때마다
바로 완성본을 뽑는다. 사람이 07:00 UTC(리셋)에 깨어 있을 필요가 없게 하는 것이 목적이다.

한 편의 완료 조건: 모든 비트의 `beatNN_<lang>.wav` 가 자리표시(무음)가 아닐 것.
완료된 편은 `--edit`/`--music` 이 있으면 그걸 써서 조립하고, 결과를 `_output` 에 남긴다.
이미 완성본이 있고 나레이션이 그보다 오래됐으면 건너뛴다(재조립 낭비 방지).

사용:
  python3 scripts/shorts/finish_episodes.py --lang ko --font <Pretendard-Bold.ttf> --minutes 600
  python3 scripts/shorts/finish_episodes.py --lang ko --font <ttf> --once     # 한 바퀴만

인자:
  --lang     ko | en (기본 ko)
  --font     자막 폰트 ttf (없으면 assemble.py 기본값)
  --eps      대상 편 코드 목록 (기본: docs/shorts 의 ep-*-beats.json 전부)
  --minutes  총 실행 시간 상한 (기본 600)
  --once     한 바퀴만 돌고 끝낸다
  --interval 바퀴 사이 대기 초 (기본 300)
"""
import json
import subprocess
import sys
import time
import wave
from pathlib import Path

DOCS = Path("docs/shorts")


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


def episode_codes():
    return sorted(p.stem[3:-6] for p in DOCS.glob("ep-*-beats.json"))


def narration_ready(ep, lang):
    """모든 비트가 진짜 나레이션이면 (True, 가장 늦은 mtime)."""
    beats_path = DOCS / f"ep-{ep}-beats.json"
    n = len(json.loads(beats_path.read_text())["beats"])
    out = DOCS / f"ep-{ep}_output"
    newest = 0.0
    for i in range(1, n + 1):
        w = out / f"beat{i:02d}_{lang}.wav"
        if is_placeholder(w):
            return False, 0.0
        newest = max(newest, w.stat().st_mtime)
    return True, newest


def assemble(ep, lang, font):
    """조립. 편집 스펙·음악이 있으면 함께 넘긴다. 성공 시 산출 경로."""
    out = DOCS / f"ep-{ep}_output"
    cmd = [sys.executable, "scripts/shorts/assemble.py", str(DOCS / f"ep-{ep}-beats.json"),
           "--lang", lang]
    edit = DOCS / f"ep-{ep}-edit.json"
    if edit.exists():
        cmd += ["--edit", str(edit)]
    music = out / "music_bed.mp3"
    if music.exists():
        cmd += ["--music", str(music)]
    if font:
        cmd += ["--font", font]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return None, (r.stdout + r.stderr)[-400:]
    final = out / f"ep-{ep}_{lang}.mp4"
    return (final if final.exists() else None), ""


def one_pass(eps, lang, font, done):
    """완료된 편을 조립한다. 이번 바퀴에 새로 만든 편 수를 돌려준다."""
    made = 0
    for ep in eps:
        if not (DOCS / f"ep-{ep}-beats.json").exists():
            continue
        ready, newest = narration_ready(ep, lang)
        if not ready:
            continue
        final = DOCS / f"ep-{ep}_output" / f"ep-{ep}_{lang}.mp4"
        if final.exists() and final.stat().st_mtime >= newest and done.get(ep) != "재조립":
            continue                       # 이미 최신 — 다시 만들지 않는다
        print(f"[{time.strftime('%H:%M:%S')}] {ep} 나레이션 완료 → 조립", flush=True)
        subprocess.run([sys.executable, "scripts/shorts/compress_silence.py"]
                       + [str(p) for p in sorted((DOCS / f"ep-{ep}_output").glob(f"beat*_{lang}.wav"))],
                       capture_output=True)
        path, err = assemble(ep, lang, font)
        if path:
            print(f"  ✓ {path}", flush=True)
            done[ep] = "완료"
            made += 1
        else:
            print(f"  ✗ 조립 실패: {err}", flush=True)
            done[ep] = "실패"
    return made


def main():
    a = sys.argv[1:]
    lang = a[a.index("--lang") + 1] if "--lang" in a else "ko"
    font = a[a.index("--font") + 1] if "--font" in a else ""
    limit = int(a[a.index("--minutes") + 1]) if "--minutes" in a else 600
    interval = int(a[a.index("--interval") + 1]) if "--interval" in a else 300
    if "--eps" in a:
        eps = []
        for x in a[a.index("--eps") + 1:]:
            if x.startswith("--"):
                break
            eps.append(x)
    else:
        eps = episode_codes()

    print(f"대상 {len(eps)}편: {' '.join(eps)} · 언어 {lang}", flush=True)
    done, deadline = {}, time.time() + limit * 60
    total = 0
    while True:
        total += one_pass(eps, lang, font, done)
        if "--once" in a or time.time() >= deadline:
            break
        # 남은 편이 없으면 조기 종료
        if all(narration_ready(e, lang)[0] for e in eps
               if (DOCS / f"ep-{e}-beats.json").exists()):
            print("모든 편 완료", flush=True)
            break
        time.sleep(interval)
    print(f"완성본 {total}편 생성", flush=True)


if __name__ == "__main__":
    main()
