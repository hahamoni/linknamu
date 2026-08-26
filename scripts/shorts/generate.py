# -*- coding: utf-8 -*-
"""쇼츠 나레이션·스틸 생성 파이프라인 (Gemini API).

사용:
  export GEMINI_API_KEY=...   # 또는 .env.local 에 GEMINI_API_KEY=... 한 줄
  python3 scripts/shorts/generate.py docs/shorts/ep-p01-beats.json          # 나레이션 한·영 전체
  python3 scripts/shorts/generate.py docs/shorts/ep-p01-beats.json --stills # 아카이브 스틸 다운로드만
  python3 scripts/shorts/generate.py docs/shorts/ep-p01-beats.json --lang ko --beats 3,10  # 부분 재생성

산출: <episode>_output/ 아래 beatNN_ko.wav / beatNN_en.wav / stills/
검수(§5)를 자동 수행: 비트당 길이 출력, 한국어 발화속도 4.5음절/초 미만이면 RETRY 표시.
표준 라이브러리만 사용 (의존성 없음).

환경변수 (선택):
  GEMINI_TTS_MODEL  기본: 자동 탐색 (모델 목록에서 'tts' 포함 첫 모델)
  GEMINI_TTS_VOICE  기본: Charon  (다큐 톤 저음. 후보: Kore, Puck, Fenrir, Aoede)
"""
import base64, json, os, re, struct, sys, time, urllib.request, urllib.error, wave
from pathlib import Path

API = "https://generativelanguage.googleapis.com/v1beta"

STILLS = {  # 파일명: Commons Special:FilePath (라이선스는 ep-p01 패키지 문서에서 확정)
    "01_heavenly_body_1944.jpg": "Hedy%20Lamarr%20in%20The%20Heavenly%20Body%201944.jpg",
    "02_screenland_1942.png": "Hedy%20Lamarr%20-%20Screenland%20(October%201942).png",
    "03_signature_1941.jpg": "Signature%20of%20Hedy%20Kiesler%20Markey%20(1941)%20(cropped).jpg",
    "09_kiesler_1933.jpg": "Hedy%20Kiesler%201933.jpg",
    "10_patent_page7.jpg": ("Patent%20Case%20File%20No.%202%2C292%2C387%2C%20Secret%20Communication%20System%2C"
                            "%20Inventors%20Hedy%20Kiesler%20Markey%20and%20George%20Antheil%20-%20DPLA%20-"
                            "%20128f022cfd9421aa10de72958a7edf90%20(page%207).jpg"),
    "11_samson_1949.png": "Hedi%20Lamarr%20in%20%22Samson%20and%20Delilah%22%20(1949)%20directed%20by%20Cecil%20B.%20DeMille.png",
}

def load_key():
    k = os.environ.get("GEMINI_API_KEY")
    if not k:
        for envfile in (".env.local", ".env"):
            p = Path(envfile)
            if p.exists():
                m = re.search(r"^GEMINI_API_KEY=(.+)$", p.read_text(), re.M)
                if m:
                    k = m.group(1).strip().strip('"')
                    break
    if not k:
        sys.exit("GEMINI_API_KEY가 없습니다. export 하거나 .env.local에 넣으세요 (커밋 금지).")
    return k

def http_json(url, payload=None, tries=6):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"Content-Type": "application/json"},
                                         data=json.dumps(payload).encode() if payload else None)
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:2000]
            if e.code in (429, 500, 503) and i < tries - 1:
                delay = 2 ** (i + 1)
                m = re.search(r'"retryDelay":\s*"(\d+)', body)  # 무료 티어 RPM 제한은 서버가 대기시간을 알려줌
                if m:
                    delay = max(delay, int(m.group(1)) + 2)
                time.sleep(delay); continue
            sys.exit(f"API 오류 {e.code}: {body[:300]}")
        except Exception as e:
            if i < tries - 1:
                time.sleep(2 ** (i + 1)); continue
            raise

def pick_tts_model(key):
    forced = os.environ.get("GEMINI_TTS_MODEL")
    if forced:
        return forced
    data = http_json(f"{API}/models?key={key}&pageSize=200")
    names = [m["name"].split("/")[-1] for m in data.get("models", [])]
    tts = [n for n in names if "tts" in n.lower()]
    pref = [n for n in tts if "flash" in n] + tts
    if not pref:
        sys.exit("TTS 모델을 찾지 못했습니다. GEMINI_TTS_MODEL로 지정하세요. 목록: " + ", ".join(names[:40]))
    print(f"· TTS 모델: {pref[0]}")
    return pref[0]

def tts(key, model, voice, text):
    payload = {
        "contents": [{"parts": [{"text": text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}},
        },
    }
    data = http_json(f"{API}/models/{model}:generateContent?key={key}", payload)
    part = data["candidates"][0]["content"]["parts"][0]["inlineData"]
    rate = 24000
    m = re.search(r"rate=(\d+)", part.get("mimeType", ""))
    if m:
        rate = int(m.group(1))
    return base64.b64decode(part["data"]), rate

def save_wav(path, pcm, rate):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
        w.writeframes(pcm)
    return len(pcm) / 2 / rate  # 초

def syl(s):  # 한글 음절 수 (대본은 숫자를 이미 풀어 씀)
    return sum(1 for ch in s if "가" <= ch <= "힣")

def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    ep_path = Path(args[0])
    ep = json.loads(ep_path.read_text())
    out = ep_path.parent / (ep_path.stem.replace("-beats", "") + "_output")
    out.mkdir(exist_ok=True)

    if "--stills" in args:
        sd = out / "stills"; sd.mkdir(exist_ok=True)
        for name, fp in STILLS.items():
            url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{fp}"
            print(f"↓ {name}")
            urllib.request.urlretrieve(url, sd / name)
        print(f"완료: {sd}"); return

    langs = ["ko", "en"]
    if "--lang" in args:
        langs = [args[args.index("--lang") + 1]]
    only = None
    if "--beats" in args:
        only = {int(x) for x in args[args.index("--beats") + 1].split(",")}

    key = load_key()
    model = pick_tts_model(key)
    voice = os.environ.get("GEMINI_TTS_VOICE", "Charon")
    print(f"· 보이스: {voice}  · 출력: {out}/")

    style = {"ko": "차분하고 낮은 다큐멘터리 나레이션 톤으로, 또박또박 읽어주세요: ",
             "en": "Read in a calm, low documentary narration tone: "}
    retry_list = []
    for lang in langs:
        for i, b in enumerate(ep["beats"], 1):
            if only and i not in only:
                continue
            if "--resume" in args and (out / f"beat{i:02d}_{lang}.wav").exists():
                continue
            text = b[lang]
            pcm, rate = tts(key, model, voice, style[lang] + text)
            dur = save_wav(out / f"beat{i:02d}_{lang}.wav", pcm, rate)
            note = ""
            if lang == "ko":
                s = syl(text)
                target = s / 5.5
                sps = s / dur if dur else 0
                if sps < 4.5:
                    note = "  ⚠ RETRY (4.5음절/초 미만 — 반복 의심, §5)"
                    retry_list.append(f"beat{i:02d}_ko")
                note = f"  목표 {target:4.1f}s · 발화 {sps:.1f}음절/s" + note
            print(f"  {lang} {i:02d}  {dur:5.2f}s{note}")
            time.sleep(0.4)
    print("\n검수: 각 wav를 대본과 눈으로 대조 (§5 한글 깨짐 — 깨진 단어는 재생성 아니라 교체).")
    if retry_list:
        print("재생성 대상: " + ", ".join(retry_list) + f"  →  --beats N --lang ko 로 부분 재실행")

if __name__ == "__main__":
    main()
