# -*- coding: utf-8 -*-
"""P01 커버 합성 (1080×1920) — Heavenly Body(1944) 초상 + 서명 오버레이.

패키지 문서 커버 스펙: 아카이브 합성, 생성 0크레딧, 커버 텍스트는 유튜브 편집
오버레이로 얹으므로 여기서는 굽지 않는다. 서명 잉크를 화이트로 반전해 하단에 빛나듯 얹는다.

사용: python3 scripts/shorts/render_cover.py
입력: ep-p01_output/stills/01_heavenly_body_1944.jpg, 03_signature_1941.jpg
산출: ep-p01_output/cover_composite.png
"""
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

W, H = 1080, 1920
OUT = Path("docs/shorts/ep-p01_output")


def cover_crop(im, w, h, y_bias=0.10):
    """비율 유지 커버 크롭. y_bias: 위쪽(얼굴) 치우침."""
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = (im.width - w) // 2
    y = min(int(im.height * y_bias), im.height - h)
    return im.crop((x, y, x + w, y + h))


def main():
    portrait = Image.open(OUT / "stills/01_heavenly_body_1944.jpg").convert("RGB")
    img = cover_crop(portrait, W, H, 0.06)

    # 그레이드: 저채도 + 남색 틴트 + 대비
    img = ImageEnhance.Color(img).enhance(0.45)
    img = ImageEnhance.Contrast(img).enhance(1.08)
    navy = Image.new("RGB", (W, H), (14, 24, 44))
    img = Image.blend(img, navy, 0.22)

    # 하단 어둡게 (서명·텍스트 오버레이 자리)
    grad = Image.new("L", (1, H), 0)
    for y in range(H):
        t = max(0.0, (y / H - 0.55) / 0.45)
        grad.putpixel((0, y), int(190 * t))
    grad = grad.resize((W, H))
    img = Image.composite(Image.new("RGB", (W, H), (5, 9, 18)), img, grad)

    # 서명: 잉크 추출 → 화이트 반전 + 글로우
    sig = Image.open(OUT / "stills/03_signature_1941.jpg").convert("L")
    sig = ImageOps.autocontrast(sig)
    ink = ImageOps.invert(sig).point(lambda v: 0 if v < 70 else min(255, int((v - 70) * 1.8)))
    sw = int(W * 0.78)
    ink = ink.resize((sw, int(ink.height * sw / ink.width)), Image.LANCZOS)
    sx, sy = (W - sw) // 2, int(H * 0.80)
    glow = ink.filter(ImageFilter.GaussianBlur(6))
    for layer, color in ((glow, (110, 190, 210)), (ink, (235, 248, 252))):
        tile = Image.new("RGB", layer.size, color)
        img.paste(tile, (sx, sy), layer)

    # 필름 그레인 + 비네트
    noise = Image.frombytes("L", (W, H), os.urandom(W * H)).point(lambda v: int(v * 0.10))
    from PIL import ImageChops
    img = ImageChops.add(img, Image.merge("RGB", (noise, noise, noise)))
    vig = Image.new("L", (W // 4, H // 4), 0)
    ImageDraw.Draw(vig).ellipse([-W // 14, -H // 14, W // 4 + W // 14, H // 4 + H // 14], fill=255)
    vig = vig.resize((W, H)).filter(ImageFilter.GaussianBlur(130)).point(lambda v: 70 + v * 185 // 255)
    img = Image.composite(img, Image.new("RGB", (W, H), (0, 0, 0)), vig)

    out = OUT / "cover_composite.png"
    img.save(out, "PNG")
    print(f"✓ {out} ({out.stat().st_size/1e6:.1f}MB)")


if __name__ == "__main__":
    main()
