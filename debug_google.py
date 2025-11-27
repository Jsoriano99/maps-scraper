from pathlib import Path
import requests
from urllib.parse import quote_plus

q = "fontaneros cordoba"
url = f"https://www.google.com/search?q={quote_plus(q)}&tbm=lcl"
headers = {"User-Agent": "Mozilla/5.0", "Accept-Language": "es-ES,es;q=0.9"}
resp = requests.get(url, headers=headers)
print("Status:", resp.status_code)
Path("google_raw.html").write_text(resp.text, encoding="utf-8")

