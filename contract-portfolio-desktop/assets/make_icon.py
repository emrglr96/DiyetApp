# -*- coding: utf-8 -*-
"""
Uygulama ikonu (app.ico) üretir — koyu yuvarlatılmış zemin üzerinde,
marj sağlığı renklerinde bir sütun grafiği. Çok boyutlu .ico kaydeder.

Çalıştır:  python assets/make_icon.py
"""
import os
from PIL import Image, ImageDraw

BG1 = (24, 32, 41)      # --panel
BG2 = (16, 21, 28)      # --bg
BARS = [
    ((79, 163, 217), 0.55),   # accent
    ((63, 182, 139), 0.80),   # ok
    ((224, 168, 60), 0.62),   # warn
    ((224, 90, 71), 0.42),    # crit
]

S = 256
R = 46  # köşe yarıçapı


def rounded(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def build():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # zemin: dikey degrade (basit) + yuvarlatılmış maske
    grad = Image.new("RGBA", (S, S))
    gd = ImageDraw.Draw(grad)
    for y in range(S):
        t = y / (S - 1)
        c = tuple(int(BG1[i] + (BG2[i] - BG1[i]) * t) for i in range(3)) + (255,)
        gd.line([(0, y), (S, y)], fill=c)
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, S - 1, S - 1], radius=R, fill=255)
    img.paste(grad, (0, 0), mask)

    # ince çerçeve
    d.rounded_rectangle([2, 2, S - 3, S - 3], radius=R - 2,
                        outline=(38, 48, 60, 255), width=3)

    # sütunlar
    n = len(BARS)
    pad_x = 46
    gap = 16
    base_y = S - 54
    top_min = 60
    usable_w = S - 2 * pad_x
    bw = (usable_w - gap * (n - 1)) / n
    for i, (col, h) in enumerate(BARS):
        x0 = pad_x + i * (bw + gap)
        x1 = x0 + bw
        bar_h = (base_y - top_min) * h
        y0 = base_y - bar_h
        d.rounded_rectangle([x0, y0, x1, base_y], radius=7, fill=col + (255,))

    # taban çizgisi
    d.line([(pad_x - 6, base_y + 5), (S - pad_x + 6, base_y + 5)],
           fill=(90, 104, 118, 255), width=4)

    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "app.ico")
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(out, format="ICO", sizes=sizes)
    # PNG önizleme (isteğe bağlı)
    img.save(os.path.join(here, "app_icon_preview.png"))
    print("Yazıldı:", out)


if __name__ == "__main__":
    build()
