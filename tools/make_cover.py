import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = 3000
img = Image.new("RGB", (S, S), "#0b1a2b")
d = ImageDraw.Draw(img)
# vertical gradient
for y in range(S):
    t = y / S
    r, g, b = int(11 + 10*t), int(26 + 30*t), int(43 + 25*t)
    d.line([(0, y), (S, y)], fill=(r, g, b))
# rain streaks
random.seed(206)
rain = Image.new("RGBA", (S, S), (0, 0, 0, 0))
rd = ImageDraw.Draw(rain)
for _ in range(900):
    x, y = random.randint(-200, S), random.randint(-200, S)
    L = random.randint(60, 220)
    rd.line([(x, y), (x + L*0.25, y + L)], fill=(170, 200, 230, random.randint(25, 70)), width=random.randint(3, 6))
img.paste(rain, (0, 0), rain)
d = ImageDraw.Draw(img)
bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def center(text, y, size, fill):
    f = ImageFont.truetype(bold, size)
    w = d.textlength(text, font=f)
    d.text(((S - w) / 2, y), text, font=f, fill=fill)
# skyline silhouette at bottom
base = 2520
d.rectangle([0, base, S, S], fill="#06101b")
random.seed(98)
x = 0
while x < S:
    w = random.randint(90, 220); h = random.randint(80, 380)
    d.rectangle([x, base - h, x + w, base], fill="#06101b"); x += w
# needle
nx = 2150
d.polygon([(nx-18, base), (nx+18, base), (nx+8, base-520), (nx-8, base-520)], fill="#06101b")
d.ellipse([nx-120, base-600, nx+120, base-520], fill="#06101b")
d.polygon([(nx-6, base-600), (nx+6, base-600), (nx, base-760)], fill="#06101b")
# title
center("RAIN CITY", 520, 400, "#ffffff")
center("HOMERS", 960, 560, "#69be28")
d.rectangle([600, 1640, 2400, 1660], fill="#ffffff")
center("ZAGS  ·  HAWKS  ·  M'S  ·  DAWGS", 1740, 150, "#cfe3f5")
center("with Cal & Rusty", 2000, 120, "#9fb6cc")
img.save("site/cover.png", optimize=True)
img.resize((600, 600)).save("site/cover_preview.png")
print("ok")
