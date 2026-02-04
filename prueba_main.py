from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from urllib.parse import quote_plus
from datetime import date
import csv
import time, random
import os
from card_parser import parse_card_html

DEFAULT_QUERY = "fontaneros cordoba"


def scrape_page(page, limit_per_page=25):
    page.wait_for_selector("div.VkpGBb", timeout=10000)
    cards = page.query_selector_all("div.VkpGBb")

    leads = []
    for c in cards[:limit_per_page]:
        card_html = c.evaluate("el => el.outerHTML")
        lead = parse_card_html(card_html)
        leads.append(lead)
        time.sleep(random.uniform(0.3, 0.8))

    return leads


def build_filename(query: str) -> str:
    q = query.lower().strip()
    parts = [p for p in q.split() if p]

    if len(parts) >= 2:
        city = parts[-1]
        job = " ".join(parts[:-1])
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


def run_scraper(query: str):
    url = f"https://www.google.com/search?q={quote_plus(query)}&tbm=lcl"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(3000)

        # Intentar aceptar cookies
        try:
            page.get_by_role("button", name="Aceptar todo").click(timeout=5000)
            page.wait_for_timeout(3000)
        except PlaywrightTimeoutError:
            pass

        MAX_PAGES = 2
        all_leads = []

        for page_index in range(MAX_PAGES):
            print(f"\n--- Página {page_index + 1} ---")
            leads = scrape_page(page)
            for lead in leads:
                print(lead)
            all_leads.extend(leads)

            try:
                next_link = page.get_by_role("link", name="Siguiente")
                if not next_link.is_visible():
                    break
                time.sleep(random.uniform(4.0, 7.0))
                next_link.click(timeout=5000)
                page.wait_for_timeout(4000)
            except PlaywrightTimeoutError:
                break
            except Exception:
                break

        browser.close()

    if all_leads:
        filename = build_filename(query)
        fieldnames = ["nombre", "telefono", "web", "estado_web", "prioridad"]
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_leads)
        print(f"\nGuardados {len(all_leads)} leads en {filename}")
    else:
        print("No se han encontrado leads.")


def main():
    user_query = input('Búsqueda local (ej: "fontaneros cordoba"): ').strip()
    query = user_query or DEFAULT_QUERY
    run_scraper(query)


if __name__ == "__main__":
    main()
