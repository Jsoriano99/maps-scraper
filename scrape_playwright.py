from playwright.sync_api import sync_playwright
from urllib.parse import quote_plus
from card_parser import parse_card_html

QUERY = "fontaneros cordoba"

def main():
    url = f"https://www.google.com/search?q={quote_plus(QUERY)}&tbm=lcl"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(3000)
        try:
            page.locator('input[type="submit"][value="Aceptar todo"]').first.click()
            page.wait_for_timeout(3000)
        except Exception:
            pass
        page.wait_for_selector("div.VkpGBb", timeout=10000)
        cards = page.query_selector_all("div.VkpGBb")[:25]
        for c in cards:
            card_html = c.evaluate("el => el.outerHTML")
            lead = parse_card_html(card_html)
            print(lead)
        browser.close()

if __name__ == "__main__":
    main()

