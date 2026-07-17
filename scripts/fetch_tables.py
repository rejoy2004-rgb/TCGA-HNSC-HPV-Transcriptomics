import urllib.request
import re
from bs4 import BeautifulSoup

url = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6040854/"
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        html = response.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables.")
    
    for i, table in enumerate(tables):
        print(f"\n--- TABLE {i+1} ---")
        # Print first few rows or header
        rows = table.find_all('tr')
        for r_idx, row in enumerate(rows[:15]): # print first 15 rows
            cols = [col.get_text(strip=True) for col in row.find_all(['td', 'th'])]
            print(cols)
except Exception as e:
    print("Error:", e)
