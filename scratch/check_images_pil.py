import os
from PIL import Image
import numpy as np

project_dir = r"C:\Users\rejoy\.gemini\antigravity\scratch\hnsc_docx_generator"
files = [
    "HNSC_HPV_GO_Upregulated.png",
    "HNSC_HPV_KEGG_Downregulated.png",
    "HNSC_HPV_GSEA_dotplot.png",
    "HNSC_HPV_GO_Downregulated.png",
    "HNSC_HPV_KEGG_Upregulated.png",
    "HNSC_HPV_GSEA_ridgeplot.png"
]

for f in files:
    path = os.path.join(project_dir, f)
    if os.path.exists(path):
        size_bytes = os.path.getsize(path)
        try:
            with Image.open(path) as img:
                # check if image has variation (not just solid color)
                data = np.array(img.convert("L"))
                std = np.std(data)
                print(f"File: {f}, Size: {img.size}, Format: {img.format}, Size Bytes: {size_bytes}, StdDev of L: {std:.2f}")
        except Exception as e:
            print(f"File: {f}, Size Bytes: {size_bytes}, ERROR: {e}")
    else:
        print(f"File: {f} NOT FOUND in workspace")
