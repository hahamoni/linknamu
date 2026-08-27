# -*- coding: utf-8 -*-
"""쇼츠 시각물 생성 (Gemini API) — 다이어그램(이미지) + 클립(Veo 3.1 lite).

사용:
  python3 scripts/shorts/generate_visuals.py docs/shorts/ep-p01-visuals.json --images
  python3 scripts/shorts/generate_visuals.py docs/shorts/ep-p01-visuals.json --clips [--only clipA_radio]

산출: <spec>-visuals.json과 같은 디렉토리의 ep-p01_output/ 아래 <name>.png / <name>.mp4
이미지 모델은 GEMINI_IMAGE_MODEL(기본 gemini-3.1-flash-image), 클립은 GEMINI_VIDEO_MODEL
(기본 veo-3.1-lite-generate-preview, 8초 720p 9:16). 표준 라이브러리만 사용.
"""
import base64, json, os, sys, time, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generate import API, http_json, load_key


def gen_image(key, model, prompt, out_path):
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
            "imageConfig": {"aspectRatio": "9:16"},
        },
    }
    data = http_json(f"{API}/models/{model}:generateContent?key={key}", payload)
    for part in data["candidates"][0]["content"].get("parts", []):
        blob = part.get("inlineData")
        if blob and blob.get("mimeType", "").startswith("image/"):
            out_path.write_bytes(base64.b64decode(blob["data"]))
            return True
    return False


def gen_clip(key, model, prompt, out_path):
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {"aspectRatio": "9:16", "durationSeconds": 8, "resolution": "720p"},
    }
    op = http_json(f"{API}/models/{model}:predictLongRunning?key={key}", payload)
    name = op["name"]
    print(f"  작업 {name} 폴링…")
    while True:
        time.sleep(15)
        op = http_json(f"{API}/{name}?key={key}")
        if op.get("done"):
            break
    if "error" in op:
        print("  ✗ 실패:", json.dumps(op["error"], ensure_ascii=False)[:300])
        return False
    resp = op.get("response", {})
    vids = (resp.get("generateVideoResponse", {}).get("generatedSamples")
            or resp.get("generatedVideos") or [])
    uri = None
    if vids:
        v = vids[0].get("video", vids[0])
        uri = v.get("uri") or v.get("videoUri")
    if not uri:
        print("  ✗ 응답에서 비디오 URI를 찾지 못함:", json.dumps(resp)[:300])
        return False
    req = urllib.request.Request(uri + ("&" if "?" in uri else "?") + f"key={key}")
    with urllib.request.urlopen(req, timeout=300) as r:
        out_path.write_bytes(r.read())
    return True


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    spec_path = Path(args[0])
    spec = json.loads(spec_path.read_text())
    out = spec_path.parent / (spec_path.stem.replace("-visuals", "") + "_output")
    out.mkdir(exist_ok=True)
    only = args[args.index("--only") + 1] if "--only" in args else None
    key = load_key()

    if "--images" in args:
        model = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image")
        for item in spec.get("images", []):
            if only and item["name"] != only:
                continue
            p = out / f"{item['name']}.png"
            print(f"· 이미지 {item['name']} ({model})")
            ok = gen_image(key, model, item["prompt"], p)
            print(f"  {'✓ ' + str(p) if ok else '✗ 이미지 파트 없음'}")

    if "--clips" in args:
        model = os.environ.get("GEMINI_VIDEO_MODEL", "veo-3.1-lite-generate-preview")
        for item in spec.get("clips", []):
            if only and item["name"] != only:
                continue
            p = out / f"{item['name']}.mp4"
            print(f"· 클립 {item['name']} ({model})")
            ok = gen_clip(key, model, item["prompt"], p)
            if ok:
                print(f"  ✓ {p} ({p.stat().st_size/1e6:.1f}MB)")


if __name__ == "__main__":
    main()
