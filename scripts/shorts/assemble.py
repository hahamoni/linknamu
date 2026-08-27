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
import os, subprocess, sys, wave
from pathlib import Path

FF = os.environ.get("FFMPEG", "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2")
W, H, FPS = 720, 1280, 24
OW, OH = W * 2, H * 2  # 줌 여유용 오버스캔
GRADE = "eq=saturation=0.55:contrast=1.06,colorbalance=bs=0.06:bm=0.03:bh=-0.02"
GRAIN = "noise=alls=7:allf=t+u"
VIG = "vignette=PI/4.4"

# 비트별 비주얼: (종류, 소스, 옵션) — still(그레이드+줌) / card(서명 카드) / pad(블러 패드) /
# clip(구간 트림) / image(스타일 완성본, 그레이드 없음) / dissolve(초상→서명 카드)
EDIT = [
    ("still", "stills/01_heavenly_body_1944.jpg", {"focus": "top"}),
    ("still", "stills/02_screenland_1942.png", {}),
    ("card", "stills/03_signature_1941.jpg", {}),
    ("clip", "clipA_radio.mp4", {"start": 0.0}),
    ("clip", "clipA_radio.mp4", {"start": 5.85}),
    ("image", "diagram_88ch.png", {}),
    ("clip", "clipB_pianoroll.mp4", {"start": 0.0}),
    ("clip", "clipB_pianoroll.mp4", {"start": 5.2}),
    ("pad", "stills/09_kiesler_1933.jpg", {}),
    ("still", "stills/10_patent_page7.jpg", {"focus": "mid", "fast": True}),
    ("pad", "stills/11_samson_1949.png", {}),
    ("still", "stills/01_heavenly_body_1944.jpg", {"focus": "top", "dark": True}),
    ("still", "stills/01_heavenly_body_1944.jpg", {"focus": "top", "bright": True}),
    ("dissolve", "stills/01_heavenly_body_1944.jpg", {"sig": "stills/03_signature_1941.jpg"}),
]
SUBS = [
    "가장 아름답다던 이 배우는,\n배우만이 아니었습니다.",
    "1942년, 특허청에\n서류 한 장이 접수됩니다.",
    "발명자 칸의 이름은\n헐리우드 배우였습니다.",
    "장치의 목적은 무선 신호를\n도청에서 지키는 것.",
    "송신기와 수신기가\n주파수를 함께 뜁니다.",
    "주파수는 모두 88개였습니다.",
    "두 장치를 맞물리게 한 부품은\n자동피아노의 종이 롤.",
    "88은 피아노 건반의 수입니다.",
    "미 해군은 이 장치를\n채택하지 않았습니다.",
    "서류는 서랍으로 들어갔습니다.",
    "특허는 1959년에 만료됐습니다.",
    "그녀는 아무 보상도\n받지 못했습니다.",
    "상이 온 것은 55년 뒤였습니다.",
    "수상 소감은 한마디,\n\"이제야 왔군요.\"",
]
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


def main():
    args = sys.argv[1:]
    ep_path = Path(args[0])
    lang = args[args.index("--lang") + 1] if "--lang" in args else "ko"
    font = args[args.index("--font") + 1] if "--font" in args else None
    music = args[args.index("--music") + 1] if "--music" in args else None
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
    for i, ((kind, src, o), dur) in enumerate(zip(EDIT, fdurs), 1):
        out = str(tmp / f"seg{i:02d}.mp4")
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
            kb(sp, dur, out, 0.06, "center", "")
        elif kind == "dissolve":
            fade, d1 = 0.5, dur * 0.58
            a, b = str(tmp / "b14a.mp4"), str(tmp / "b14b.mp4")
            kb(sp, d1 + fade, a, 0.10, "top", still_post)
            png = str(tmp / "card14.png")
            compose_card(str(out_dir / o["sig"]), png)
            kb(png, dur - d1 + fade, b, 0.08, "center", f",{GRAIN},{VIG}")
            run(["-i", a, "-i", b, "-filter_complex",
                 f"[0:v][1:v]xfade=transition=fade:duration={fade}:offset={d1 - fade/2:.3f}",
                 "-t", f"{dur:.4f}"] + ENC + [out])
        print(f"  {i:02d} {kind} {dur:.2f}s")

    print("· 비디오 concat")
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file 'seg{i:02d}.mp4'\n" for i in range(1, 15)))
    silent = str(tmp / "video_silent.mp4")
    run(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", silent])

    print("· 오디오 믹스 (나레이션 + 클립 앰비언트)")
    na = tmp / "narr_list.txt"
    na.write_text("".join(f"file '../beat{i:02d}_{lang}.wav'\n" for i in range(1, 15)))
    narr = str(tmp / "narration.wav")
    run(["-f", "concat", "-safe", "0", "-i", str(na), narr])
    amb_in, amb_f, amb_lbl = [], [], []
    for j, (bi, clip, s0) in enumerate([(3, "clipA_radio.mp4", 0.0), (4, "clipA_radio.mp4", 5.85),
                                        (6, "clipB_pianoroll.mp4", 0.0), (7, "clipB_pianoroll.mp4", 5.2)]):
        amb_in += ["-ss", f"{s0:.3f}", "-t", f"{fdurs[bi]:.4f}", "-i", str(out_dir / clip)]
        ms = int(starts[bi] * 1000)
        amb_f.append(f"[{j+1}:a]volume=0.4,adelay={ms}|{ms}[a{j}]")
        amb_lbl.append(f"[a{j}]")
    fc = ";".join(amb_f) + f";[0:a]{''.join(amb_lbl)}amix=inputs=5:normalize=0[mix]"
    audio = str(tmp / "audio_mix.m4a")
    run(["-i", narr] + amb_in + ["-filter_complex", fc, "-map", "[mix]", "-c:a", "aac", "-b:a", "160k", audio])
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
            "Style: Default,Noto Sans KR,44,&H00FFFFFF,&H00FFFFFF,&HD0000000,&H80000000,"
            "-1,0,0,0,100,100,0,0,1,3,1,2,40,40,270,1", "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        ]
        for i, t in enumerate(SUBS):
            lines.append(f"Dialogue: 0,{ts(starts[i])},{ts(starts[i]+fdurs[i])},Default,,0,0,0,,"
                         + t.replace("\n", "\\N"))
        ass.write_text("\n".join(lines))
        run(["-i", silent, "-i", audio,
             "-vf", f"subtitles=filename='{ass}':fontsdir='{Path(font).parent}'",
             "-map", "0:v", "-map", "1:a", "-c:a", "copy"] + ENC[:8] + ["-shortest", final])
    else:
        run(["-i", silent, "-i", audio, "-map", "0:v", "-map", "1:a", "-c", "copy", "-shortest", final])
    print(f"✓ {final}  (총 {bounds[-1]:.1f}s)")


if __name__ == "__main__":
    main()
