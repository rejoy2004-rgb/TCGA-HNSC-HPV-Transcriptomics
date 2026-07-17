import os
try:
    import pytesseract
    has_tesseract = True
except ImportError:
    has_tesseract = False

from PIL import Image

brain_dir = r"C:\Users\rejoy\.gemini\antigravity\brain\67335ae6-040d-491e-adcb-9f3be36881ba"
new_files = [
    "media__1782411540027.png",
    "media__1782411554525.png",
    "media__1782411588013.png",
    "media__1782411602735.png",
    "media__1782411633474.png"
]

print(f"Has pytesseract: {has_tesseract}")

for filename in new_files:
    path = os.path.join(brain_dir, filename)
    if os.path.exists(path):
        with Image.open(path) as img:
            # Crop the top portion where titles usually reside (e.g., top 100 pixels)
            title_crop = img.crop((10, 5, img.width - 10, 80))
            if has_tesseract:
                try:
                    text = pytesseract.image_to_string(title_crop).strip()
                    print(f"{filename} Top Crop Text:\n{text}")
                    print("-" * 20)
                except Exception as e:
                    print(f"Error OCR-ing {filename}: {e}")
            else:
                # print some statistics about the crop to distinguish
                pixels = list(title_crop.getdata())
                non_white = sum(1 for p in pixels if sum(p[:3])/3 < 240)
                print(f"{filename} (size {img.size}): non-white pixels in title crop = {non_white}")
