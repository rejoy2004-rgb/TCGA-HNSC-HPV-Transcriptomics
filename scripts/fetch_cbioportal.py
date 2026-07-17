import urllib.request
import json
import pandas as pd
import numpy as np

# We can query the cBioPortal API
# Let's try to get the clinical data for the TCGA HNSC study (hnsc_tcga)
url = "https://www.cbioportal.org/api/studies/hnsc_tcga/clinical-data?projection=DETAILED"
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    print("Fetching clinical data from cBioPortal...")
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        
    print(f"Fetched {len(data)} clinical data records.")
    
    # We will build a DataFrame where each row is a patient and columns are clinical attributes
    # Clinical data in cBioPortal is returned as a list of records:
    # {"patientId": "...", "sampleId": "...", "clinicalAttributeId": "...", "value": "..."}
    df_list = []
    patient_data = {}
    for record in data:
        pid = record.get('patientId')
        attr = record.get('clinicalAttributeId')
        val = record.get('value')
        if pid not in patient_data:
            patient_data[pid] = {}
        patient_data[pid][attr] = val
        
    df = pd.DataFrame.from_dict(patient_data, orient='index')
    print("DataFrame shape:", df.shape)
    
    # Let's see what columns are in the DataFrame related to HPV status
    hpv_cols = [c for c in df.columns if 'hpv' in c.lower()]
    print("HPV columns found:", hpv_cols)
    
    # Print a small preview of the columns
    print("Attributes list:", list(df.columns)[:30])
    
    # Save the dataframe to a CSV file to inspect it
    df.to_csv("cbioportal_hnsc_clinical.csv")
    print("Saved to cbioportal_hnsc_clinical.csv")

except Exception as e:
    print("Error:", e)
