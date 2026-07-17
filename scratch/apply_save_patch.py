with open('generate_docx.py', 'rb') as f:
    content = f.read()

target = b'# Save document\r\n    output_filename = "Immune_Landscape_HNSC.docx"\r\n    doc.save(output_filename)\r\n    print(f"Document created successfully: {os.path.abspath(output_filename)}")'

replacement = b'# Save document\r\n    output_filename = "Immune_Landscape_HNSC.docx"\r\n    try:\r\n        doc.save(output_filename)\r\n        print(f"Document created successfully: {os.path.abspath(output_filename)}")\r\n    except PermissionError:\r\n        alt_filename = "Immune_Landscape_HNSC_Updated.docx"\r\n        doc.save(alt_filename)\r\n        print(f"WARNING: \'{output_filename}\' is locked (likely open in Microsoft Word).")\r\n        print(f"Alternative document created successfully: {os.path.abspath(alt_filename)}")'

if target in content:
    new_content = content.replace(target, replacement)
    with open('generate_docx.py', 'wb') as f:
        f.write(new_content)
    print("Patch applied successfully via binary replace!")
else:
    print("Target byte sequence not found in generate_docx.py")
