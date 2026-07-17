import os
import datetime

brain_dir = r"C:\Users\rejoy\.gemini\antigravity\brain\67335ae6-040d-491e-adcb-9f3be36881ba"
print("Scanning brain directory for new files:")
for f in os.listdir(brain_dir):
    path = os.path.join(brain_dir, f)
    if os.path.isfile(path):
        mtime = os.path.getmtime(path)
        mtime_dt = datetime.datetime.fromtimestamp(mtime, datetime.timezone.utc)
        print(f"  {f}: Size {os.path.getsize(path)} bytes, Modified: {mtime_dt.isoformat()}")
