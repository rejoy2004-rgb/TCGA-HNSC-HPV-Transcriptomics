import os
from PIL import Image
import numpy as np

brain_dir = r"C:\Users\rejoy\.gemini\antigravity\brain\67335ae6-040d-491e-adcb-9f3be36881ba"
intern_dir = r"C:\Users\rejoy\Documents\Intern_Project"

brain_files = [f for f in os.listdir(brain_dir) if f.startswith("media__") and f.endswith(".png")]
intern_files = [f for f in os.listdir(intern_dir) if f.endswith(".png")]

print(f"Comparing {len(brain_files)} brain files with {len(intern_files)} intern project files:")

for bf in sorted(brain_files):
    bp = os.path.join(brain_dir, bf)
    b_size = os.path.getsize(bp)
    
    # Try to open brain image
    try:
        with Image.open(bp) as b_img:
            b_data = np.array(b_img)
    except Exception as e:
        print(f"Error reading brain file {bf}: {e}")
        continue
        
    matches = []
    for ipf in intern_files:
        ipp = os.path.join(intern_dir, ipf)
        if os.path.getsize(ipp) == 0:
            continue
        try:
            with Image.open(ipp) as i_img:
                if i_img.size == b_img.size:
                    i_data = np.array(i_img)
                    if b_data.shape == i_data.shape:
                        diff = np.sum(np.abs(b_data.astype(float) - i_data.astype(float)))
                        if diff == 0:
                            matches.append((ipf, 1.0))
                        else:
                            # calculate similarity
                            max_diff = b_data.size * 255.0
                            sim = 1.0 - (diff / max_diff)
                            if sim > 0.95:
                                matches.append((ipf, sim))
        except Exception as e:
            pass
            
    if matches:
        match_str = ", ".join([f"{name} ({sim*100:.2f}% sim)" for name, sim in matches])
        print(f"Brain: {bf} ({b_size} bytes, size {b_img.size}) matches: {match_str}")
    else:
        print(f"Brain: {bf} ({b_size} bytes, size {b_img.size}) has NO match")
