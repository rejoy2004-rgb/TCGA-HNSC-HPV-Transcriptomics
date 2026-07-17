import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('generate_docx.py', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if any(term in line for term in ['Table 5', 'Table 6', 'Table 7', 't5', 't6', 't7', 'table_5_data', 'table_6_data', 'table_7_data']):
            print(f"{i}: {line.strip()}")
