import urllib.request
from bs4 import BeautifulSoup

url = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6040854/"
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        html = response.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    print("Page Title:", soup.title.string if soup.title else "No Title")
    print("First 1000 characters of text:")
    print(soup.get_text()[:1000])
except Exception as e:
    print("Error:", e)
