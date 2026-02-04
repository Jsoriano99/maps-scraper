from bs4 import BeautifulSoup
from card_parser import parse_card_html

def main():
    with open("sample_results.html", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("div.VkpGBb")

    print(f"Encontradas {len(cards)} tarjetas en el HTML local.")
    for card in cards[:5]:  # probamos solo las 5 primeras
        lead = parse_card_html(str(card))
        print(lead)

if __name__ == "__main__":
    main()

