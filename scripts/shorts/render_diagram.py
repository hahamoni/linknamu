# -*- coding: utf-8 -*-
"""P01 비트6 — 88채널 주파수 도약 다이어그램 프로그래매틱 렌더링 (1080×1920).

생성 모델은 '정확히 88개'를 못 세므로 코드로 그린다 (0크레딧, 결정적 재현).
스펙: ep-p01-hedy-lamarr.md §생성 클립 프롬프트의 그래픽 항목 — 남색 배경,
좌우 송수신탑, 피아노 현처럼 쌓인 88개 시안 주파수 라인, 도약 중인 신호 점,
무거운 필름 그레인, 블루프린트 선화. 텍스트·인물 없음.

사용: python3 scripts/shorts/render_diagram.py [출력경로]
기본 출력: docs/shorts/ep-p01_output/diagram_88ch.png
의존성: pillow (pip install pillow)
"""
import os, random, sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1920
NAVY = (8, 14, 28)
CYAN_DIM = (61, 122, 138)
CYAN_HI = (127, 212, 232)
N_LINES = 88
X0, X1 = 260, 820          # 라인 좌우
Y0, Y1 = 430, 1490         # 라인 상하
GLOW_IDX = 31              # 빛나는 라인 (위에서부터)
random.seed(2292387)       # 특허번호 — 결정적 재현


def tower(draw, cx, base_y, h, side):
    """블루프린트 스타일 무선탑: 격자 마스트 + 안테나 + 방송 아크."""
    top_y = base_y - h
    w0, w1 = 46, 10  # 바닥/꼭대기 반폭
    steps = 6
    pts_l, pts_r = [], []
    for i in range(steps + 1):
        t = i / steps
        y = base_y - h * t
        half = w0 + (w1 - w0) * t
        pts_l.append((cx - half, y)); pts_r.append((cx + half, y))
    for a, b in zip(pts_l, pts_l[1:]):
        draw.line([a, b], fill=CYAN_DIM, width=3)
    for a, b in zip(pts_r, pts_r[1:]):
        draw.line([a, b], fill=CYAN_DIM, width=3)
    for i in range(steps):
        draw.line([pts_l[i], pts_r[i + 1]], fill=CYAN_DIM, width=2)
        draw.line([pts_r[i], pts_l[i + 1]], fill=CYAN_DIM, width=2)
        draw.line([pts_l[i], pts_r[i]], fill=CYAN_DIM, width=2)
    draw.line([(cx, top_y), (cx, top_y - 60)], fill=CYAN_DIM, width=3)
    draw.ellipse([cx - 5, top_y - 70, cx + 5, top_y - 60], fill=CYAN_HI)
    for r, alpha_w in ((36, 3), (66, 2), (96, 2)):
        box = [cx - r, top_y - 65 - r, cx + r, top_y - 65 + r]
        if side == "L":
            draw.arc(box, -55, 55, fill=CYAN_DIM, width=alpha_w)
        else:
            draw.arc(box, 125, 235, fill=CYAN_DIM, width=alpha_w)


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs/shorts/ep-p01_output/diagram_88ch.png")
    out.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    # 배경 미세 그라데이션 (위가 아주 살짝 밝음)
    for y in range(H):
        t = y / H
        c = tuple(int(v + (6 - 12 * t)) for v in NAVY)
        draw.line([(0, y), (W, y)], fill=c)

    # 88개 주파수 라인 — 피아노 현처럼, 밝기 미세 변주
    ys = [Y0 + (Y1 - Y0) * i / (N_LINES - 1) for i in range(N_LINES)]
    for i, y in enumerate(ys):
        if i == GLOW_IDX:
            continue
        j = random.uniform(0.75, 1.1)
        c = tuple(min(255, int(v * j)) for v in CYAN_DIM)
        draw.line([(X0, y), (X1, y)], fill=c, width=2)

    # 좌우 송수신탑
    tower(draw, 130, Y1 + 20, 620, "L")
    tower(draw, W - 130, Y1 + 20, 620, "R")

    # 글로우 레이어: 빛나는 라인 + 신호 점 + 도약 궤적
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gy = ys[GLOW_IDX]
    gd.line([(X0, gy), (X1, gy)], fill=CYAN_HI, width=4)
    dot_x = X0 + (X1 - X0) * 0.62
    gd.ellipse([dot_x - 14, gy - 14, dot_x + 14, gy + 14], fill=CYAN_HI)
    for k, (di, dx, r) in enumerate([(-9, 0.38, 9), (7, 0.50, 7), (-4, 0.30, 5)]):
        ty = ys[GLOW_IDX + di]
        tx = X0 + (X1 - X0) * dx
        a = 150 - k * 45
        gd.ellipse([tx - r, ty - r, tx + r, ty + r], fill=(a * CYAN_HI[0] // 255, a * CYAN_HI[1] // 255, a * CYAN_HI[2] // 255))
        gd.line([(dot_x, gy), (tx, ty)], fill=(30, 55, 66), width=1)
    glow = glow.filter(ImageFilter.GaussianBlur(6))
    from PIL import ImageChops
    img = ImageChops.screen(img, glow)
    # 선명한 코어 다시 그리기
    draw = ImageDraw.Draw(img)
    draw.line([(X0, gy), (X1, gy)], fill=CYAN_HI, width=3)
    draw.ellipse([dot_x - 8, gy - 8, dot_x + 8, gy + 8], fill=(210, 245, 255))

    # 무거운 필름 그레인
    noise = Image.frombytes("L", (W, H), os.urandom(W * H))
    noise = noise.point(lambda v: int(v * 0.16))
    img = ImageChops.add(img, Image.merge("RGB", (noise, noise, noise)))

    # 비네트
    vig = Image.new("L", (W // 4, H // 4), 0)
    vd = ImageDraw.Draw(vig)
    vd.ellipse([-W // 16, -H // 16, W // 4 + W // 16, H // 4 + H // 16], fill=255)
    vig = vig.resize((W, H)).filter(ImageFilter.GaussianBlur(120)).point(lambda v: 60 + v * 195 // 255)
    black = Image.new("RGB", (W, H), (0, 0, 0))
    img = Image.composite(img, black, vig)

    img.save(out, "PNG")
    print(f"✓ {out} ({out.stat().st_size/1e6:.1f}MB, {W}x{H}, 라인 {N_LINES}개)")


if __name__ == "__main__":
    main()
