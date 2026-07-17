import json
import os

log_file = r"C:\Users\rejoy\.gemini\antigravity\brain\67335ae6-040d-491e-adcb-9f3be36881ba\.system_generated\logs\transcript_full.jsonl"

if os.path.exists(log_file):
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                step = json.loads(line)
                idx = step.get("step_index")
                if 1055 <= idx <= 1075:
                    print(f"Step {idx} ({step.get('source')}):")
                    print(step.get('content')[:1000])
                    print("="*40)
            except Exception as e:
                pass
else:
    print("Transcript log file not found.")
