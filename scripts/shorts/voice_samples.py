# -*- coding: utf-8 -*-
"""목소리 고르기용 샘플 생성 — 같은 문장을 여러 목소리로 읽어 한 파일에 잇는다.

편을 고르기 전에 화자를 먼저 정하기 위한 도구다. 목소리를 바꾸면 이미 만든
나레이션을 전부 다시 뽑아야 하므로, 대량 생성 **전에** 이걸로 정하는 게 싸다.

사용:
  python3 scripts/shorts/voice_samples.py
  python3 scripts/shorts/voice_samples.py --voices Charon,Kore,Orus --model gemini-2.5-flash-preview-tts

산출: docs/shorts/_voice_samples/<이름>.wav 와, 이름을 사이사이 끼워 이어 붙인
      compare_<lang>.wav (한 번에 쭉 들으며 고르라고).
"""
import sys
import time
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from chunked_tts import STYLE
from generate import load_key, save_wav, tts

OUT = Path(__file__).resolve().parents[2] / "docs" / "shorts" / "_voice_samples"

# 다큐 나레이션에 쓸 만한 결이 다른 것들로 골랐다. 전체 30종은 Gemini 문서 참조.
DEFAULT = ["Charon", "Kore", "Orus", "Rasalgethi", "Gacrux", "Algieba"]

# 쿼터가 닫혀 있으면 열릴 때까지 버틴다(무료 티어 리셋 07:00 UTC).
# 밤에 걸어두고 자도 아침에 샘플이 나와 있게 하려는 것.
WAIT_TRIES = 40
WAIT_SECS = 600

# 실제 대본에서 가져온 문장 — 훅 하나, 설명 하나, 반전 하나.
LINES = {
    "ko": ("그네 타는 법, 특허가 될 수 있을까요? "
           "특허청은 이 서류를 통과시켰습니다. "
           "그 서류를 써준 변리사는 아버지였습니다."),
    "en": ("Can a way of swinging on a swing be patented? "
           "The patent office let it through. "
           "The attorney who wrote that filing was his father."),
}


def main():
    a = sys.argv[1:]
    lang = a[a.index("--lang") + 1] if "--lang" in a else "ko"
    model = a[a.index("--model") + 1] if "--model" in a else "gemini-2.5-flash-preview-tts"
    voices = (a[a.index("--voices") + 1].split(",") if "--voices" in a else DEFAULT)
    OUT.mkdir(parents=True, exist_ok=True)

    key = load_key()
    text = STYLE[lang] + LINES[lang]
    made = []
    for v in voices:
        dst = OUT / f"{v}_{lang}.wav"
        if dst.exists():
            print(f"· {v} 이미 있음 — 건너뜀")
            made.append((v, dst))
            continue
        print(f"· {v} 합성 중…", flush=True)
        pcm = rate = None
        for attempt in range(1, WAIT_TRIES + 1):
            try:
                pcm, rate = tts(key, model, v, text)
                break
            except Exception as e:
                msg = str(e)
                if "429" not in msg or attempt == WAIT_TRIES:
                    print(f"  ✗ {v}: {msg[:120]}")
                    break
                # 쿼터가 닫혀 있으면 열릴 때까지 기다린다 — 무료 티어는 07:00 UTC 리셋.
                print(f"  · 쿼터 대기 {attempt}/{WAIT_TRIES} "
                      f"({WAIT_SECS // 60}분 후 재시도)", flush=True)
                time.sleep(WAIT_SECS)
        if pcm is None:
            continue
        save_wav(dst, pcm, rate)
        made.append((v, dst))
        print(f"  ✓ {dst.name}", flush=True)
        time.sleep(20)          # 무료 티어 분당 제한 완화

    if len(made) < 2:
        print("\n비교 파일을 만들 만큼 모이지 않았습니다.")
        return

    # 사이에 0.7초 침묵을 두고 이어 붙인다.
    with wave.open(str(made[0][1])) as w:
        params = w.getparams()
    gap = b"\x00" * (params.framerate * params.sampwidth * params.nchannels * 7 // 10)
    comp = OUT / f"compare_{lang}.wav"
    with wave.open(str(comp), "wb") as o:
        o.setparams(params)
        for v, p in made:
            with wave.open(str(p)) as w:
                o.writeframes(w.readframes(w.getnframes()))
            o.writeframes(gap)
    print(f"\n✓ {comp}")
    print("  순서: " + " → ".join(v for v, _ in made))


if __name__ == "__main__":
    main()
