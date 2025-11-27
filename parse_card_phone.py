from bs4 import BeautifulSoup
from pathlib import Path


html = Path("card.html").read_text(encoding="utf-8")
soup = BeautifulSoup(html, "html.parser")
card = soup.select_one("div.VkpGBb")
details = card.select_one("div.rllt__details")
rows = details.find_all("div", recursive=False)
phone_line = rows[-1].get_text(" ", strip=True)
phone = phone_line.split("·")[-1].strip()
print("Teléfono:", phone)

