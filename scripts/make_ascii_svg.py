from pathlib import Path
from PIL import Image
import numpy as np

# ============================================================
# CONFIG
# ============================================================

INPUT_IMAGE = Path("assets/profile-prepped.png")
OUTPUT_SVG = Path("assets/ascii.svg")

ASCII_WIDTH = 110

FONT_SIZE = 8
LINE_HEIGHT = 10

FONT = (
    "'JetBrains Mono',"
    "'Cascadia Code',"
    "'Fira Code',"
    "monospace"
)

BACKGROUND = "#0D1117"
TEXT = "#F3F4F6"
ACCENT = "#FF4D5A"
CARD = "#161B22"
BORDER = "#30363D"

PADDING = 28

TITLE = "sidharth@heyimsid:~$ whoami"

# brighter -> darker (your original ramp)
RAMP = (
    " "
    "."
    "`"
    "'"
    ":"
    "-"
    "="
    "+"
    "*"
    "o"
    "O"
    "#"
    "%"
    "@"
)

# ============================================================
# IMAGE
# ============================================================


def load_image():
    if not INPUT_IMAGE.exists():
        raise FileNotFoundError(f"Input image not found: {INPUT_IMAGE}")

    return Image.open(INPUT_IMAGE).convert("L")


def resize(img):
    w, h = img.size
    aspect = h / w
    height = int(ASCII_WIDTH * aspect * 0.55)

    return img.resize(
        (ASCII_WIDTH, height),
        Image.Resampling.LANCZOS,
    )


def normalize(img):
    arr = np.asarray(img).astype(np.float32)
    diff = arr.max() - arr.min()

    # Prevent division by zero if diff is 0
    if diff == 0:
        return img

    arr = ((arr - arr.min()) / diff) * 255
    return Image.fromarray(arr.astype(np.uint8))


# ============================================================
# ASCII
# ============================================================


def brightness_to_char(v):
    index = int((v / 255) * (len(RAMP) - 1))
    return RAMP[index]


def image_to_ascii(img):
    px = img.load()
    rows = []

    for y in range(img.height):
        line = []
        for x in range(img.width):
            value = px[x, y]
            line.append(brightness_to_char(value))
        rows.append("".join(line))

    return rows


# ============================================================
# SVG TERMINAL
# ============================================================

CHAR_WIDTH = FONT_SIZE * 0.62


def escape_html(text):
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace(" ", "&#160;")
    )


def terminal_size(lines):
    width = int(len(lines[0]) * CHAR_WIDTH + PADDING * 2)
    height = int(len(lines) * LINE_HEIGHT + PADDING * 2 + 55)
    return width, height


def svg_header(width, height):
    return f"""<svg
xmlns="http://www.w3.org/2000/svg"
width="{width}"
height="{height}"
viewBox="0 0 {width} {height}">

<style>

text{{
font-family:{FONT};
font-size:{FONT_SIZE}px;
fill:{TEXT};
xml:space:preserve;
}}

.title{{
font-size:13px;
font-weight:600;
}}

.line{{
opacity:0;
animation:fade .35s forwards;
}}

@keyframes fade{{
from{{
opacity:0;
transform:translateY(2px);
}}
to{{
opacity:1;
transform:translateY(0);
}}
}}

</style>
"""


def terminal_frame(width, height):
    return f"""
<rect
x="0"
y="0"
rx="14"
ry="14"
width="{width}"
height="{height}"
fill="{CARD}"
stroke="{BORDER}"
stroke-width="1"/>

<rect
x="0"
y="0"
rx="14"
ry="14"
width="{width}"
height="42"
fill="{BACKGROUND}"/>

<circle cx="22" cy="21" r="6" fill="#FF5F57"/>
<circle cx="42" cy="21" r="6" fill="#FEBC2E"/>
<circle cx="62" cy="21" r="6" fill="#28C840"/>

<text
x="90"
y="26"
class="title"
fill="{ACCENT}">
{TITLE}
</text>

<line
x1="0"
y1="42"
x2="{width}"
y2="42"
stroke="{BORDER}"/>
"""


def svg_ascii(lines):
    out = []
    y = 62
    delay = 0

    for row in lines:
        row = escape_html(row)
        out.append(f"""
<text
class="line"
x="{PADDING}"
y="{y}"
style="animation-delay:{delay:.2f}s">
{row}
</text>
""")
        y += LINE_HEIGHT
        delay += 0.03

    return "".join(out)


def svg_footer():
    return "</svg>"


# ============================================================
# MAIN EXECUTION
# ============================================================


def main():
    img = load_image()
    img = resize(img)
    img = normalize(img)

    lines = image_to_ascii(img)
    width, height = terminal_size(lines)

    svg_content = [
        svg_header(width, height),
        terminal_frame(width, height),
        svg_ascii(lines),
        svg_footer(),
    ]

    OUTPUT_SVG.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SVG.write_text("".join(svg_content), encoding="utf-8")
    print(f"ASCII SVG generated at: {OUTPUT_SVG}")


if __name__ == "__main__":
    main()