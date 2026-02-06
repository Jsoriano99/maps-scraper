from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from urllib.parse import quote_plus
from datetime import date
import csv
import time, random
import os
from card_parser import parse_card_html
import re
import requests

# Consulta de Google Maps Local
QUERY = "cerrajeros cordoba"

def extract_email_from_website(url: str) -> str:
    """
    Intenta extraer un correo electrónico de la página web proporcionada.
    Devuelve el primer email encontrado o una cadena vacía si no se encuentra ninguno.
    Se excluyen enlaces a redes sociales y servicios que normalmente no contienen el email de contacto.
    """
    if not url:
        return ""
    # Ignorar enlaces de redes sociales o plataformas genéricas
    blacklisted = ["facebook.com", "instagram.com", "twitter.com", "linkedin.com",
                   "youtube.com", "linktr.ee", "canva.com"]
    if any(host in url for host in blacklisted):
        return ""
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code != 200:
            return ""
        html = resp.text
        # Buscar enlace mailto:
        mailto_match = re.search(r'href=["\']mailto:([^"\']+)', html, re.IGNORECASE)
        if mailto_match:
            email = mailto_match.group(1)
            # quitar parámetros después del ?
            email = email.split("?")[0]
            return email.strip()
        # Buscar patrones de email en el HTML
        emails = re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', html)
        return emails[0] if emails else ""
    except Exception:
        return ""


def scrape_page(page, limit_per_page=25):
    page.wait_for_selector("div.VkpGBb", timeout=10000)
    cards = page.query_selector_all("div.VkpGBb")

    leads = []
    for c in cards[:limit_per_page]:
        card_html = c.evaluate("el => el.outerHTML")
        lead = parse_card_html(card_html)
        # Obtener correo electrónico desde la web si la hay
        email = extract_email_from_website(lead.get("web", ""))
        lead["email"] = email
        leads.append(lead)
        # pequeña pausa por si más adelante hacemos cosas extra aquí
        time.sleep(random.uniform(0.3, 0.8))

    return leads


def build_filename(query: str) -> str:
    q = query.lower().strip()
    parts = [p for p in q.split() if p]

    if len(parts) >= 2:
        city = parts[-1]                # última palabra = ciudad
        job = " ".join(parts[:-1])      # resto = oficio
    else:
        city = "desconocida"
        job = q or "sin_query"

    job_slug = job.replace(" ", "_")
    city_slug = city.replace(" ", "_")
    today = date.today().isoformat()

    folder = os.path.join("data", job_slug, city_slug)
    os.makedirs(folder, exist_ok=True)

    filename = f"leads_{today}.csv"
    return os.path.join(folder, filename)


def main():
    url = f"https://www.google.com/search?q={quote_plus(QUERY)}&tbm=lcl"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(3000)

        # Intentar aceptar cookies (pantalla "Antes de ir a Google")
        try:
            page.get_by_role("button", name="Aceptar todo").click(timeout=5000)
            page.wait_for_timeout(3000)
        except PlaywrightTimeoutError:
            # Si no sale el botón, seguimos como si nada
            pass

        MAX_PAGES = 6  # scrapear las primeras seis páginas de resultados

        all_leads = []

        for page_index in range(MAX_PAGES):
            print(f"\n--- Página {page_index + 1} ---")
            leads = scrape_page(page)
            for lead in leads:
                print(lead)
            all_leads.extend(leads)

            # Intentar pasar a la página siguiente
            try:
                next_link = page.get_by_role("link", name="Siguiente")
                if not next_link.is_visible():
                    break
                # pausa entre página y página para no ir tan bot
                time.sleep(random.uniform(4.0, 7.0))
                next_link.click(timeout=5000)
                page.wait_for_timeout(4000)
            except PlaywrightTimeoutError:
                break
            except Exception:
                break

        browser.close()

        if all_leads:
            # Eliminar duplicados: usar teléfono como clave principal, o web si no hay teléfono, o nombre como último recurso
            unique_map = {}
            for lead in all_leads:
                key = lead.get("telefono") or lead.get("web") or lead.get("nombre")
                if key and key not in unique_map:
                    unique_map[key] = lead
            unique_leads = list(unique_map.values())
            filename = build_filename(QUERY)
            fieldnames = ["nombre", "telefono", "web", "estado_web", "prioridad", "email"]
            with open(filename, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(unique_leads)
            print(f"\nGuardados {len(unique_leads)} leads en {filename}")
        else:
            print("No se han encontrado leads.")


if __name__ == "__main__":
    main()