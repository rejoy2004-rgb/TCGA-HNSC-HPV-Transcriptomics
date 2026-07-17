import os
from PIL import Image

intern_dir = r"C:\Users\rejoy\Documents\Intern_Project"
heatmaps = [
    "HNSC_HPV_Immune_Heatmap.png",
    "Revised_Immune_Heatmap.png",
    "HNSC_HPV_Significant_Immune_Heatmap.png",
    r"HNSC\HNSC_HPV_Heatmap.png"
]

for hm in heatmaps:
    path = os.path.join(intern_dir, hm)
    if os.path.exists(path):
        size_bytes = os.path.getsize(path)
        if size_bytes > 0:
            with Image.open(path) as img:
                print(f"File: {hm}, Size: {img.size}, Format: {img.format}, Size Bytes: {size_bytes}")
        else:
            print(f"File: {hm}, Size Bytes: 0 (Empty)")
    else:
        print(f"File: {hm} not found")
