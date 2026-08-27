# -*- coding: utf-8 -*-
"""P01 편집 조립 — 나레이션 타임라인에 맞춰 비트별 비주얼을 잘라 붙인다.

사용:
  python3 scripts/shorts/assemble.py docs/shorts/ep-p01-beats.json --lang ko \
      --font <NotoSansKR-Bold.ttf 경로> [--no-subs] [--music <트랙.mp3>]

산출: ep-p01_output/ep-p01_<lang>_preview.mp4 (720x1280 24fps, 나레이션+클립 앰비언트 믹스)
음악 트랙을 주면 최종 믹스(ep-p01_<lang>.mp4), 없으면 프리뷰. 의존성: ffmpeg.
비주얼 매핑·자막 줄바꿈은 아래 EDIT/SUBS 스펙 (패키지 문서 비트 표 기준).

폰트: OFL Noto Sans KR —
  curl -sLo nkr.woff2 https://cdn.jsdelivr.net/fontsource/fonts/noto-sans-kr@latest/korean-700-normal.woff2
  pip install fonttools brotli && python3 -c "from fontTools.ttLib import TTFont; f=TTFont('nkr.woff2'); f.flavor=None; f.save('NotoSansKR-Bold.ttf')"
"""
import json, os, subprocess, sys, wave
from pathlib import Path

FF = os.environ.get("FFMPEG", "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2")
W, H, FPS = 720, 1280, 24
OW, OH = W * 2, H * 2  # 줌 여유용 오버스캔
GRADE = "eq=saturation=0.55:contrast=1.06,colorbalance=bs=0.06:bm=0.03:bh=-0.02"
GRAIN = "noise=alls=7:allf=t+u"
VIG = "vignette=PI/4.4"

# 비트별 비주얼: (종류, 소스, 옵션) — still(그레이드+줌) / card(서명 카드) / pad(블러 패드) /
# clip(구간 트림) / image(스타일 완성본, 그레이드 없음) / dissolve(초상→서명 카드)
# C안 v2 (ep-p01-scripts-v3.md) — 블루투스 역추적, 이름은 마지막 비트에 공개
EDIT = [
    ("still", "stills/01_heavenly_body_1944.jpg", {"focus": "top"}),
    ("image", "diagram_88ch.png", {}),
    ("clip", "clipA_radio.mp4", {"start": 0.0}),
    ("clip", "clipA_radio.mp4", {"start": 5.85}),
    ("image", "diagram_88ch.png", {"fast": True}),
    ("clip", "clipB_pianoroll.mp4", {"start": 0.0}),
    ("clip", "clipB_pianoroll.mp4", {"start": 5.2}),
    ("pad", "stills/09_kiesler_1933.jpg", {}),
    ("card", "stills/03_signature_1941.jpg", {}),
    ("still", "stills/02_screenland_1942.png", {}),
    ("pad", "stills/11_samson_1949.png", {}),
    ("still", "stills/12_lady_without_passport_1950.jpg", {"dark": True}),
    # 13~14 병합: 같은 초상 연속 컷 대신 한 컷을 길게 — 밝아지는 푸시인 → 비트14 시작점에 서명 디졸브
    ("dissolve", "stills/01_heavenly_body_1944.jpg",
     {"sig": "stills/03_signature_1941.jpg", "span": 2, "bright": True}),
    ("skip", "", {}),
]
SUBS = [
    "당신의 블루투스,\n이 배우에게서\n시작됐다면요?",
    "블루투스 속 기술은,\n채널을 계속 바꾸는 거죠.",
    "이 설계의 원본은,\n1942년의 특허입니다.",
    "적이 엿듣지 못하게,\n어뢰 신호를 지키려던 거였죠.",
    "채널이 88개라,\n따라잡을 수 없죠.",
    "두 기계는 자동피아노\n악보로 박자를 맞췄습니다.",
    "그래서 피아노 건반처럼\n88개죠.",
    "발명자는 군인도,\n공학자도 아니었습니다.",
    "특허의 서명란엔,\n낯선 여자의 이름 하나.",
    "그 여자의 얼굴은,\n온 세상이 알고 있었습니다.",
    "해군은 장치를 서랍에 묻었고,\n보상은 없었습니다.",
    "그녀는 평생\n'얼굴'로만 소비됐습니다.",
    "그 발명자는, 당대\n'세상에서 가장 아름다운 여자'.",
    "할리우드의 전설,\n'헤디 라마르'였습니다.",
]
SUBS_EN = [
    "What if your Bluetooth\nstarted with this actress?",
    "Inside Bluetooth: a signal\nthat keeps switching channels.",
    "Its original blueprint:\na 1942 patent.",
    "So enemies couldn't listen in\non torpedo signals.",
    "Eighty-eight channels,\nimpossible to follow.",
    "The two machines kept time\nwith a player piano roll.",
    "That's why: eighty-eight,\nlike piano keys.",
    "The inventor was\nno soldier or engineer.",
    "On the patent:\none unfamiliar woman's name.",
    "But the whole world\nknew her face.",
    "The Navy buried it;\nshe was never paid.",
    "Her whole life,\nonly the face was seen.",
    "The inventor: 'the most\nbeautiful woman in the world.'",
    "Hollywood legend\nHedy Lamarr.",
]
BOTTOM = {9, 14}      # 서명 카드가 중앙에 오는 비트 — 자막 하단 배치 (겹침 방지)
AMBIENT = [(3, "clipA_radio.mp4", 0.0), (4, "clipA_radio.mp4", 5.85),
           (6, "clipB_pianoroll.mp4", 0.0), (7, "clipB_pianoroll.mp4", 5.2)]
ENC = ["-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS), "-an"]


def run(args):
    r = subprocess.run([FF, "-y", "-v", "error"] + args, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ffmpeg 실패: {' '.join(str(a) for a in args[:10])}…\n{r.stderr[-800:]}")


def compose_card(src, out_png):
    """남색 배경 중앙에 서명 스트립을 얹은 정적 카드 (오버스캔 크기)."""
    run(["-i", src, "-filter_complex",
         f"color=0x0a0f1e:s={OW}x{OH}[bg];[0:v]scale={int(OW*0.86)}:-2[sig];"
         f"[bg][sig]overlay=(W-w)/2:(H-h)/2:shortest=1",
         "-frames:v", "1", out_png])


def compose_pad(src, out_png):
    """가로 스틸: 블러 채움 배경 + 원본 폭맞춤 전경 (오버스캔 크기)."""
    run(["-i", src, "-filter_complex",
         f"[0:v]split[a][b];[a]scale={OW}:{OH}:force_original_aspect_ratio=increase,"
         f"crop={OW}:{OH},gblur=sigma=40,eq=brightness=-0.08[bg];"
         f"[b]scale={OW}:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2",
         "-frames:v", "1", out_png])


def kb(src, dur, out, zoom=0.10, focus="center", post=""):
    """단일 이미지 → 푸시인 세그먼트. 커버 스케일 후 zoompan."""
    frames = max(int(round(dur * FPS)), 2)
    ytab = {"top": "ih*0.10", "mid": "ih/2-(ih/zoom/2)", "center": "ih/2-(ih/zoom/2)"}
    vf = (f"scale={OW}:{OH}:force_original_aspect_ratio=increase,crop={OW}:{OH}:(iw-{OW})/2:(ih-{OH})/2,"
          f"zoompan=z='1+{zoom}*on/{max(frames-1,1)}':x='iw/2-(iw/zoom/2)':y='{ytab[focus]}'"
          f":d={frames}:s={W}x{H}:fps={FPS}{post}")
    run(["-i", src, "-vf", vf, "-frames:v", str(frames)] + ENC + [out])


def seg_clip(src, dur, out, start):
    run(["-ss", f"{start:.3f}", "-i", src, "-t", f"{dur:.4f}", "-vf", f"fps={FPS},scale={W}:{H}"] + ENC + [out])


def load_spec(path):
    """편별 편집 스펙 JSON → (EDIT, SUBS, SUBS_EN, BOTTOM, AMBIENT) 치환.

    형식: {"edit":[{"kind","src","opts"}...], "subs_ko":[...], "subs_en":[...],
           "bottom_beats":[...], "ambient":[{"beat","clip","start"}...]}
    """
    s = json.loads(Path(path).read_text())
    edit = [(e["kind"], e.get("src", ""), e.get("opts", {})) for e in s["edit"]]
    amb = [(a["beat"] - 1, a["clip"], a["start"]) for a in s.get("ambient", [])]
    return edit, s.get("subs_ko", []), s.get("subs_en", []), set(s.get("bottom_beats", [])), amb


def main():
    global EDIT, SUBS, SUBS_EN, BOTTOM, AMBIENT
    args = sys.argv[1:]
    ep_path = Path(args[0])
    lang = args[args.index("--lang") + 1] if "--lang" in args else "ko"
    font = args[args.index("--font") + 1] if "--font" in args else None
    music = args[args.index("--music") + 1] if "--music" in args else None
    if "--edit" in args:
        EDIT, SUBS, SUBS_EN, BOTTOM, AMBIENT = load_spec(args[args.index("--edit") + 1])
    out_dir = ep_path.parent / (ep_path.stem.replace("-beats", "") + "_output")
    tmp = out_dir / "_build"
    tmp.mkdir(exist_ok=True)

    durs = []
    for i in range(1, 15):
        with wave.open(str(out_dir / f"beat{i:02d}_{lang}.wav")) as w:
            durs.append(w.getnframes() / w.getframerate())
    bounds = [0.0]
    for d in durs:
        bounds.append(bounds[-1] + d)
    # 프레임 정확 경계 (누적 드리프트 방지)
    fdurs = [round(bounds[i + 1] * FPS) / FPS - round(bounds[i] * FPS) / FPS for i in range(14)]
    starts = [round(bounds[i] * FPS) / FPS for i in range(14)]

    print("· 비트 세그먼트 렌더링")
    still_post = f",{GRADE},{GRAIN},{VIG}"
    seg_names = []
    for i, ((kind, src, o), _d) in enumerate(zip(EDIT, fdurs), 1):
        if kind == "skip":  # 직전 span 세그먼트에 흡수된 비트
            continue
        dur = sum(fdurs[i - 1:i - 1 + o.get("span", 1)])
        out = str(tmp / f"seg{i:02d}.mp4")
        seg_names.append(f"seg{i:02d}.mp4")
        sp = str(out_dir / src)
        if kind == "still":
            extra = ""
            if o.get("dark"):
                extra = ",eq=brightness=-0.12:saturation=0.45"
            if o.get("bright"):
                extra = ",eq=brightness=0.06:saturation=0.7"
            kb(sp, dur, out, 0.16 if o.get("fast") else 0.10, o.get("focus", "center"), still_post + extra)
        elif kind == "card":
            png = str(tmp / f"card{i:02d}.png")
            compose_card(sp, png)
            kb(png, dur, out, 0.08, "center", f",{GRAIN},{VIG}")
        elif kind == "pad":
            png = str(tmp / f"pad{i:02d}.png")
            compose_pad(sp, png)
            kb(png, dur, out, 0.09, "center", still_post)
        elif kind == "clip":
            seg_clip(sp, dur, out, o["start"])
        elif kind == "image":
            kb(sp, dur, out, 0.16 if o.get("fast") else 0.06, "center", "")
        elif kind == "dissolve":
            fade = 0.5
            # span 병합 시 서명 전환점 = 첫 비트 길이 (자막 경계와 일치)
            d1 = fdurs[i - 1] if o.get("span") else dur * 0.58
            extra = ",eq=brightness=0.06:saturation=0.7" if o.get("bright") else ""
            a, b = str(tmp / "b14a.mp4"), str(tmp / "b14b.mp4")
            kb(sp, d1 + fade, a, 0.10, "top", still_post + extra)
            png = str(tmp / "card14.png")
            compose_card(str(out_dir / o["sig"]), png)
            kb(png, dur - d1 + fade, b, 0.08, "center", f",{GRAIN},{VIG}")
            run(["-i", a, "-i", b, "-filter_complex",
                 f"[0:v][1:v]xfade=transition=fade:duration={fade}:offset={d1 - fade/2:.3f}",
                 "-t", f"{dur:.4f}"] + ENC + [out])
        print(f"  {i:02d} {kind} {dur:.2f}s")

    print("· 비디오 concat")
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{n}'\n" for n in seg_names))
    silent = str(tmp / "video_silent.mp4")
    run(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", silent])

    print("· 오디오 믹스 (나레이션 + 클립 앰비언트)")
    na = tmp / "narr_list.txt"
    na.write_text("".join(f"file '../beat{i:02d}_{lang}.wav'\n" for i in range(1, 15)))
    narr = str(tmp / "narration.wav")
    run(["-f", "concat", "-safe", "0", "-i", str(na), narr])
    amb_in, amb_f, amb_lbl = [], [], []
    for j, (bi, clip, s0) in enumerate(AMBIENT):
        amb_in += ["-ss", f"{s0:.3f}", "-t", f"{fdurs[bi]:.4f}", "-i", str(out_dir / clip)]
        ms = int(starts[bi] * 1000)
        amb_f.append(f"[{j+1}:a]volume=0.4,adelay={ms}|{ms}[a{j}]")
        amb_lbl.append(f"[a{j}]")
    audio = str(tmp / "audio_mix.m4a")
    if amb_f:
        fc = ";".join(amb_f) + f";[0:a]{''.join(amb_lbl)}amix=inputs={len(amb_f)+1}:normalize=0[mix]"
        run(["-i", narr] + amb_in + ["-filter_complex", fc, "-map", "[mix]", "-c:a", "aac", "-b:a", "160k", audio])
    else:  # 생성 클립 없는 편 — 나레이션만
        run(["-i", narr, "-c:a", "aac", "-b:a", "160k", audio])
    if music:
        m = str(tmp / "audio_music.m4a")
        run(["-i", audio, "-i", music, "-filter_complex",
             "[1:a]volume=0.2,afade=t=out:st=" + f"{bounds[-1]-1.2:.2f}" + ":d=1.2[mu];"
             "[0:a][mu]amix=inputs=2:normalize=0:duration=first[mix]",
             "-map", "[mix]", "-c:a", "aac", "-b:a", "160k", m])
        audio = m

    final = str(out_dir / f"ep-p01_{lang}{'' if music else '_preview'}.mp4")
    if font and "--no-subs" not in args:
        print("· 자막 번인 + 먹싱 (libass)")
        family = "Noto Sans KR"
        try:  # 폰트 파일에서 패밀리명 자동 추출 (fonttools 있으면) — 커스텀 폰트 교체 대응
            from fontTools.ttLib import TTFont
            name = TTFont(font)["name"]
            rec = name.getName(16, 3, 1, 0x409) or name.getName(1, 3, 1, 0x409)
            if rec:
                family = rec.toUnicode()
        except Exception:
            pass
        print(f"  폰트 패밀리: {family}")

        def ts(sec):
            cs = int(round(sec * 100))
            return f"{cs//360000}:{cs//6000%60:02d}:{cs//100%60:02d}.{cs%100:02d}"

        ass = tmp / "subs.ass"
        lines = [
            "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
            "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
            "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            # 크기 52·중앙 배치(Alignment 5) — 피드백 2026-08-28
            f"Style: Default,{family},52,&H00FFFFFF,&H00FFFFFF,&HD0000000,&H80000000,"
            "-1,0,0,0,100,100,0,0,1,3,1,5,25,25,0,1", "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        ]
        subs = SUBS if lang == "ko" else SUBS_EN
        for i, t in enumerate(subs):
            bottom = (i + 1) in BOTTOM
            mv, tag = (250, "{\\an2}") if bottom else (0, "")
            lines.append(f"Dialogue: 0,{ts(starts[i])},{ts(starts[i]+fdurs[i])},Default,,0,0,{mv},,"
                         + tag + t.replace("\n", "\\N"))
        ass.write_text("\n".join(lines))
        run(["-i", silent, "-i", audio,
             "-vf", f"subtitles=filename='{ass}':fontsdir='{Path(font).parent}'",
             "-map", "0:v", "-map", "1:a", "-c:a", "copy"] + ENC[:8] + ["-shortest", final])
    else:
        run(["-i", silent, "-i", audio, "-map", "0:v", "-map", "1:a", "-c", "copy", "-shortest", final])
    print(f"✓ {final}  (총 {bounds[-1]:.1f}s)")


if __name__ == "__main__":
    main()
