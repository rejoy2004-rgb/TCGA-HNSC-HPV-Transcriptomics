import sys

sys.stdout.reconfigure(encoding='utf-8')

r_script_path = r"C:\Users\rejoy\Documents\Intern_Project\HPV_HNSC_Revision.R"
with open(r_script_path, 'r', encoding='utf-8') as f:
    for i in range(100):
        line = f.readline()
        if not line:
            break
        print(f"{i+1}: {line.strip()}")
