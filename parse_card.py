from bs4 import BeautifulSoup
from pathlib import Path


html = Path("card.html").read_text(encoding="utf-8")
soup = BeautifulSoup(html, "html.parser")
card = soup.select_one("div.VkpGBb")
name = card.select_one("div.dbg0pd span.OSrXXb").get_text(strip=True)
print("Nombre:", name)

