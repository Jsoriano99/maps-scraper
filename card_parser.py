# Leer tarjeta de negocio
import re
from bs4 import BeautifulSoup

def parse_card_html(card_html: str) -> dict:

    # Pasamos string HTML y "motor" interprete HTML (convierte a DOM)
    soup = BeautifulSoup(card_html, "html.parser")

    # 1.- Aseguramos que estamos en el div correcto
    card = soup.select_one("div.VkpGBb")
    def safe_text(parent, selector):
        el = parent.select_one(selector) if parent else None
        return el.get_text(strip=True) if el else None
    name = safe_text(card, "div.dbg0pd span.OSrXXb")
    details = card.select_one("div.rllt__details") if card else None
    rows = details.find_all("div", recursive=False) if details else []
    phone = None

    # 1) Intento “viejo”: última fila del bloque de detalles
    if rows:
        phone_line = rows[-1].get_text(" ", strip=True)
        if "·" in phone_line:
            candidate = phone_line.split("·")[-1].strip()
            if any(ch.isdigit() for ch in candidate):
                phone = candidate

    # 2) Fallback: buscar cualquier texto con al menos 9 dígitos en toda la tarjeta
    if phone is None:
        for text in card.stripped_strings:
            digits_only = re.sub(r"\D", "", text)
            if len(digits_only) >= 9:
                phone = text.strip()
                break
                
    web = next((a["href"] for a in card.find_all("a", href=True) if "Sitio web" in a.get_text()), None) if card else None

    if web is None:
        estado_web = "sin_web"
        prioridad = "muy_alta"
    else:
        web_lower = web.lower()
        if "facebook.com" in web_lower or "instagram.com" in web_lower or "linktr.ee" in web_lower:
            estado_web = "solo_red_social"
            prioridad = "alta"
        else:
            estado_web = "web_presente"
            prioridad = "baja"


    return {
        "nombre": name,
        "telefono": phone,
        "web": web,
        "estado_web": estado_web,
        "prioridad": prioridad,
    }
    

