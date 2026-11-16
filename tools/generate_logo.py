"""
==========================================================
PEMBUAT LOGO APLIKASI - AGRIUNO
==========================================================
Skrip pembantu yang menghasilkan seluruh aset visual AgriUno:

* ``assets/logo_agriuno.png``          - emblem berbentuk 512x512 RGBA
* ``assets/logo_agriuno_wordmark.png``  - lockup emblem + wordmark
* ``assets/logo_agriuno.ico``          - ikon untuk berkas .exe

Konsep visual:
  Emblem berbentuk kotak bersudut membulat dengan gradien hijau
 Agriculture. Di dalamnya terdapat monogram huruf "A" yang
  disusun dari batang tanaman dewasa, diselingi helai daun padi,
  dan dilingkupi oleh dua baris landskap (sawah) sebagai lambang
  rantai pasok hasil panen.

Jalankan skrip ini bila Wants nichts aset visual perlu dibangun ulang::

    python tools/generate_logo.py

Pustaka Pillow (PIL) merupakan satu-satunya dependensi tambahan.
"""

import os

from PIL import Image, ImageDraw, ImageFont

# ------------------------------------------------------------
# PARAMETER WARNA (selaras dengan config/constants.py)
# ------------------------------------------------------------
HIJAU_TUA = (27, 67, 50)  # #1b4332
HIJAU_TENGAH = (45, 106, 79)  # #2d6a4f
HIJAU_MUDA = (133, 193, 153)  # #85c199
KREM = (246, 241, 226)  # #f6f1e2
KREM_MUDA = (255, 252, 243)
EMAS = (217, 119, 6)  # #d97706

#: Lokasi folder aset.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

#: Faktor supersampling untuk menghasilkan tepi halus.
SS = 4


# ------------------------------------------------------------
# Helper
# ------------------------------------------------------------
def _lerp(c1, c2, t):
    """Mencampur dua warna RGB dengan rasio t (0..1)."""
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(c1, c2, strict=False))


def _vertical_gradient(size, top, bottom):
    """Membuat gradien vertikal RGB."""
    w, h = size
    img = Image.new("RGB", (1, h))
    px = img.load()
    for y in range(h):
        px[0, y] = _lerp(top, bottom, y / max(1, h - 1))
    return img.resize((w, h), Image.BILINEAR)


def _rounded_gradient(size, radius, top, bottom):
    """Gradien vertikal dengan sudut membulat (mask alpha)."""
    grad = _vertical_gradient(size, top, bottom)
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255
    )
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.paste(grad, (0, 0), mask)
    return out


def _load_font(size, bold=True, italic=False):
    """Memuat berkas TTF sistem dengan beberapa cadangan."""
    candidates = []
    if bold and italic:
        candidates += ["seguibl.ttf", "arialbi.ttf"]
    elif bold:
        candidates += ["segoeuib.ttf", "arialbd.ttf", "calibrib.ttf"]
    elif italic:
        candidates += ["seguili.ttf", "ariali.ttf"]
    else:
        candidates += ["segoeui.ttf", "arial.ttf", "calibri.ttf"]

    for name in candidates:
        path = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", name)
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _leaf(draw, center, length, width, angle, color):
    """Menggambar helai daun runcing yang diputar sebesar ``angle`` derajat."""
    pad = int(length)
    layer = Image.new("RGBA", (pad * 2, pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # Bentuk daun: dua busur yang bertemu pada kedua ujung.
    top = (pad, pad - length // 2)
    bottom = (pad, pad + length // 2)
    d.polygon(
        [
            top,
            (pad + width // 2, pad - length // 6),
            (pad + width // 2, pad + length // 6),
            bottom,
            (pad - width // 2, pad + length // 6),
            (pad - width // 2, pad - length // 6),
        ],
        fill=color,
    )
    # Urat tengah daun.
    d.line([top, bottom], fill=(0, 0, 0, 0), width=2)

    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=False)
    draw._image.alpha_composite(layer, (center[0] - pad, center[1] - pad))


# ------------------------------------------------------------
# Emblem
# ------------------------------------------------------------
def build_emblem(size=512):
    """Membangun emblem AgriUno berukuran ``size`` piksel (RGBA)."""
    S = size * SS
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))

    # 1) Latar: kotak bersudut membulat dengan gradien hijau.
    radius = int(S * 0.22)
    badge = _rounded_gradient((S, S), radius, HIJAU_TENGAH, HIJAU_TUA)
    img.alpha_composite(badge)

    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # 2) Cincin tipis di dalam badge sebagai pembatas emblem.
    inset = int(S * 0.075)
    d.rounded_rectangle(
        [inset, inset, S - inset, S - inset],
        radius=int(radius * 0.82),
        outline=HIJAU_MUDA + (110,),
        width=max(2, int(S * 0.009)),
    )

    # 3) Baris landskap (sawah) di bagian bawah emblem.
    for yy, alpha in ((0.70, 90), (0.775, 130), (0.85, 170)):
        y = int(S * yy)
        d.arc(
            [int(S * 0.16), y - int(S * 0.09), int(S * 0.84), y + int(S * 0.09)],
            start=200,
            end=340,
            fill=HIJAU_MUDA + (alpha,),
            width=max(2, int(S * 0.016)),
        )

    # 4) Monogram "A" - dua batang penyusun huruf A.
    apex = (int(S * 0.50), int(S * 0.255))
    left_foot = (int(S * 0.295), int(S * 0.655))
    right_foot = (int(S * 0.705), int(S * 0.655))
    stroke = int(S * 0.075)

    d.polygon(
        [
            (apex[0], apex[1]),
            (apex[0] + stroke // 2, apex[1] + int(S * 0.035)),
            (right_foot[0], right_foot[1]),
            (right_foot[0] - stroke, right_foot[1]),
        ],
        fill=KREM,
    )
    d.polygon(
        [
            (apex[0], apex[1]),
            (apex[0] - stroke // 2, apex[1] + int(S * 0.035)),
            (left_foot[0], left_foot[1]),
            (left_foot[0] + stroke, left_foot[1]),
        ],
        fill=KREM,
    )
    # Balok silang huruf A.
    d.rounded_rectangle(
        [int(S * 0.385), int(S * 0.505), int(S * 0.615), int(S * 0.505) + stroke],
        radius=stroke // 3,
        fill=KREM,
    )

    # 5) Helai daun padi pada batang kiri dan kanan.
    _leaf(d, (int(S * 0.335), int(S * 0.395)), int(S * 0.30), int(S * 0.115), 28, HIJAU_MUDA)
    _leaf(d, (int(S * 0.665), int(S * 0.395)), int(S * 0.30), int(S * 0.115), -28, HIJAU_MUDA)

    # 6) Tunas kecil di puncak monogram (menegaskan unsur tanaman).
    _leaf(d, (int(S * 0.50), int(S * 0.205)), int(S * 0.20), int(S * 0.085), 0, EMAS)

    img.alpha_composite(layer)

    # 7) Penalaan akhir.
    img = img.resize((size, size), Image.LANCZOS)
    return img


# ------------------------------------------------------------
# Wordmark
# ------------------------------------------------------------
def build_wordmark(emblem=None, width=None, scale=3):
    """Membangun lockup emblem + wordmark "AgriUno" beserta sub-teks.

    Parameter ``scale`` mengatur faktor supersampling sehingga gambar
    kecil tetap tajam saat dirender langsung pada ukuran akhir.
    """
    if emblem is None:
        emblem = build_emblem(512)

    em = emblem.resize((190 * scale, 190 * scale), Image.LANCZOS)

    main_size = 112 * scale
    sub_size = 40 * scale
    sub_gap = 20 * scale

    font_main = _load_font(main_size, bold=True)
    font_sub = _load_font(sub_size, bold=False)

    text_main = "AgriUno"
    text_sub = "Manajemen Hasil Panen Pertanian Lokal"

    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    w_main = int(tmp.textlength(text_main, font=font_main))
    w_sub = int(tmp.textlength(text_sub, font=font_sub))

    gap = 40 * scale
    pad = 18 * scale

    # Tinggi blok teks = judul + jarak + sub-teks.
    text_block_h = main_size + sub_gap + sub_size
    height = max(em.height, text_block_h) + pad * 2
    total_w = em.width + gap + max(w_main, w_sub) + pad * 2

    out = Image.new("RGBA", (total_w, height), (0, 0, 0, 0))
    out.alpha_composite(em, (pad, (height - em.height) // 2))

    d = ImageDraw.Draw(out)
    tx = pad + em.width + gap
    ty = (height - text_block_h) // 2

    # Kata utama digambar pada lapisan tersendiri agar titik pada huruf
    # "i" dapat diwarnai ulang dengan warna aksen emas.
    main_layer = Image.new("RGBA", (total_w, height), (0, 0, 0, 0))
    ImageDraw.Draw(main_layer).text((tx, ty), text_main, font=font_main, fill=HIJAU_TUA)
    _recolor_dot(main_layer, tx, ty, text_main, font_main, EMAS)
    out.alpha_composite(main_layer)

    d.text(
        (tx + 4 * scale, ty + main_size + sub_gap),
        text_sub,
        font=font_sub,
        fill=(107, 114, 128),
    )

    out = out.resize((total_w // scale, height // scale), Image.LANCZOS)
    if width and out.width != width:
        ratio = width / out.width
        out = out.resize((width, int(out.height * ratio)), Image.LANCZOS)
    return out


def _recolor_dot(layer, origin_x, origin_y, text, font, color):
    """Mewarnai titik pada huruf "i" dengan warna aksen.

    Fungsi ini menggambar ulang titik yang sudah ada pada glif huruf
    "i" sehingga posisinya selalu tepat mengikuti bentuk huruf pada
    berkas font yang dipakai.
    """
    index = text.index("i")
    x0 = origin_x + int(
        ImageDraw.Draw(Image.new("RGB", (4, 4))).textlength(text[:index], font=font)
    )
    x1 = origin_x + int(
        ImageDraw.Draw(Image.new("RGB", (4, 4))).textlength(text[: index + 1], font=font)
    )

    pixels = layer.load()
    w, h = layer.size

    # Cari piksel paling atas pada pita kolom huruf "i".
    top_y = None
    for y in range(h):
        found = False
        for x in range(max(0, x0), min(w, x1 + 1)):
            if pixels[x, y][3] > 40:
                found = True
                break
        if found:
            top_y = y
            break

    if top_y is None:
        return

    # Warnai seluruh piksel pada run pertama (yaitu titik huruf "i").
    bottom_y = top_y
    for y in range(top_y, h):
        solid = False
        for x in range(max(0, x0), min(w, x1 + 1)):
            if pixels[x, y][3] > 40:
                solid = True
                break
        if not solid:
            break
        bottom_y = y

    for y in range(top_y, bottom_y + 1):
        for x in range(max(0, x0), min(w, x1 + 1)):
            r, g, b, a = pixels[x, y]
            if a > 40:
                pixels[x, y] = (color[0], color[1], color[2], a)


# ------------------------------------------------------------
# Frames animasi splash
# ------------------------------------------------------------
def build_splash_frames(emblem=None, steps=24, size=260, bg=(255, 255, 255)):
    """Membangun deretan frame PNG untuk animasi opening aplikasi.

    Setiap frame menampilkan emblem AgriUno dengan skala dan
    tingkat opasitas yang meningkat (ease-out cubic). Frame
    disimpan pada folder ``assets/anim`` dan diputar oleh
    ``views/splash_view.py`` menggunakan ``tkinter.PhotoImage``
    sehingga aplikasi tidak memerlukan Pillow saat dijalankan.
    """
    if emblem is None:
        emblem = build_emblem(512)

    anim_dir = os.path.join(ASSETS_DIR, "anim")
    os.makedirs(anim_dir, exist_ok=True)

    for stale in os.listdir(anim_dir):
        if stale.startswith("frame_") and stale.endswith(".png"):
            os.remove(os.path.join(anim_dir, stale))

    canvas_size = size
    paths = []
    for i in range(steps):
        t = i / max(1, steps - 1)
        ease = 1 - (1 - t) ** 3  # ease-out cubic
        scale = 0.68 + 0.32 * ease
        alpha = int(255 * ease)

        art = emblem.resize((int(canvas_size * scale), int(canvas_size * scale)), Image.LANCZOS)

        # Terapkan opasitas pada kanal alpha.
        if alpha < 255:
            a = art.getchannel("A").point(lambda v, k=alpha: int(v * k / 255))
            art.putalpha(a)

        frame = Image.new("RGBA", (canvas_size, canvas_size), bg + (255,))
        offset = ((canvas_size - art.width) // 2, (canvas_size - art.height) // 2)
        frame.alpha_composite(art, offset)

        path = os.path.join(anim_dir, "frame_%02d.png" % i)
        frame.convert("RGB").save(path)
        paths.append(path)

    return paths


# ------------------------------------------------------------
# Ikon .ico
# ------------------------------------------------------------
def build_ico(emblem, path):
    """Menyimpan emblem sebagai berkas .ico multi-ukuran."""
    ukuran = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    emblem.save(path, format="ICO", sizes=ukuran)


# ------------------------------------------------------------
# Entry point
# ------------------------------------------------------------
def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)

    print("Membangun emblem AgriUno ...")
    emblem = build_emblem(512)
    emblem_path = os.path.join(ASSETS_DIR, "logo_agriuno.png")
    emblem.save(emblem_path)
    print("  ->", emblem_path)

    print("Membangun wordmark AgriUno ...")
    wordmark = build_wordmark(emblem)
    wordmark_path = os.path.join(ASSETS_DIR, "logo_agriuno_wordmark.png")
    wordmark.save(wordmark_path)
    print("  ->", wordmark_path)

    # Versi kecil untuk jendela splash (tidak perlu penskalaan saat runtime).
    small = build_wordmark(emblem, width=300, scale=2)
    small_path = os.path.join(ASSETS_DIR, "logo_agriuno_wordmark_small.png")
    small.save(small_path)
    print("  ->", small_path)

    print("Membangun ikon .ico ...")
    ico_path = os.path.join(ASSETS_DIR, "logo_agriuno.ico")
    build_ico(emblem, ico_path)
    print("  ->", ico_path)

    print("Membangun frame animasi splash ...")
    frames = build_splash_frames(emblem)
    print("  ->", os.path.join(ASSETS_DIR, "anim"), "(%d frame)" % len(frames))

    print("Selesai.")


if __name__ == "__main__":
    main()
