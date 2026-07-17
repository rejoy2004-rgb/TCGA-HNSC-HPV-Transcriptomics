import os

intern_project_dir = r"C:\Users\rejoy\Documents\Intern_Project"
if os.path.exists(intern_project_dir):
    print("Files in Intern_Project:")
    for f in os.listdir(intern_project_dir):
        path = os.path.join(intern_project_dir, f)
        if os.path.isfile(path):
            print(f"  {f} ({os.path.getsize(path)} bytes)")
        else:
            print(f"  [Dir] {f}")
else:
    print(f"Directory {intern_project_dir} does not exist.")
