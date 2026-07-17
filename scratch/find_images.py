import sys

with open("generate_docx.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

output_lines = []
for i, line in enumerate(lines):
    if any(x in line.lower() for x in [".png", "add_picture", "figure", "table"]):
        safe_line = line.strip().encode('ascii', errors='replace').decode('ascii')
        output_lines.append(f"Line {i+1}: {safe_line}")

with open("scratch/find_images_output.txt", "w", encoding="utf-8") as out:
    out.write("\n".join(output_lines))

print(f"Successfully wrote {len(output_lines)} matching lines to scratch/find_images_output.txt")
