"""
Color derivation for number detail pages.

Background color: number's decimal digits treated as a base-10 integer, reduced
mod 0x1000000 (16,777,216), then formatted as #RRGGBB hex. This covers the full
24-bit color space (#000000–#FFFFFF). Streaming modulo keeps computation O(n)
with small intermediate values — no bigint overhead even for 10,000-digit inputs.

Text color: background color with hue rotated 180° in HSV space, plus S-floor
and V-inversion for readable contrast on dark/grey backgrounds.
"""


def number_to_bg_hex(canonical: str) -> str:
    """Convert a canonical number string to a background #RRGGBB color.

    Strips non-digit characters, interprets the remaining digits as a decimal
    integer, and maps them into the full 24-bit color space via mod 0x1000000.
    """
    digits = "".join(c for c in canonical if c.isdigit())
    if not digits:
        digits = "0"
    n = 0
    for d in digits:
        n = (n * 10 + int(d)) % 0x1000000
    return f"#{n:06X}"


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _rgb_to_hsv(r: int, g: int, b: int) -> tuple[float, float, float]:
    r_p = r / 255.0
    g_p = g / 255.0
    b_p = b / 255.0

    c_max = max(r_p, g_p, b_p)
    c_min = min(r_p, g_p, b_p)
    delta = c_max - c_min

    v = c_max
    s = 0.0 if c_max == 0.0 else delta / c_max

    if delta == 0.0:
        h = 0.0
    elif c_max == r_p:
        h = 60.0 * (((g_p - b_p) / delta) % 6)
    elif c_max == g_p:
        h = 60.0 * ((b_p - r_p) / delta + 2)
    else:
        h = 60.0 * ((r_p - g_p) / delta + 4)

    if h < 0:
        h += 360.0

    return h, s, v


def _hsv_to_rgb(h: float, s: float, v: float) -> tuple[int, int, int]:
    c = v * s
    x = c * (1 - abs((h / 60.0) % 2 - 1))
    m = v - c

    if 0 <= h < 60:
        r_p, g_p, b_p = c, x, 0.0
    elif 60 <= h < 120:
        r_p, g_p, b_p = x, c, 0.0
    elif 120 <= h < 180:
        r_p, g_p, b_p = 0.0, c, x
    elif 180 <= h < 240:
        r_p, g_p, b_p = 0.0, x, c
    elif 240 <= h < 300:
        r_p, g_p, b_p = x, 0.0, c
    else:
        r_p, g_p, b_p = c, 0.0, x

    return (
        int(round((r_p + m) * 255)),
        int(round((g_p + m) * 255)),
        int(round((b_p + m) * 255)),
    )


def get_number_colors(canonical: str) -> tuple[str, str]:
    """Return (bg_hex, text_hex) for a canonical number string."""
    bg_hex = number_to_bg_hex(canonical)
    r, g, b = _hex_to_rgb(bg_hex)
    h, s, v = _rgb_to_hsv(r, g, b)
    h_shifted = (h + 180.0) % 360.0
    s_text = max(s, 0.5)                          # floor S so grey bgs produce chromatic text
    v_text = max(0.15, min(0.95, 1.0 - v))        # invert V; clamp to avoid pure black/white
    r2, g2, b2 = _hsv_to_rgb(h_shifted, s_text, v_text)
    text_hex = f"#{r2:02X}{g2:02X}{b2:02X}"
    return bg_hex, text_hex
