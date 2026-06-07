import requests
from bs4 import BeautifulSoup
import json
import time

# Define headers to look like a standard web browser (prevents basic blocks)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

all_kanji_data = []
page = 1

print("Starting N3 Kanji Scraper...")

while True:
    # Construct URL dynamically with the page index variable
    url = f"https://jisho.org/search/%20%23kanji%20%23jlpt-n3%20?page={page}"
    print(f"Scraping Page {page}: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        # If the page returns a bad status code, stop the loop
        if response.status_code != 200:
            print(f"Stopped. Server responded with status code: {response.status_code}")
            break
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # BROAD MATCH FIX: Find the explicit blocks containing the kanji characters first
        literal_blocks = soup.find_all('div', class_='literal_block')
        
        # If Jisho returns an empty page (we've passed the last page), break out
        if not literal_blocks:
            print("No more entries found. Scraping complete!")
            break
            
        # Navigate from the literal block up or down to find contextual readings
        for block in literal_blocks:
            # The entry component containing the local content data
            parent_container = block.find_parent('div', class_='kanji_light_content')
            if not parent_container:
                # Fallback to general parent entry if the exact inner wrapper changes
                parent_container = block.parent 

            # 1. Kanji Character
            kanji_char = block.get_text(strip=True)
            
            # 2. Meanings
            meanings_div = parent_container.find('div', class_='meanings')
            meanings = []
            if meanings_div:
                meanings = [m.get_text(strip=True).rstrip(',') for m in meanings_div.find_all('span')]
                meanings = [m for m in meanings if m]
                
            # 3. Kunyomi
            kun_div = parent_container.find('div', class_='kun')
            kun_readings = []
            if kun_div:
                reading_spans = kun_div.find_all('span')[1:]
                kun_readings = [r.get_text(strip=True).rstrip('、') for r in reading_spans]
                
            # 4. Onyomi
            on_div = parent_container.find('div', class_='on')
            on_readings = []
            if on_div:
                reading_spans = on_div.find_all('span')[1:]
                on_readings = [r.get_text(strip=True).rstrip('、') for r in reading_spans]

            # Append structured object
            all_kanji_data.append({
                "kanji": kanji_char,
                "meanings": meanings,
                "kunyomi": kun_readings,
                "onyomi": on_readings
            })
            
        print(f"[DEBUG] Successfully grabbed {len(literal_blocks)} entries from page {page}.")
        
        # Move to next page
        page += 1
        
        # Pause 1.5 seconds between pages so Jisho doesn't rate-limit your IP
        time.sleep(1.5)
        
    except Exception as e:
        print(f"An error occurred on page {page}: {e}")
        break

# Save all results perfectly to a local JSON file
output_file = "n3_kanji_database.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_kanji_data, f, indent=2, ensure_ascii=False)

print(f"\nSuccess! Gathered {len(all_kanji_data)} Kanji cards.")
print(f"Saved database offline to: '{output_file}'")