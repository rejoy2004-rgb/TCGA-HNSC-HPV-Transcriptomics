import json
import os

log_file = r"C:\Users\rejoy\.gemini\antigravity\brain\67335ae6-040d-491e-adcb-9f3be36881ba\.system_generated\logs\transcript.jsonl"

if os.path.exists(log_file):
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                step = json.loads(line)
                if step.get("type") == "USER_INPUT":
                    print(f"Step {step.get('step_index')}: {step.get('content')[:300]}...")
            except Exception as e:
                pass
else:
    print("Transcript log file not found.")
