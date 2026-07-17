import os
from PIL import Image
import numpy as np

project_dir = r"C:\Users\rejoy\.gemini\antigravity\scratch\hnsc_docx_generator"
path = os.path.join(project_dir, "HNSC_HPV_PCA.png")

if os.path.exists(path):
    size_bytes = os.path.getsize(path)
    try:
        with Image.open(path) as img:
            data = np.array(img.convert("L"))
            std = np.std(data)
            print(f"File: HNSC_HPV_PCA.png, Size: {img.size}, Format: {img.format}, Size Bytes: {size_bytes}, StdDev: {std:.2f}")
    except Exception as e:
        print(f"File: HNSC_HPV_PCA.png, ERROR: {e}")
else:
    print("File not found")
