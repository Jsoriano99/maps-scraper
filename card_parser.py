from bs4 import BeautifulSoup

def parse_card_html(card_html: str) -> dict:
    soup = BeautifulSoup(card_html, "html.parser")
    card = soup.select_one("div.VkpGBb")
    def safe_text(parent, selector):
        el = parent.select_one(selector) if parent else None
        return el.get_text(strip=True) if el else None
    name = safe_text(card, "div.dbg0pd span.OSrXXb")
    details = card.select_one("div.rllt__details") if card else None
    rows = details.find_all("div", recursive=False) if details else []
    phone_line = rows[-1].get_text(" ", strip=True) if rows else None
    phone = phone_line.split("·")[-1].strip() if phone_line and "·" in phone_line else phone_line
    web = next((a["href"] for a in card.find_all("a", href=True) if "Sitio web" in a.get_text()), None) if card else None

    if web is None:
        estado_web = "no_web"
        prioridad = "alta"
    else:
        estado_web = "desconocido"
        prioridad = "baja"

    return {
        "nombre": name,
        "telefono": phone,
        "web": web,
        "estado_web": estado_web,
        "prioridad": prioridad,
    }
    

