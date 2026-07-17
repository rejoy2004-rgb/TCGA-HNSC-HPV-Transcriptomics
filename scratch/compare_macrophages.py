import os
from PIL import Image
import numpy as np

brain_dir = r"C:\Users\rejoy\.gemini\antigravity\brain\67335ae6-040d-491e-adcb-9f3be36881ba"
intern_dir = r"C:\Users\rejoy\Documents\Intern_Project"

m2_brain_path = os.path.join(brain_dir, "media__1782411602735.png")
target_files = [
    "M2_Macrophage_Boxplot.png",
    "Revised_CD8_M2_Boxplot.png",
    "HNSC_CD8_M2_Ratio_Boxplot.png"
]

with Image.open(m2_brain_path) as m_img:
    m_img_rgb = m_img.convert("RGB")
    m_data = np.array(m_img_rgb)
    m_size = m_img_rgb.size
    print(f"Brain file: media__1782411602735.png, Size: {m_size}")

for tf in target_files:
    tf_path = os.path.join(intern_dir, tf)
    if os.path.exists(tf_path):
        with Image.open(tf_path) as t_img:
            t_resized = t_img.resize(m_size).convert("RGB")
            t_data = np.array(t_resized)
            
            # calculate difference
            diff = np.sum(np.abs(m_data.astype(float) - t_data.astype(float)))
            max_diff = m_data.size * 255.0
            sim = 1.0 - (diff / max_diff)
            print(f"  Comparison with {tf} ({os.path.getsize(tf_path)} bytes): Similarity = {sim*100:.2f}%")
    else:
        print(f"  {tf} not found in Intern_Project")
