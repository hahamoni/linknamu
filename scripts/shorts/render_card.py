# -*- coding: utf-8 -*-
"""특허 인용 카드 렌더링 (1080×1920) — 문서에서 뽑은 한 줄을 화면에 세우는 컷.

생성 모델 없이 코드로 그린다(0크레딧, 결정적 재현). P01 서명 카드와 같은 문법:
남색 배경 + 종이질감 스트립 + 타자기체 인용 + 강조 단어 하이라이트 + 필름 그레인·비네트.

사용:
  python3 scripts/shorts/render_card.py <출력.png> "인용문" [--highlight "강조할 부분"] \
      [--caption "출처 한 줄"] [--font <ttf>]

예:
  python3 scripts/shorts/render_card.py docs/shorts/ep-p04_output/stills/20_claim_card.png \
      "engaging eight cube pieces as a composite cube" --highlight "eight" --caption "US3,655,201 · Claim 3"
"""
import os, sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
NAVY = (10, 16, 32)
PAPER = (232, 226, 208)
INK = (26, 28, 32)
HL = (196, 148, 42)      # 강조 밑줄·박스
CAPTION = (120, 150, 168)
FALLBACK_FONTS = [
    "/usr/share/fonts/truetype/freefont/FreeMono.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
]


def pick_font(path, size):
    for p in ([path] if path else []) + FALLBACK_FONTS:
        if p and os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def wrap(draw, text, font, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        sys.exit(__doc__)
    out = Path(args[0])
    text = args[1]
    hl = args[args.index("--highlight") + 1] if "--highlight" in args else None
    cap = args[args.index("--caption") + 1] if "--caption" in args else None
    fpath = args[args.index("--font") + 1] if "--font" in args else None
    out.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    for y in range(H):                      # 미세 그라데이션
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(v + (8 - 16 * t)) for v in NAVY))

    font = pick_font(fpath, 58)
    margin = 96
    lines = wrap(d, text, font, W - margin * 2 - 60)
    lh = int(font.size * 1.55)
    strip_h = lh * len(lines) + 130
    y0 = (H - strip_h) // 2

    # 종이 스트립
    paper = Image.new("RGB", (W - margin, strip_h), PAPER)
    pd = ImageDraw.Draw(paper)
    noise = Image.frombytes("L", paper.size, os.urandom(paper.size[0] * paper.size[1]))
    paper = ImageChops.subtract(paper, Image.merge("RGB", (noise.point(lambda v: v // 22),) * 3))
    pd = ImageDraw.Draw(paper)
    ty = 66
    for ln in lines:
        x = 62
        if hl and hl.lower() in ln.lower():             # 강조 단어에 밑줄+연한 박스
            i = ln.lower().index(hl.lower())
            pre, mid = ln[:i], ln[i:i + len(hl)]
            x0 = x + pd.textlength(pre, font=font)
            wid = pd.textlength(mid, font=font)
            pd.rectangle([x0 - 8, ty - 6, x0 + wid + 8, ty + font.size + 12], fill=(214, 198, 150))
            pd.line([(x0 - 4, ty + font.size + 14), (x0 + wid + 4, ty + font.size + 14)], fill=HL, width=5)
        pd.text((x, ty), ln, font=font, fill=INK)
        ty += lh
    img.paste(paper, (margin // 2, y0))

    if cap:
        cf = pick_font(fpath, 34)
        cw = d.textlength(cap, font=cf)
        d.text(((W - cw) / 2, y0 + strip_h + 46), cap, font=cf, fill=CAPTION)

    n2 = Image.frombytes("L", (W, H), os.urandom(W * H)).point(lambda v: int(v * 0.13))
    img = ImageChops.add(img, Image.merge("RGB", (n2, n2, n2)))
    vig = Image.new("L", (W // 4, H // 4), 0)
    ImageDraw.Draw(vig).ellipse([-W // 15, -H // 15, W // 4 + W // 15, H // 4 + H // 15], fill=255)
    vig = vig.resize((W, H)).filter(ImageFilter.GaussianBlur(120)).point(lambda v: 66 + v * 189 // 255)
    img = Image.composite(img, Image.new("RGB", (W, H), (0, 0, 0)), vig)
    img.save(out, "PNG")
    print(f"✓ {out} ({W}x{H}, {len(lines)}줄)")


if __name__ == "__main__":
    main()
