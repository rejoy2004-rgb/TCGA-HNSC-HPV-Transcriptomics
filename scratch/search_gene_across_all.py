import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

search_dir = r"C:\Users\rejoy\Documents\Intern_Project"
target_genes = ["IGHA1", "TACSTD2"]

for root, dirs, files in os.walk(search_dir):
    for file in files:
        if file.endswith(('.csv', '.txt', '.tsv', '.R', '.Rhistory')):
            fpath = os.path.join(root, file)
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f, 1):
                        for gene in target_genes:
                            if gene in line:
                                print(f"Found {gene} in {fpath}:{i} -> {line.strip()[:150]}")
            except Exception as e:
                pass
