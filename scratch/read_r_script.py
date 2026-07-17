import sys

sys.stdout.reconfigure(encoding='utf-8')

r_script_path = r"C:\Users\rejoy\Documents\Intern_Project\HPV_HNSC_Revision.R"
try:
    with open(r_script_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Search for DESeq2 export and gene mapping
    import re
    matches = re.finditer(r'res|write|csv|mapping|symbol', code, re.IGNORECASE)
    printed = set()
    for m in matches:
        start = max(0, m.start() - 100)
        end = min(len(code), m.end() + 150)
        chunk = code[start:end].strip()
        if chunk not in printed:
            print(f"Match context:\n{chunk}\n{'-'*40}")
            printed.add(chunk)
except Exception as e:
    print("Error reading R script:", e)
