import os
import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Search for any CSV file in the workspace or parent directory that contains DESeq2 results
csv_files = []
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.csv'):
            csv_files.append(os.path.join(root, file))

print("Found CSV files:")
for f in csv_files:
    print(f" - {f}")

genes_of_interest = ["IGKC", "IGHA1", "MS4A1", "CD79A", "S100A7", "TACSTD2"]

for fpath in csv_files:
    try:
        df = pd.read_csv(fpath)
        # Check if there is a column for gene or symbol
        gene_col = None
        for col in df.columns:
            if col.lower() in ['gene', 'symbol', 'genesymbol', 'gene_symbol', 'id', 'row.names', 'unnamed: 0']:
                gene_col = col
                break
        if gene_col is not None:
            # Check if any genes of interest are in this column
            subset = df[df[gene_col].astype(str).isin(genes_of_interest)]
            if not subset.empty:
                print(f"\nFound matches in {fpath}:")
                print(subset.to_string())
    except Exception as e:
        pass
