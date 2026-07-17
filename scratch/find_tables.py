import re

with open('generate_docx.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Find all Table titles and print their context
table_titles = re.findall(r'Table \d+\..*?(?=\")', code)
for title in table_titles:
    print(f"Table Title: {title}")

# Let's search for table headings and where they are placed
for m in re.finditer(r'Table \d+', code):
    start = max(0, m.start() - 100)
    end = min(len(code), m.end() + 150)
    print(f"\nContext around {m.group()}:")
    print(code[start:end].replace('\n', ' [NL] '))
