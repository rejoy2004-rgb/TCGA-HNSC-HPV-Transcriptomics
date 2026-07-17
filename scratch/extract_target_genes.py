import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

all_results_file = r"C:\Users\rejoy\Documents\Intern_Project\HNSC_DESeq2_All_Results.csv"
df = pd.read_csv(all_results_file).reset_index()

print("Columns:", df.columns.tolist())
print("First 10 rows:")
print(df.head(10).to_string())
