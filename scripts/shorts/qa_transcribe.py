# -*- coding: utf-8 -*-
"""나레이션 wav 검수 (§5): Gemini STT로 받아쓰고 대본과 대조 + 길이·발화속도.

사용:
  python3 scripts/shorts/qa_transcribe.py docs/shorts/ep-p01-beats.json --lang ko --beats 1,2,3,4 --model gemini-2.5-flash

출력: 비트당 JSON 한 줄
  {"beat":1,"lang":"ko","dur":4.1,"rate":4.4,"similarity":0.97,"verdict":"PASS","transcript":"…"}
verdict: FAIL(대조 불일치·반복 의심) / CHECK(경계·저속) / PASS.
표준 라이브러리만 사용. 무료 티어 RPM 고려해 호출 사이 7초 대기.
"""
import base64, difflib, json, re, sys, time, wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generate import API, http_json, load_key, syl

PROMPT = {
    "ko": "이 오디오의 발화를 한국어로 그대로 받아쓰세요. 설명이나 다른 말 없이 받아쓴 텍스트만 출력하세요.",
    "en": "Transcribe this audio verbatim in English. Output only the transcription, nothing else.",
}


def norm(s):
    return re.sub(r"[^0-9a-z가-힣]", "", s.lower())


def transcribe(key, model, wav_path, lang):
    b64 = base64.b64encode(wav_path.read_bytes()).decode()
    payload = {"contents": [{"parts": [
        {"text": PROMPT[lang]},
        {"inlineData": {"mimeType": "audio/wav", "data": b64}},
    ]}]}
    data = http_json(f"{API}/models/{model}:generateContent?key={key}", payload)
    parts = data["candidates"][0]["content"].get("parts", [])
    return " ".join(p.get("text", "") for p in parts).strip()


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    ep_path = Path(args[0])
    ep = json.loads(ep_path.read_text())
    lang = args[args.index("--lang") + 1]
    model = args[args.index("--model") + 1]
    beats = [int(x) for x in args[args.index("--beats") + 1].split(",")]
    out = ep_path.parent / (ep_path.stem.replace("-beats", "") + "_output")
    key = load_key()

    for bi in beats:
        script = ep["beats"][bi - 1][lang]
        p = out / f"beat{bi:02d}_{lang}.wav"
        if not p.exists():
            print(json.dumps({"beat": bi, "lang": lang, "verdict": "FAIL",
                              "error": "missing wav"}, ensure_ascii=False))
            continue
        with wave.open(str(p)) as w:
            dur = w.getnframes() / w.getframerate()
        t = transcribe(key, model, p, lang)
        ns, nt = norm(script), norm(t)
        sim = difflib.SequenceMatcher(None, ns, nt).ratio()
        # 반복 의심: 받아쓴 텍스트가 대본 앞부분을 두 번 이상 포함
        rep = len(ns) >= 8 and nt.count(ns[:8]) > 1
        rate = syl(script) / dur if lang == "ko" and dur else None
        if sim < 0.70 or rep:
            verdict = "FAIL"
        elif sim < 0.85 or (rate is not None and rate < 4.0):
            verdict = "CHECK"
        else:
            verdict = "PASS"
        row = {"beat": bi, "lang": lang, "dur": round(dur, 2),
               "similarity": round(sim, 3), "verdict": verdict, "transcript": t}
        if rate is not None:
            row["rate"] = round(rate, 2)
        if rep:
            row["repetition"] = True
        print(json.dumps(row, ensure_ascii=False), flush=True)
        time.sleep(7)


if __name__ == "__main__":
    main()
