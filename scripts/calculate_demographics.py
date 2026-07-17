import urllib.request
import pandas as pd
import numpy as np
from scipy import stats

headers = {'User-Agent': 'Mozilla/5.0'}

# URLs
full_pat_url = "https://media.githubusercontent.com/media/cBioPortal/datahub/master/public/hnsc_tcga/data_clinical_patient.txt"
pub_pat_url = "https://media.githubusercontent.com/media/cBioPortal/datahub/master/public/hnsc_tcga_pub/data_clinical_patient.txt"

try:
    print("Downloading full patient dataset...")
    req = urllib.request.Request(full_pat_url, headers=headers)
    with urllib.request.urlopen(req) as response:
        full_data = response.read().decode('utf-8')
    with open("data_clinical_patient_full.txt", "w", encoding="utf-8") as f:
        f.write(full_data)
        
    print("Downloading publication patient dataset...")
    req = urllib.request.Request(pub_pat_url, headers=headers)
    with urllib.request.urlopen(req) as response:
        pub_data = response.read().decode('utf-8')
    with open("data_clinical_patient_pub.txt", "w", encoding="utf-8") as f:
        f.write(pub_data)
        
    print("Files downloaded successfully!")
    
    # Load into Pandas
    df_full = pd.read_csv("data_clinical_patient_full.txt", sep="\t", skiprows=4)
    df_pub = pd.read_csv("data_clinical_patient_pub.txt", sep="\t", skiprows=4)
    
    print(f"Full dataset patient count: {df_full.shape[0]}")
    print(f"Publication dataset patient count: {df_pub.shape[0]}")
    
    # Merge datasets
    merged = pd.merge(df_pub, df_full, on="PATIENT_ID", how="left")
    print(f"Merged dataset shape: {merged.shape}")
    
    # Check HPV_STATUS values
    print("HPV status in merged cohort:")
    print(merged['HPV_STATUS'].value_counts(dropna=False))
    
    # Let's write a function to calculate statistics for each variable
    hpv_pos = merged[merged['HPV_STATUS'] == 'HPV+']
    hpv_neg = merged[merged['HPV_STATUS'] == 'HPV-']
    
    print(f"\nHPV+ count: {len(hpv_pos)}")
    print(f"HPV- count: {len(hpv_neg)}")
    
    # 1. AGE
    # Convert to numeric
    merged['AGE'] = pd.to_numeric(merged['AGE'], errors='coerce')
    age_pos = hpv_pos['AGE'].dropna().astype(float)
    age_neg = hpv_neg['AGE'].dropna().astype(float)
    
    print("\n--- AGE ---")
    print(f"HPV+ Age: Mean={age_pos.mean():.1f}, SD={age_pos.std():.1f}, Median={age_pos.median():.1f}")
    print(f"HPV- Age: Mean={age_neg.mean():.1f}, SD={age_neg.std():.1f}, Median={age_neg.median():.1f}")
    # t-test P-value
    t_stat, p_age = stats.ttest_ind(age_pos, age_neg, equal_var=False)
    print(f"Age t-test P-value: {p_age:.4f}")
    
    # 2. GENDER (SEX)
    print("\n--- GENDER ---")
    gender_table = pd.crosstab(merged['SEX'], merged['HPV_STATUS'])
    print(gender_table)
    chi2, p_gender, dof, ex = stats.chi2_contingency(gender_table)
    print(f"Gender Chi2 P-value: {p_gender:.4f}")
    
    # 3. STAGE (AJCC_PATHOLOGIC_TUMOR_STAGE)
    # Simplify stage for clean presentation: Stage I/II vs Stage III/IV
    print("\n--- STAGE ---")
    stage_table_raw = pd.crosstab(merged['AJCC_PATHOLOGIC_TUMOR_STAGE'], merged['HPV_STATUS'])
    print(stage_table_raw)
    
    # Clean staging (group into I, II, III, IV)
    def clean_stage(val):
        if pd.isna(val) or val == '[Not Available]':
            return 'Unknown'
        val = str(val).strip()
        if 'Stage I' == val:
            return 'Stage I'
        elif 'Stage II' == val:
            return 'Stage II'
        elif 'Stage III' == val:
            return 'Stage III'
        elif 'Stage IV' in val:
            return 'Stage IV'
        return 'Unknown'
        
    merged['stage_clean'] = merged['AJCC_PATHOLOGIC_TUMOR_STAGE'].apply(clean_stage)
    stage_table = pd.crosstab(merged['stage_clean'], merged['HPV_STATUS'])
    print("\nCleaned stage table:")
    print(stage_table)
    # Exclude Unknown for Chi-square
    stage_table_chi = stage_table.drop('Unknown', errors='ignore')
    chi2_stage, p_stage, dof, ex = stats.chi2_contingency(stage_table_chi)
    print(f"Stage Chi2 P-value (excluding Unknown): {p_stage:.4f}")
    
    # 4. SMOKING STATUS (TOBACCO_SMOKING_HISTORY_INDICATOR)
    print("\n--- SMOKING ---")
    smoking_table_raw = pd.crosstab(merged['TOBACCO_SMOKING_HISTORY_INDICATOR'], merged['HPV_STATUS'])
    print(smoking_table_raw)
    
    def clean_smoking(val):
        if pd.isna(val) or val in ['[Not Available]', '[Unknown]']:
            return 'Unknown'
        val = str(val).strip()
        if 'never' in val.lower():
            return 'Never Smoker'
        elif 'current' in val.lower() or 'smoker' in val.lower():
            return 'Ever Smoker'
        return 'Unknown'
        
    merged['smoking_clean'] = merged['TOBACCO_SMOKING_HISTORY_INDICATOR'].apply(clean_smoking)
    smoking_table = pd.crosstab(merged['smoking_clean'], merged['HPV_STATUS'])
    print("\nCleaned smoking table:")
    print(smoking_table)
    # Chi-square excluding Unknown
    smoking_table_chi = smoking_table.drop('Unknown', errors='ignore')
    chi2_smoke, p_smoke, dof, ex = stats.chi2_contingency(smoking_table_chi)
    print(f"Smoking Chi2 P-value (excluding Unknown): {p_smoke:.4f}")
    
    # 5. PRIMARY SITE (PRIMARY_SITE_PATIENT)
    print("\n--- PRIMARY SITE ---")
    site_table_raw = pd.crosstab(merged['PRIMARY_SITE_PATIENT'], merged['HPV_STATUS'])
    print(site_table_raw)
    
    def clean_site(val):
        if pd.isna(val) or val == '[Not Available]':
            return 'Unknown'
        val = str(val).strip().lower()
        if 'larynx' in val:
            return 'Larynx'
        elif 'tongue' in val or 'oral cavity' in val or 'lip' in val or 'floor of mouth' in val or 'buccal' in val or 'gum' in val or 'palate' in val:
            return 'Oral Cavity'
        elif 'oropharynx' in val or 'tonsil' in val or 'base of tongue' in val:
            return 'Oropharynx'
        elif 'hypopharynx' in val:
            return 'Hypopharynx'
        return 'Other/Unknown'
        
    merged['site_clean'] = merged['PRIMARY_SITE_PATIENT'].apply(clean_site)
    site_table = pd.crosstab(merged['site_clean'], merged['HPV_STATUS'])
    print("\nCleaned site table:")
    print(site_table)
    site_table_chi = site_table.drop('Unknown', errors='ignore')
    chi2_site, p_site, dof, ex = stats.chi2_contingency(site_table_chi)
    print(f"Primary Site Chi2 P-value (excluding Unknown): {p_site:.4f}")
    
    # 6. SURVIVAL STATUS (OS_STATUS)
    print("\n--- SURVIVAL ---")
    survival_table = pd.crosstab(merged['OS_STATUS_x'], merged['HPV_STATUS']) # OS_STATUS_x from pub file
    print(survival_table)
    chi2_surv, p_surv, dof, ex = stats.chi2_contingency(survival_table)
    print(f"Survival Chi2 P-value: {p_surv:.4f}")

except Exception as e:
    print("Error:", e)
