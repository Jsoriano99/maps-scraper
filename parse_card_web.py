from bs4 import BeautifulSoup
from pathlib import Path


html = Path("card.html").read_text(encoding="utf-8")
soup = BeautifulSoup(html, "html.parser")
card = soup.select_one("div.VkpGBb")
for a in card.find_all("a", href=True):
    if "Sitio web" in a.get_text():
        print("Web:", a["href"])
        break

