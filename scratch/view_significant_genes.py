import pandas as pd
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

sig_file = r"C:\Users\rejoy\Documents\Intern_Project\HNSC_DESeq2_Significant_Genes.csv"
if os.path.exists(sig_file):
    df = pd.read_csv(sig_file)
    print("Columns in Significant Genes:", df.columns.tolist())
    print(df.head(5).to_string())
else:
    print("Significant genes file does not exist at", sig_file)
