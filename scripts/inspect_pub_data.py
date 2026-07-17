import pandas as pd

try:
    df_pat = pd.read_csv("data_clinical_patient.txt", sep="\t", skiprows=4)
    df_sam = pd.read_csv("data_clinical_sample.txt", sep="\t", skiprows=4)
    
    print("Patient file columns:", list(df_pat.columns))
    print(df_pat.head(5))
    
    print("\nSample file columns:", list(df_sam.columns))
    print(df_sam.head(5))
    
except Exception as e:
    print("Error:", e)
