with open("generate_docx.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

line_numbers = [408, 501, 516, 664, 681, 688, 759, 777, 784, 804, 963]

for ln in line_numbers:
    print(f"--- Line {ln} ---")
    start = max(0, ln - 4)
    end = min(len(lines), ln + 4)
    for idx in range(start, end):
        print(f"  {idx+1}: {lines[idx].rstrip()}")
