import pandas as pd
import numpy as np

cibersort_file = r"C:\Users\rejoy\Documents\Intern_Project\CIBERSORTx_Job14_Results.csv"
clinical_file = r"C:\Users\rejoy\Documents\Intern_Project\HNSC_HPV_status.csv"

# Load files
cb = pd.read_csv(cibersort_file)
clin = pd.read_csv(clinical_file)

# Extract first 15 characters of sample ID
cb["sample_id_15"] = cb["Mixture"].str[:15]
clin["sample_id_15"] = clin["Sample ID"].str[:15]

# Merge dataframes
merged = pd.merge(cb, clin, on="sample_id_15", how="inner")

print(f"Merged cohort size: {len(merged)} samples")
print(merged["HPV Status"].value_counts())

# Columns of interest
nk_col = "NK cells resting"
cd4_col = "T cells CD4 memory resting"

for col in [nk_col, cd4_col]:
    if col in merged.columns:
        print(f"\nCell type: {col}")
        pos_median = merged[merged["HPV Status"] == "positive"][col].median()
        neg_median = merged[merged["HPV Status"] == "negative"][col].median()
        print(f"  HPV-positive Median: {pos_median:.4f}")
        print(f"  HPV-negative Median: {neg_median:.4f}")
    else:
        # Search for columns that contain the name
        match_cols = [c for c in cb.columns if "NK" in c or "CD4" in c or "resting" in c]
        print(f"\nWarning: Column '{col}' not found. Potential matches: {match_cols}")
