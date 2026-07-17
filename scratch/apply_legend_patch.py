with open('generate_docx.py', 'rb') as f:
    content = f.read()

target = b'All genes show HR < 1.0, indicating that higher expression is associated with reduced risk and better survival.'
replacement = b'Although statistically significant, all hazard ratios were close to unity, indicating relatively modest effect sizes.'

if target in content:
    content = content.replace(target, replacement)
    with open('generate_docx.py', 'wb') as f:
        f.write(content)
    print("Legend patch applied successfully!")
else:
    # Try with normal string in case of single backslashes or formatting
    print("Target byte sequence not found, searching string-based...")
    with open('generate_docx.py', 'r', encoding='utf-8') as f:
        text = f.read()
    if 'All genes show HR < 1.0' in text:
        text = text.replace('All genes show HR < 1.0, indicating that higher expression is associated with reduced risk and better survival.',
                            'Although statistically significant, all hazard ratios were close to unity, indicating relatively modest effect sizes.')
        with open('generate_docx.py', 'w', encoding='utf-8') as f:
            f.write(text)
        print("Legend patch applied successfully (string)!")
    else:
        print("Target string not found in text.")
