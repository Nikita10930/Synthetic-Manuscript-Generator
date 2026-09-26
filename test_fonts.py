from PIL import Image, ImageDraw, ImageFont
import re

# --------------------------------------------------
# Paths
# --------------------------------------------------

FONT_DEVANAGARI = "assets/fonts/NotoSansDevanagari[wdth,wght].ttf"
FONT_MODI = "assets/fonts/NotoSansModi-Regular.ttf"
FONT_SHARADA = "assets/fonts/Sharada-SVG.ttf"

SOURCE_DEVANAGARI = "data/source/devanagari.md"
SOURCE_MODI = "data/source/modi.md"
SOURCE_SHARADA = "data/source/sharada.md"


# --------------------------------------------------
# Find actual script text from source file
# --------------------------------------------------

def get_script_text(file_path, start, end):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Remove Markdown formatting
        line = re.sub(r"[*_#>`]", "", line)

        characters = [
            char for char in line
            if start <= ord(char) <= end
        ]

        if len(characters) >= 8:
            return line[:100]

    return "No suitable script text found"


# --------------------------------------------------
# Get real text
# --------------------------------------------------

devanagari_text = get_script_text(
    SOURCE_DEVANAGARI,
    0x0900,
    0x097F
)

modi_text = get_script_text(
    SOURCE_MODI,
    0x11600,
    0x1173F
)

sharada_text = get_script_text(
    SOURCE_SHARADA,
    0x11180,
    0x111DF
)


# --------------------------------------------------
# Load fonts
# --------------------------------------------------

font_dev = ImageFont.truetype(FONT_DEVANAGARI, 48)
font_modi = ImageFont.truetype(FONT_MODI, 48)
font_sharada = ImageFont.truetype(FONT_SHARADA, 48)


# --------------------------------------------------
# Create image
# --------------------------------------------------

img = Image.new("RGB", (1600, 900), "white")
draw = ImageDraw.Draw(img)


# --------------------------------------------------
# Devanagari
# --------------------------------------------------

draw.text(
    (50, 40),
    "REAL DEVANAGARI SOURCE TEXT",
    font=ImageFont.truetype(FONT_DEVANAGARI, 38),
    fill="black"
)

draw.text(
    (50, 110),
    devanagari_text,
    font=font_dev,
    fill="black"
)


# --------------------------------------------------
# Modi
# --------------------------------------------------

draw.text(
    (50, 300),
    "REAL MODI SOURCE TEXT",
    font=ImageFont.truetype(FONT_MODI, 38),
    fill="black"
)

draw.text(
    (50, 370),
    modi_text,
    font=font_modi,
    fill="black"
)


# --------------------------------------------------
# Sharada
# --------------------------------------------------

draw.text(
    (50, 560),
    "REAL SHARADA SOURCE TEXT",
    font=ImageFont.truetype(FONT_SHARADA, 38),
    fill="black"
)

draw.text(
    (50, 630),
    sharada_text,
    font=font_sharada,
    fill="black"
)


# --------------------------------------------------
# Save
# --------------------------------------------------

output_path = "samples/real_source_font_test.png"

img.save(output_path)

print("Real source font test completed!")
print(f"Saved at: {output_path}")

print("\nDetected source text:")
print("Devanagari:", devanagari_text)
print("Modi:", modi_text)
print("Sharada:", sharada_text)