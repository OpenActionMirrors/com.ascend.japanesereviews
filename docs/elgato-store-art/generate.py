"""Generate the three Elgato Marketplace gallery images for the Japanese Reviews plugin.

Outputs three 1920x960 PNGs into this directory:
  01-hero.png        - Title card with plugin icon, name, tagline, and supported sites
  02-in-action.png   - Stream Deck buttons mockup showing live review counts
  03-features.png    - Supported sites grid + key features

Run:
  python docs/elgato-store-art/generate.py
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Brand palette sampled from the plugin icon
NAVY_OUTER = (26, 26, 46)     # #1A1A2E
NAVY_INNER = (22, 33, 62)     # #16213E
NAVY_DEEP  = (15, 52, 96)     # #0F3460
PINK       = (233, 69, 96)    # #E94560
WHITE      = (255, 255, 255)
LIGHT      = (220, 222, 230)
MUTED      = (155, 160, 178)

W, H = 1920, 960

ROOT = Path(__file__).resolve().parents[2]
ICONS = ROOT / "com.ascend.japanesereviews.sdPlugin" / "static" / "imgs"
OUT = Path(__file__).resolve().parent

F_BOLD  = "C:/Windows/Fonts/segoeuib.ttf"
F_SEMI  = "C:/Windows/Fonts/seguisb.ttf"
F_REG   = "C:/Windows/Fonts/segoeui.ttf"
F_LIGHT = "C:/Windows/Fonts/segoeuil.ttf"
F_TREB  = "C:/Windows/Fonts/trebucbd.ttf"  # Trebuchet MS Bold (matches plugin badge)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def load_rgba(p: Path) -> Image.Image:
    return Image.open(p).convert("RGBA")


def text_size(d: ImageDraw.ImageDraw, s: str, f: ImageFont.FreeTypeFont):
    bbox = d.textbbox((0, 0), s, font=f)
    return bbox[2] - bbox[0], bbox[3] - bbox[1], bbox


def draw_text_centered(d: ImageDraw.ImageDraw, cx: int, cy: int,
                       s: str, f: ImageFont.FreeTypeFont, fill):
    w, h, b = text_size(d, s, f)
    d.text((cx - w / 2 - b[0], cy - h / 2 - b[1]), s, font=f, fill=fill)


def gradient_bg(w: int, h: int, top, bottom) -> Image.Image:
    """Vertical linear gradient."""
    img = Image.new("RGB", (w, h), top)
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        for x in range(w):
            px[x, y] = (r, g, b)
    return img


def diamond_outline(layer: Image.Image, cx: int, cy: int, size: int,
                    color, width: int):
    d = ImageDraw.Draw(layer)
    pts = [(cx, cy - size), (cx + size, cy),
           (cx, cy + size), (cx - size, cy),
           (cx, cy - size)]
    d.line(pts, fill=color, width=width, joint="curve")


def add_decor_diamonds(img: Image.Image, specs):
    """specs: list of (cx, cy, size, alpha)."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    for cx, cy, sz, a in specs:
        diamond_outline(layer, cx, cy, sz, PINK + (a,), 4)
    return Image.alpha_composite(img.convert("RGBA"), layer)


def draw_glyph(d: ImageDraw.ImageDraw, kind: str, cx: int, cy: int, r: int):
    """Draw a small white vector glyph centered at (cx, cy) inside a circle of radius r."""
    if kind == "clock":
        # Clock face
        rr = int(r * 0.55)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=WHITE, width=4)
        # Tick at top
        d.line([cx, cy - rr, cx, cy - rr + 5], fill=WHITE, width=4)
        # Hour hand (up)
        d.line([cx, cy, cx, cy - int(rr * 0.55)], fill=WHITE, width=4)
        # Minute hand (right)
        d.line([cx, cy, cx + int(rr * 0.7), cy], fill=WHITE, width=4)
    elif kind == "arrow":
        # Diagonal arrow up-right
        rr = int(r * 0.55)
        x1, y1 = cx - rr, cy + rr
        x2, y2 = cx + rr, cy - rr
        d.line([x1, y1, x2, y2], fill=WHITE, width=5)
        head = int(r * 0.4)
        d.polygon([(x2, y2), (x2 - head, y2 + 2), (x2 - 2, y2 + head)], fill=WHITE)
    elif kind == "gear":
        # Three vertical sliders
        rr = int(r * 0.55)
        for off in (-rr, 0, rr):
            x = cx + off // 2 if False else cx + (off)
        # Two horizontal sliders for clarity
        slider_w = int(r * 1.0)
        for i, y_off in enumerate([-int(r * 0.5), 0, int(r * 0.5)]):
            y = cy + y_off
            d.line([cx - slider_w // 2, y, cx + slider_w // 2, y], fill=WHITE, width=3)
            knob_x = cx + (-slider_w // 4 if i % 2 == 0 else slider_w // 4)
            d.ellipse([knob_x - 5, y - 5, knob_x + 5, y + 5], fill=WHITE)
    elif kind == "badge":
        # Counter pill with mini number-bars
        rr = int(r * 0.6)
        d.rounded_rectangle([cx - rr, cy - rr // 2,
                             cx + rr, cy + rr // 2],
                            radius=rr // 2, fill=WHITE)
        # Two short dark "digit" bars inside
        bar_w = max(2, rr // 5)
        bar_h = rr // 2
        for i, off in enumerate([-rr // 3, rr // 3]):
            d.rectangle([cx + off - bar_w // 2, cy - bar_h // 2,
                         cx + off + bar_w // 2, cy + bar_h // 2],
                        fill=PINK)


def render_review_button(icon_path: Path, count: str, btn_size: int) -> Image.Image:
    """Render a Stream Deck button: black square + scaled site icon + count overlay
    matching the plugin's actual rendering style."""
    btn = Image.new("RGBA", (btn_size, btn_size), (0, 0, 0, 0))
    d = ImageDraw.Draw(btn)
    # Stream Deck key face: very dark, slight rounded corner
    d.rounded_rectangle([0, 0, btn_size - 1, btn_size - 1], radius=22,
                        fill=(8, 8, 12, 255))

    icon = load_rgba(icon_path).resize((btn_size, btn_size), Image.LANCZOS)
    btn = Image.alpha_composite(btn, icon)

    # Count overlay - matches rendering.ts which renders against the 72x72 icon.
    # The plugin loads `bunpro.png` (@1x), not `bunpro@2x.png`, so scale from 72.
    scale = btn_size / 72
    char_w = 12 * scale
    pad = 4 * scale
    box_w = char_w * len(count) + pad
    box_h = 26 * scale
    box_x = btn_size / 2 - box_w / 2
    box_y = 24 * scale

    overlay = Image.new("RGBA", btn.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle(
        [box_x - 4 * scale, box_y - 2 * scale,
         box_x + box_w + 4 * scale, box_y + box_h + 2 * scale],
        radius=int(6 * scale), fill=(0, 0, 0, 220))
    overlay = overlay.filter(__import__("PIL.ImageFilter", fromlist=["GaussianBlur"])
                             .GaussianBlur(radius=int(4 * scale)))
    btn = Image.alpha_composite(btn, overlay)

    d = ImageDraw.Draw(btn)
    f = font(F_TREB, int(22 * scale))
    # Match the plugin's text placement: drawn at boxY+21 (font baseline) in source.
    # In PIL we use top-anchor, so the equivalent y is boxY for the visual top.
    tw, _, b = text_size(d, count, f)
    d.text((btn_size / 2 - tw / 2 - b[0], box_y - b[1] + 2 * scale),
           count, font=f, fill=WHITE)
    return btn


# ---------------------------------------------------------------------------
# Image 1 — Hero
# ---------------------------------------------------------------------------
def make_hero():
    img = gradient_bg(W, H, (18, 18, 36), NAVY_OUTER).convert("RGBA")
    img = add_decor_diamonds(img, [
        (180, 130, 80, 40),
        (1780, 110, 55, 45),
        (1820, 850, 95, 35),
        (140, 880, 60, 35),
    ])

    plugin_icon = load_rgba(ICONS / "pluginIcon@2x.png").resize((440, 440), Image.LANCZOS)
    img.paste(plugin_icon, (140, 130), plugin_icon)

    d = ImageDraw.Draw(img)

    f_title = font(F_BOLD, 130)
    f_sub   = font(F_LIGHT, 50)

    title_x = 640
    d.text((title_x, 170), "Japanese", font=f_title, fill=WHITE)
    d.text((title_x, 320), "Reviews", font=f_title, fill=WHITE)

    # Pink accent bar
    d.rectangle([title_x, 480, title_x + 220, 488], fill=PINK)

    d.text((title_x, 520), "Live review counts for your favorite", font=f_sub, fill=LIGHT)
    d.text((title_x, 585), "Japanese learning sites — on every key.", font=f_sub, fill=LIGHT)

    # Site logos row
    sites = [
        ("Bunpro",   ICONS / "actions" / "review" / "bunpro@2x.png"),
        ("WaniKani", ICONS / "actions" / "review" / "wanikani@2x.png"),
        ("MaruMori", ICONS / "actions" / "review" / "marumori@2x.png"),
        ("Kitsun",   ICONS / "actions" / "review" / "kitsun@2x.png"),
    ]
    icon_size = 110
    name_font = font(F_SEMI, 36)

    n = len(sites)
    margin = 220
    row_w = W - 2 * margin
    slot = row_w / n
    y = 760

    for i, (name, path) in enumerate(sites):
        cx = margin + slot * i + slot / 2
        ic = load_rgba(path).resize((icon_size, icon_size), Image.LANCZOS)
        img.paste(ic, (int(cx - icon_size / 2), y), ic)
        nw, _, b = text_size(d, name, name_font)
        d.text((cx - nw / 2 - b[0], y + icon_size + 16), name, font=name_font, fill=WHITE)

    img.convert("RGB").save(OUT / "01-hero.png", "PNG", optimize=True)
    print("saved 01-hero.png")


# ---------------------------------------------------------------------------
# Image 2 — In Action
# ---------------------------------------------------------------------------
def make_in_action():
    img = gradient_bg(W, H, (14, 14, 28), NAVY_OUTER).convert("RGBA")
    img = add_decor_diamonds(img, [
        (130, 880, 70, 30),
        (1820, 110, 60, 35),
    ])

    d = ImageDraw.Draw(img)

    f_title = font(F_BOLD, 76)
    f_sub   = font(F_LIGHT, 38)

    draw_text_centered(d, W // 2, 130, "Pending reviews at a glance", f_title, WHITE)
    draw_text_centered(d, W // 2, 215, "Counts refresh automatically every 10 minutes.", f_sub, LIGHT)

    # Pink accent under title
    d.rectangle([W // 2 - 110, 178, W // 2 + 110, 186], fill=PINK)

    # Stream Deck row
    sites = [
        ("bunpro",   "146"),
        ("marumori", "48"),
        ("wanikani", "406"),
        ("kitsun",   "27"),
    ]
    btn = 240
    gap = 36
    total = len(sites) * btn + (len(sites) - 1) * gap

    base_pad_x = 70
    base_pad_y = 60
    base_w = total + base_pad_x * 2
    base_h = btn + base_pad_y * 2
    base_x = (W - base_w) // 2
    base_y = 350

    base = Image.new("RGBA", (base_w, base_h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(base)
    bd.rounded_rectangle([0, 0, base_w - 1, base_h - 1], radius=28,
                         fill=(34, 34, 40, 255), outline=(60, 62, 72, 255), width=3)
    # subtle inner highlight
    bd.rounded_rectangle([4, 4, base_w - 5, base_h - 5], radius=24,
                         outline=(50, 52, 62, 255), width=1)
    img.paste(base, (base_x, base_y), base)

    btn_y = base_y + base_pad_y
    start_x = base_x + base_pad_x
    for i, (key, count) in enumerate(sites):
        x = start_x + i * (btn + gap)
        b = render_review_button(ICONS / "actions" / "review" / f"{key}@2x.png",
                                 count, btn)
        img.paste(b, (x, btn_y), b)

    # Caption row under buttons
    f_cap = font(F_REG, 30)
    caption_y = base_y + base_h + 60
    captions = ["Bunpro", "MaruMori", "WaniKani", "Kitsun"]
    for i, name in enumerate(captions):
        cx = start_x + i * (btn + gap) + btn / 2
        nw, _, bb = text_size(d, name, f_cap)
        d.text((cx - nw / 2 - bb[0], caption_y), name, font=f_cap, fill=MUTED)

    # Click hint
    f_hint = font(F_LIGHT, 32)
    draw_text_centered(d, W // 2, caption_y + 90,
                       "Press any key to open that site's reviews in your browser.",
                       f_hint, LIGHT)

    img.convert("RGB").save(OUT / "02-in-action.png", "PNG", optimize=True)
    print("saved 02-in-action.png")


# ---------------------------------------------------------------------------
# Image 3 — Supported sites & features
# ---------------------------------------------------------------------------
def make_features():
    img = gradient_bg(W, H, (18, 18, 36), NAVY_OUTER).convert("RGBA")
    img = add_decor_diamonds(img, [
        (140, 130, 65, 35),
        (1800, 870, 80, 35),
    ])

    d = ImageDraw.Draw(img)

    f_title = font(F_BOLD, 70)
    draw_text_centered(d, W // 2, 110, "Track every site you study on", f_title, WHITE)

    # 4 site cards
    sites = [
        ("Bunpro",   "Grammar & Vocab",  "API key",           ICONS / "actions" / "review" / "bunpro@2x.png"),
        ("WaniKani", "Kanji",            "API key",           ICONS / "actions" / "review" / "wanikani@2x.png"),
        ("MaruMori", "Grammar & Vocab",  "API key",           ICONS / "actions" / "review" / "marumori@2x.png"),
        ("Kitsun",   "Grammar & Vocab",  "Email & Password",  ICONS / "actions" / "review" / "kitsun@2x.png"),
    ]
    n = len(sites)
    card_w = 380
    card_h = 400
    gap = 32
    total_w = n * card_w + (n - 1) * gap
    start_x = (W - total_w) // 2
    y = 230

    f_name = font(F_BOLD, 42)
    f_kind = font(F_REG, 26)
    f_auth_lbl = font(F_LIGHT, 20)
    f_auth_val = font(F_SEMI, 22)

    for i, (name, kind, auth, path) in enumerate(sites):
        x = start_x + i * (card_w + gap)
        card = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
        cd = ImageDraw.Draw(card)
        cd.rounded_rectangle([0, 0, card_w - 1, card_h - 1], radius=22,
                             fill=NAVY_INNER + (255,),
                             outline=(58, 62, 88, 255), width=2)

        # Icon
        ic_size = 150
        ic = load_rgba(path).resize((ic_size, ic_size), Image.LANCZOS)
        card.paste(ic, ((card_w - ic_size) // 2, 44), ic)

        # Name
        nw, _, b = text_size(cd, name, f_name)
        cd.text(((card_w - nw) / 2 - b[0], 218), name, font=f_name, fill=WHITE)

        # Kind (subtitle)
        kw, _, b = text_size(cd, kind, f_kind)
        cd.text(((card_w - kw) / 2 - b[0], 278), kind, font=f_kind, fill=LIGHT)

        # Auth row at bottom
        auth_label = "Auth"
        lw, _, b = text_size(cd, auth_label, f_auth_lbl)
        cd.text(((card_w - lw) / 2 - b[0], 326), auth_label, font=f_auth_lbl, fill=MUTED)
        vw, _, b = text_size(cd, auth, f_auth_val)
        cd.text(((card_w - vw) / 2 - b[0], 352), auth, font=f_auth_val, fill=PINK)

        img.paste(card, (x, y), card)

    # Feature strip at bottom
    feat_y = 720
    features = [
        ("clock",  "Auto-refresh",     "Every 10 minutes"),
        ("arrow",  "One-click open",   "Jump to site's reviews"),
        ("gear",   "Configurable",     "Per-button site choice"),
        ("badge",  "Live counter",     "Always up to date"),
    ]
    f_feat_h = font(F_BOLD, 30)
    f_feat_b = font(F_LIGHT, 24)

    fn = len(features)
    fcard_w = 380
    fcard_h = 150
    f_gap = 32
    f_total_w = fn * fcard_w + (fn - 1) * f_gap
    f_start_x = (W - f_total_w) // 2

    for i, (glyph, h_text, b_text) in enumerate(features):
        x = f_start_x + i * (fcard_w + f_gap)
        c = Image.new("RGBA", (fcard_w, fcard_h), (0, 0, 0, 0))
        cdr = ImageDraw.Draw(c)
        cdr.rounded_rectangle([0, 0, fcard_w - 1, fcard_h - 1], radius=18,
                              fill=(30, 32, 52, 230),
                              outline=(58, 62, 88, 255), width=2)
        # Glyph circle
        cx0, cy0 = 80, fcard_h // 2
        rr = 36
        cdr.ellipse([cx0 - rr, cy0 - rr, cx0 + rr, cy0 + rr], fill=PINK)
        draw_glyph(cdr, glyph, cx0, cy0, rr)

        # Heading
        cdr.text((140, 38), h_text, font=f_feat_h, fill=WHITE)
        cdr.text((140, 80), b_text, font=f_feat_b, fill=LIGHT)

        img.paste(c, (x, feat_y), c)

    img.convert("RGB").save(OUT / "03-features.png", "PNG", optimize=True)
    print("saved 03-features.png")


if __name__ == "__main__":
    make_hero()
    make_in_action()
    make_features()
