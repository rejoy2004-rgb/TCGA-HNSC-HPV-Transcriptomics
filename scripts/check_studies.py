import urllib.request
import json

url = "https://www.cbioportal.org/api/studies"
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        studies = json.loads(response.read().decode('utf-8'))
        
    hnsc_studies = [s for s in studies if 'hnsc' in s.get('studyId', '').lower()]
    for s in hnsc_studies:
        print(s.get('studyId'), "|", s.get('name'))
        
except Exception as e:
    print("Error:", e)
