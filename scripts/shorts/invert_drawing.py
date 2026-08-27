# -*- coding: utf-8 -*-
"""특허 도면 반전 — 흰 종이·검은 선 → 남색 배경·시안 선 (블루프린트 룩).

문서 중심 편(P05·P06 등)은 도면이 화면의 대부분을 차지하는데, 흰 배경 위에 흰 자막을 얹으면
읽히지 않는다. 반전하면 자막 대비가 확보되고 시리즈의 남색·청록 톤과도 맞는다.

사용: python3 scripts/shorts/invert_drawing.py <입력.png> [<입력2> ...]
산출: 같은 폴더에 <이름>_inv.png
"""
import os, sys
from pathlib import Path

from PIL import Image, ImageChops, ImageOps

NAVY = (10, 17, 34)
LINE = (188, 226, 240)


def invert(path):
    p = Path(path)
    g = Image.open(p).convert("L")
    g = ImageOps.autocontrast(g, cutoff=1)
    ink = ImageOps.invert(g)                       # 선=밝음, 종이=어두움
    ink = ink.point(lambda v: 0 if v < 40 else min(255, int((v - 40) * 1.6)))
    out = Image.new("RGB", g.size, NAVY)
    out.paste(Image.new("RGB", g.size, LINE), (0, 0), ink)
    noise = Image.frombytes("L", g.size, os.urandom(g.size[0] * g.size[1]))
    noise = noise.point(lambda v: int(v * 0.09))
    out = ImageChops.add(out, Image.merge("RGB", (noise, noise, noise)))
    dest = p.with_name(p.stem + "_inv.png")
    out.save(dest, "PNG")
    print(f"✓ {dest.name} ({out.size[0]}x{out.size[1]})")
    return dest


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for a in sys.argv[1:]:
        invert(a)
