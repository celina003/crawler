from playwright.async_api import async_playwright
import re

async def scrape_jobs():
    jobs = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.arbeitsagentur.de/jobsuche/suche?angebotsart=4&wo=K%C3%B6ln&umkreis=25&externestellenboersen=true", timeout=60000)

        # Versuchen, das Cookie-Banner zu schließen (wird ignoriert, falls nicht gefunden)
        try:
            # Wartezeit verlängern, um sicherzustellen, dass der Banner da ist
            await page.wait_for_selector('div#bahf-cookie-disclaimer-modal', timeout=30000)  # Den Cookie-Modal-Selktor verwenden
            print("Cookie-Banner gefunden, versuche zu schließen...")
            # Versuch, auf den Hintergrund zu klicken, um den Cookie-Banner zu schließen
            await page.click('div#bahf-cookie-disclaimer-modal')  # Klicke auf den Hintergrund des Banners
            print("Cookie-Banner geschlossen oder ignoriert")
        except Exception as e:
            print(f"Kein Cookie-Banner gefunden oder Fehler beim Schließen: {e}")

        # Warten auf die Jobkarten, auch wenn das Modal da ist
        await page.wait_for_selector('[aria-label^="1. Ergebnis:"]', timeout=30000)

        # Holen Sie alle Jobkarten
        job_elements = await page.query_selector_all('[aria-label^="1. Ergebnis:"]')

        for job_elem in job_elements:
            aria_label = await job_elem.get_attribute('aria-label')

            # Extrahieren der Jobinformationen mit regulären Ausdrücken
            title_match = re.search(r"1\. Ergebnis: (.*?), m/w/d", aria_label)
            company_match = re.search(r"m/w/d\) (.*?), Arbeitsort", aria_label)
            location_match = re.search(r"Arbeitsort: (.*?), Eintrittsdatum", aria_label)
            start_date_match = re.search(r"Eintrittsdatum: (.*?)$", aria_label)

            title = title_match.group(1) if title_match else "Kein Titel"
            company = company_match.group(1) if company_match else "Unbekannt"
            location = location_match.group(1) if location_match else "Unbekannt"
            start_date = start_date_match.group(1) if start_date_match else "Unbekannt"

            # Klicken auf die Jobkarte
            await job_elem.click()

            # Warten auf die Detailseite und Extrahieren der Jobbeschreibung
            await page.wait_for_selector('.job-description')  # Passe den Selektor nach Bedarf an
            description = await page.inner_text('.job-description')  # Beispiel für das Extrahieren der Beschreibung

            jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "start_date": start_date,
                "description": description
            })

            # Zurück zur Jobliste, um mit der nächsten Jobkarte fortzufahren
            await page.go_back()

        await browser.close()

    return jobs