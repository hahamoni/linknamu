# -*- coding: utf-8 -*-
"""쇼츠 커버 합성 (1080×1920) — 아카이브 스틸/도면에 시리즈 그레이드를 입힌다.

커버 텍스트는 **굽지 않는다**(유튜브 업로드 시 편집 오버레이). 이 스크립트는 배경만 만든다.

사용:
  python3 scripts/shorts/render_cover.py <출력.png> <주이미지> [--overlay <아래에 얹을 스트립>] \
      [--focus top|center] [--invert]

예:
  python3 scripts/shorts/render_cover.py docs/shorts/ep-p02_output/cover.png \
      docs/shorts/ep-p02_output/stills/01_magie_1906_wt.jpg --overlay docs/shorts/ep-p02_output/stills/05_board_cover.jpg
"""
import os, sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps

W, H = 1080, 1920
NAVY = (14, 24, 44)


def cover_crop(im, w, h, y_bias=0.10):
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = (im.width - w) // 2
    y = min(int(im.height * y_bias), max(0, im.height - h))
    return im.crop((x, y, x + w, y + h))


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        sys.exit(__doc__)
    out, main_src = Path(args[0]), args[1]
    overlay = args[args.index("--overlay") + 1] if "--overlay" in args else None
    focus = args[args.index("--focus") + 1] if "--focus" in args else "top"
    out.parent.mkdir(parents=True, exist_ok=True)

    base = Image.open(main_src).convert("RGB")
    if "--invert" in args:
        g = ImageOps.autocontrast(base.convert("L"), cutoff=1)
        ink = ImageOps.invert(g).point(lambda v: 0 if v < 40 else min(255, int((v - 40) * 1.6)))
        base = Image.new("RGB", g.size, NAVY)
        base.paste(Image.new("RGB", g.size, (188, 226, 240)), (0, 0), ink)

    img = cover_crop(base, W, H, 0.06 if focus == "top" else 0.5 - (H / base.height) / 2 if base.height > H else 0.0)
    img = ImageEnhance.Color(img).enhance(0.5)
    img = ImageEnhance.Contrast(img).enhance(1.08)
    img = Image.blend(img, Image.new("RGB", (W, H), NAVY), 0.20)

    # 하단 어둡게 — 업로드 시 텍스트가 올라갈 자리
    grad = Image.new("L", (1, H), 0)
    for y in range(H):
        t = max(0.0, (y / H - 0.52) / 0.48)
        grad.putpixel((0, y), int(200 * t))
    img = Image.composite(Image.new("RGB", (W, H), (5, 9, 18)), img, grad.resize((W, H)))

    if overlay and os.path.exists(overlay):
        ov = Image.open(overlay).convert("RGB")
        ow = int(W * 0.80)
        ov = ov.resize((ow, max(1, int(ov.height * ow / ov.width))), Image.LANCZOS)
        ov = ImageEnhance.Color(ov).enhance(0.6)
        img.paste(ov, ((W - ow) // 2, int(H * 0.72)))

    noise = Image.frombytes("L", (W, H), os.urandom(W * H)).point(lambda v: int(v * 0.10))
    img = ImageChops.add(img, Image.merge("RGB", (noise, noise, noise)))
    vig = Image.new("L", (W // 4, H // 4), 0)
    ImageDraw.Draw(vig).ellipse([-W // 14, -H // 14, W // 4 + W // 14, H // 4 + H // 14], fill=255)
    vig = vig.resize((W, H)).filter(ImageFilter.GaussianBlur(130)).point(lambda v: 70 + v * 185 // 255)
    img = Image.composite(img, Image.new("RGB", (W, H), (0, 0, 0)), vig)
    img.save(out, "PNG")
    print(f"✓ {out} ({W}x{H})")


if __name__ == "__main__":
    main()
