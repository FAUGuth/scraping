# ISKA Projekte Scraper

Dieser Scraper extrahiert Informationen über Projekte von der ISKA Nürnberg Website.

## Installation

1. Stellen Sie sicher, dass Python 3.7 oder höher installiert ist
2. Installieren Sie die erforderlichen Pakete:
```bash
pip install -r requirements.txt
```

## Verwendung

Führen Sie den Scraper aus mit:
```bash
python scraper.py
```

Die Ergebnisse werden in einer CSV-Datei namens `projekte.csv` gespeichert.

## Funktionen

- Extrahiert Titel und Beschreibung jedes Projekts
- Speichert die Daten in einer CSV-Datei
- Berücksichtigt Rate-Limiting durch Verzögerungen zwischen Anfragen

## Hinweise

- Der Scraper respektiert die Website durch angemessene Verzögerungen zwischen Anfragen
- Die Daten werden mit UTF-8 Encoding gespeichert
- Bei Fehlern werden diese protokolliert und der Scraper fährt mit dem nächsten Projekt fort 