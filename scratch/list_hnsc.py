import os

hnsc_dir = r"C:\Users\rejoy\Documents\Intern_Project\HNSC"
if os.path.exists(hnsc_dir):
    print("Files in HNSC:")
    for f in os.listdir(hnsc_dir):
        print(f"  {f}")
else:
    print("HNSC directory does not exist.")
