with open('generate_docx.py', 'rb') as f:
    content = f.read()

# find position of '# Save document'
idx = content.find(b'# Save document')
if idx != -1:
    print(repr(content[idx:idx+250]))
else:
    print("Not found")
