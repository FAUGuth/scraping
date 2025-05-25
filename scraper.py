import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import List, Dict
import json
import time
import re

class ISKAScraper:
    def __init__(self):
        self.base_url = "https://www.iska-nuernberg.de/zab/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_page(self, url: str) -> BeautifulSoup:
        """Holt eine Seite und gibt sie als BeautifulSoup Objekt zurück"""
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')

    def get_main_text(self, url: str) -> str:
        try:
            # Entferne die Session-ID aus der URL
            url = re.sub(r'\?PHPSESSID=[^&]+', '', url)
            soup = self.get_page(url)
            main = soup.find('main')
            if main:
                # Nur sichtbaren Text, keine Skripte/Styles
                return main.get_text(separator='\n', strip=True)
            else:
                return ''
        except Exception as e:
            print(f"Fehler beim Abrufen von {url}: {e}")
            return ''

    def scrape_projekte(self) -> List[Dict]:
        """Scraped alle Projekte von der Projekte-Seite"""
        soup = self.get_page(self.base_url + "projekte.html")
        projekte = []
        for block in soup.find_all('div', class_='kasten-grau'):
            kategorie = block.find('h2').get_text(strip=True)
            for a in block.find_all('a'):
                titel = a.get_text(strip=True)
                link = a.get('href')
                if link and not link.startswith('http'):
                    link = self.base_url + link
                details = self.get_main_text(link) if link else ''
                projekte.append({
                    'Kategorie': kategorie,
                    'Titel': titel,
                    'Link': link,
                    'Details': details
                })
                time.sleep(0.5)  # Schonung des Servers
        return projekte

    def save_to_csv(self, data: List[Dict], filename: str = 'projekte.csv'):
        """Speichert die Daten in einer CSV-Datei"""
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"Daten wurden in {filename} gespeichert")

    def save_to_json(self, data: List[Dict], filename: str = 'projekte.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Daten wurden in {filename} gespeichert")

def main():
    scraper = ISKAScraper()
    print("Starte Scraping der Projekte...")
    projekte = scraper.scrape_projekte()
    print(f"Gefunden: {len(projekte)} Projekte")
    scraper.save_to_csv(projekte)
    scraper.save_to_json(projekte)

if __name__ == "__main__":
    main() 