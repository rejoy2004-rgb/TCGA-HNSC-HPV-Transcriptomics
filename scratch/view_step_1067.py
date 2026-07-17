import json
import os

log_file = r"C:\Users\rejoy\.gemini\antigravity\brain\67335ae6-040d-491e-adcb-9f3be36881ba\.system_generated\logs\transcript_full.jsonl"

if os.path.exists(log_file):
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                step = json.loads(line)
                if step.get("step_index") == 1067:
                    print(step.get('content'))
            except Exception as e:
                pass
else:
    print("Transcript log file not found.")
