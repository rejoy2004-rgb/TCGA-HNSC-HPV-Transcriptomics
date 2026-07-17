import urllib.request
import os

patient_url = "https://media.githubusercontent.com/media/cBioPortal/datahub/master/public/hnsc_tcga_pub/data_clinical_patient.txt"
sample_url = "https://media.githubusercontent.com/media/cBioPortal/datahub/master/public/hnsc_tcga_pub/data_clinical_sample.txt"

headers = {'User-Agent': 'Mozilla/5.0'}

try:
    print("Downloading data_clinical_patient.txt for hnsc_tcga_pub...")
    req = urllib.request.Request(patient_url, headers=headers)
    with urllib.request.urlopen(req) as response:
        patient_data = response.read().decode('utf-8')
    with open("data_clinical_patient.txt", "w", encoding="utf-8") as f:
        f.write(patient_data)
        
    print("Downloading data_clinical_sample.txt for hnsc_tcga_pub...")
    req = urllib.request.Request(sample_url, headers=headers)
    with urllib.request.urlopen(req) as response:
        sample_data = response.read().decode('utf-8')
    with open("data_clinical_sample.txt", "w", encoding="utf-8") as f:
        f.write(sample_data)
        
    print("Downloads completed successfully!")
    
    # Read the data to print the shape
    import pandas as pd
    df_pat = pd.read_csv("data_clinical_patient.txt", sep="\t", skiprows=4)
    print("Patient clinical data shape:", df_pat.shape)
    
except Exception as e:
    print("Error:", e)
