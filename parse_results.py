from pathlib import Path
from bs4 import BeautifulSoup
from card_parser import parse_card_html

html = Path("results.html").read_text(encoding="utf-8")
soup = BeautifulSoup(html, "html.parser")
cards = soup.select("div.VkpGBb")
for card in cards:
    print(parse_card_html(str(card)))

