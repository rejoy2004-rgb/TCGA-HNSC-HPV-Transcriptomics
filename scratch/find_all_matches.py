import os
from PIL import Image
import numpy as np

brain_dir = r"C:\Users\rejoy\.gemini\antigravity\brain\67335ae6-040d-491e-adcb-9f3be36881ba"
intern_dir = r"C:\Users\rejoy\Documents\Intern_Project"

brain_files = [f for f in os.listdir(brain_dir) if f.startswith("media__") and f.endswith((".png", ".jpg"))]
intern_files = [f for f in os.listdir(intern_dir) if f.endswith((".png", ".jpg"))]

print("Establishing mappings...")

for bf in sorted(brain_files):
    bp = os.path.join(brain_dir, bf)
    if os.path.getsize(bp) == 0:
        continue
    try:
        with Image.open(bp) as b_img:
            b_img_rgb = b_img.convert("RGB")
            b_data = np.array(b_img_rgb)
            b_size = b_img_rgb.size
    except Exception as e:
        continue
        
    best_matches = []
    for ipf in intern_files:
        ipp = os.path.join(intern_dir, ipf)
        if os.path.getsize(ipp) == 0:
            continue
        try:
            with Image.open(ipp) as i_img:
                i_resized = i_img.resize(b_size).convert("RGB")
                i_data = np.array(i_resized)
                diff = np.sum(np.abs(b_data.astype(float) - i_data.astype(float)))
                max_diff = b_data.size * 255.0
                sim = 1.0 - (diff / max_diff)
                if sim > 0.85:
                    best_matches.append((ipf, sim))
        except Exception:
            pass
            
    if best_matches:
        # sort by similarity descending
        best_matches.sort(key=lambda x: x[1], reverse=True)
        top = best_matches[0]
        print(f"Brain: {bf} (size {b_size}) -> Top Match: {top[0]} ({top[1]*100:.2f}%)")
    else:
        print(f"Brain: {bf} (size {b_size}) -> NO MATCH (>85% similarity)")
