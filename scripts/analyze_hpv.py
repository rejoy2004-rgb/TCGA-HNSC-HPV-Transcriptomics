import pandas as pd
try:
    df_sample = pd.read_csv("data_clinical_sample.txt", sep="\t", skiprows=4)
    print("Sample clinical dataframe loaded. Shape:", df_sample.shape)
    
    # Check all columns for 'hpv' or 'viral'
    hpv_cols = [c for c in df_sample.columns if 'hpv' in c.lower() or 'viral' in c.lower()]
    print("\nHPV-related columns in sample file:", hpv_cols)
    
    if len(hpv_cols) > 0:
        for c in hpv_cols:
            print(f"\nValue counts for {c}:")
            print(df_sample[c].value_counts(dropna=False))
            
    # Print preview of first 30 columns
    print("\nSample attributes list:", list(df_sample.columns)[:30])
except Exception as e:
    print("Error:", e)
