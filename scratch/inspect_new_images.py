import os
from PIL import Image

brain_dir = r"C:\Users\rejoy\.gemini\antigravity\brain\67335ae6-040d-491e-adcb-9f3be36881ba"
new_files = [
    "media__1782411540027.png",
    "media__1782411554525.png",
    "media__1782411588013.png",
    "media__1782411602735.png",
    "media__1782411633474.png"
]

for filename in new_files:
    path = os.path.join(brain_dir, filename)
    if os.path.exists(path):
        with Image.open(path) as img:
            print(f"File: {filename}, Format: {img.format}, Size: {img.size}, Mode: {img.mode}, File Size: {os.path.getsize(path)} bytes")
    else:
        print(f"File {filename} not found")
