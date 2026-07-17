import json
import os

log_file = r"C:\Users\rejoy\.gemini\antigravity\brain\67335ae6-040d-491e-adcb-9f3be36881ba\.system_generated\logs\transcript_full.jsonl"

if os.path.exists(log_file):
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                step = json.loads(line)
                content = step.get("content", "")
                if "Heatmap" in content or "heatmap" in content:
                    # Print context of match
                    print(f"Step {step.get('step_index')} ({step.get('source')}):")
                    for text_line in content.split("\n"):
                        if "heatmap" in text_line.lower():
                            print(f"  {text_line.strip()[:120]}")
            except Exception as e:
                pass
else:
    print("Transcript log file not found.")
