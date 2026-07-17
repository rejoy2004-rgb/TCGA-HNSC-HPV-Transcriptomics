import pandas as pd

try:
    df_full = pd.read_csv("data_clinical_patient_full.txt", sep="\t", skiprows=4)
    df_pub = pd.read_csv("data_clinical_patient_pub.txt", sep="\t", skiprows=4)
    merged = pd.merge(df_pub, df_full, on="PATIENT_ID", how="left")
    
    merged['AGE'] = pd.to_numeric(merged['AGE'], errors='coerce')
    age_pos = merged[merged['HPV_STATUS'] == 'HPV+']['AGE'].dropna()
    age_neg = merged[merged['HPV_STATUS'] == 'HPV-']['AGE'].dropna()
    
    print(f"HPV+ Age range: {age_pos.min():.0f} - {age_pos.max():.0f}")
    print(f"HPV- Age range: {age_neg.min():.0f} - {age_neg.max():.0f}")
except Exception as e:
    print(e)
