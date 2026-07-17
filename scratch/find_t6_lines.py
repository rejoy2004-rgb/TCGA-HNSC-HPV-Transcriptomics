import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('generate_docx.py', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if any(term in line for term in ['table_6_data', 'Table 6', 'p_t6_title', 'r_t6_title', 'p_t6_space', 't6']):
            print(f"{i}: {line.strip()}")
