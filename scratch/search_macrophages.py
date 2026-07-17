import os

intern_dir = r"C:\Users\rejoy\Documents\Intern_Project"
for root, dirs, files in os.walk(intern_dir):
    for f in files:
        if f.endswith((".py", ".R", ".txt", ".csv")):
            path = os.path.join(root, f)
            try:
                with open(path, "r", errors="ignore") as file:
                    content = file.read()
                    if "M0" in content or "M2" in content or "Macrophage" in content:
                        print(f"Found in {os.path.relpath(path, intern_dir)}")
            except Exception:
                pass
