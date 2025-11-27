import requests; from bs4 import BeautifulSoup; from urllib.parse import quote_plus
from card_parser import parse_card_html


q = "fontaneros cordoba"
url = f"https://www.google.com/search?q={quote_plus(q)}&tbm=lcl"
headers = {"User-Agent":"Mozilla/5.0","Accept-Language":"es-ES,es;q=0.9"}
html = requests.get(url, headers=headers).text
soup = BeautifulSoup(html, "html.parser")
for card in soup.select("div.VkpGBb")[:25]: print(parse_card_html(str(card)))

