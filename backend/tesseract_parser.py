import io
import pytesseract
from PIL import Image, ImageOps


def extract_text(contents):
    image = Image.open(io.BytesIO(contents))
    image = ImageOps.exif_transpose(image)
    image = image.convert("L")
    image = ImageOps.autocontrast(image)

    if image.width < 1500:
        image = image.resize((image.width * 2, image.height * 2), Image.Resampling.LANCZOS)

    raw_text = pytesseract.image_to_string(image, config="--psm 6")
    text_lines = raw_text.split("\n")
    return [line.strip() for line in text_lines if line.strip() != ""]