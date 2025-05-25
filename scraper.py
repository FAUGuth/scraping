import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
import os
import time
import json

def clean_url(url):
    # Find the position of =angebot&
    pos = url.find('=angebot&')
    if pos != -1:
        # Return everything up to and including =angebot&
        return url[:pos + 9]
    return url

def extract_content(url):
    try:
        print(f"Fetching content from: {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title (h2)
        title = soup.find('h2')
        title_text = title.text.strip() if title else ''
        
        # Extract description (first p tag after h2)
        description = ''
        if title:
            # Find the first p tag after the h2
            next_p = title.find_next('p')
            if next_p:
                description = next_p.text.strip()
        
        # Extract Zeitaufwand from small tag
        zeitaufwand = ''
        zeitaufwand_small = soup.find('small', string=lambda text: text and 'Zeitaufwand:' in text)
        if zeitaufwand_small:
            zeitaufwand = zeitaufwand_small.text.strip()
            
        # Extract Einsatzgebiet from small tag
        einsatzgebiet = ''
        einsatzgebiet_small = soup.find('small', string=lambda text: text and 'Einsatzgebiet:' in text)
        if einsatzgebiet_small:
            einsatzgebiet = einsatzgebiet_small.text.strip()
        
        print(f"Found title: {title_text[:50]}..." if len(title_text) > 50 else f"Found title: {title_text}")
        print(f"Found description: {description[:50]}..." if len(description) > 50 else f"Found description: {description}")
        print(f"Found Zeitaufwand: {zeitaufwand}")
        print(f"Found Einsatzgebiet: {einsatzgebiet}")
        
        return {
            'title': title_text,
            'description': description,
            'zeitaufwand': zeitaufwand,
            'einsatzgebiet': einsatzgebiet
        }
    except Exception as e:
        print(f"Error extracting content from {url}: {str(e)}")
        return {
            'title': '',
            'description': '',
            'zeitaufwand': '',
            'einsatzgebiet': ''
        }

def save_html_content(url, title, output_dir='html_content'):
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            print(f"Creating directory: {output_dir}")
            os.makedirs(output_dir)
        
        # Clean the title to create a valid filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = f"{safe_title}.html"
        filepath = os.path.join(output_dir, filename)
        
        print(f"Saving HTML content to: {filepath}")
        # Get the HTML content
        response = requests.get(url)
        response.raise_for_status()
        
        # Save the HTML content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        return True
    except Exception as e:
        print(f"Error saving HTML content for {title}: {str(e)}")
        return False

def scrape_volunteer_opportunities(url):
    print("\nStarting to scrape volunteer opportunities...")
    print(f"Fetching main page: {url}")
    
    # Send a GET request to the URL
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all volunteer opportunities
    opportunities = []
    
    # The opportunities are in <p> tags with <a> tags inside
    print("\nSearching for volunteer opportunities...")
    for i, p in enumerate(soup.find_all('p'), 1):
        # Stop after 10 opportunities
        if len(opportunities) >= 10:
            print("\nReached 10 opportunities, stopping...")
            break
            
        link = p.find('a')
        if link:
            title = link.text.strip()
            print(f"\nProcessing opportunity {i}: {title}")
            
            href = link.get('href', '')
            # Convert relative URL to absolute URL and clean it
            full_url = clean_url(urljoin(url, href))
            
            # Extract content from detail page
            content = extract_content(full_url)
            
            opportunity = {
                'titel': title,
                'link': full_url,
                'organisation': 'Zentrum Aktiver Bürger',
                'zeitaufwand': content['zeitaufwand'],
                'einsatzgebiet': content['einsatzgebiet'],
                'beschreibung': content['description']
            }
            opportunities.append(opportunity)
            
            # Add a small delay to be nice to the server
            print("Waiting 1 second before next request...")
            time.sleep(1)
            
            # Save the HTML content for this opportunity
            save_html_content(full_url, title)
    
    return opportunities

def save_to_csv(opportunities, filename='volunteer_opportunities.csv'):
    print(f"\nSaving {len(opportunities)} opportunities to CSV: {filename}")
    # Write the opportunities to a CSV file
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['titel', 'link', 'organisation', 'zeitaufwand', 'einsatzgebiet', 'beschreibung'])
        writer.writeheader()
        writer.writerows(opportunities)
    print("CSV file saved successfully!")

def save_to_json(opportunities, filename='volunteer_opportunities.json'):
    print(f"\nSaving {len(opportunities)} opportunities to JSON: {filename}")
    # Write the opportunities to a JSON file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(opportunities, f, ensure_ascii=False, indent=2)
    print("JSON file saved successfully!")

def main():
    print("Starting the volunteer opportunity scraper...")
    url = "https://www.iska-nuernberg.de/zab/buergernetz_alle.html?database%5Bsort%5D=angebot&database%5Bcsv%5D=be-stellen&database%5Bfields%5D%5Bzkinder%5D=&database%5Bfields%5D%5Bzjugendliche%5D=&database%5Bfields%5D%5Bzerwachsene%5D=&database%5Bfields%5D%5Bzsenioren%5D=&database%5Bfields%5D%5Bwvor%5D=&database%5Bfields%5D%5Bwnach%5D=&database%5Bfields%5D%5Bwabend%5D=&database%5Bfields%5D%5Bwwochend%5D=&database%5Bfields%5D%5Bwkurz%5D=&database%5Bfields%5D%5Btberatung%5D=&database%5Bfields%5D%5Btbetreuung%5D=&database%5Bfields%5D%5Btbuero%5D=&database%5Bfields%5D%5Btfinanzen%5D=&database%5Bfields%5D%5Bthandwerk%5D=&database%5Bfields%5D%5Btit%5D=&database%5Bfields%5D%5Btkreativ%5D=&database%5Bfields%5D%5Btoeff%5D=&database%5Bfields%5D%5Btorga%5D=&database%5Bfields%5D%5Btpate%5D=&database%5Bfields%5D%5Btsport%5D=&database%5Bfields%5D%5Btsprach%5D=&database%5Bfields%5D%5Btoutdoor%5D=&database%5Bfields%5D%5Btunterricht%5D=&database%5Bfields%5D%5Bbarbeitslos%5D=&database%5Bfields%5D%5Bbarmut%5D=&database%5Bfields%5D%5Bbbildung%5D=&database%5Bfields%5D%5Bbinternat%5D=&database%5Bfields%5D%5Bbfamilie%5D=&database%5Bfields%5D%5Bbforschung%5D=&database%5Bfields%5D%5Bbfrieden%5D=&database%5Bfields%5D%5Bbgesund%5D=&database%5Bfields%5D%5Bbkultur%5D=&database%5Bfields%5D%5Bbbehind%5D=&database%5Bfields%5D%5Bbfluechtlinge%5D=&database%5Bfields%5D%5Bbmobil%5D=&database%5Bfields%5D%5Bboeko%5D=&database%5Bfields%5D%5Bbreligion%5D=&database%5Bfields%5D%5Bbsport%5D=&database%5Bfields%5D%5Bbresoz%5D=&database%5Bfields%5D%5Bbtiere%5D=&database%5Bfields%5D%5Bbwohn%5D=&database%5Bfields%5D%5Bsjung%5D=&database%5Bfields%5D%5B_einrichtung%5D=&database%5Bfields%5D%5B_kurzinfo%5D=&Senden=Suche"
    
    try:
        opportunities = scrape_volunteer_opportunities(url)
        save_to_csv(opportunities)
        save_to_json(opportunities)
        print("\nScraping completed successfully!")
        print(f"Total opportunities scraped: {len(opportunities)}")
        print(f"Data saved to:")
        print(f"- volunteer_opportunities.csv")
        print(f"- volunteer_opportunities.json")
        print(f"HTML content saved in the 'html_content' directory")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    main() 