import json

# Function to convert Katakana to Hiragana for uniform sorting
def katakana_to_hiragana(text):
    # Shift character codes from Katakana range to Hiragana range
    return "".join(chr(ord(c) - 96) if 12449 <= ord(c) <= 12534 else c for c in text)

# Clean readings by dropping trailing okurigana (e.g., "あら.わす" -> "あら")
def clean_reading(reading_str):
    if '.' in reading_str:
        return reading_str.split('.')[0]
    return reading_str

# Load your freshly scraped raw database
with open("n3_kanji_database.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

onyomi_grouped = {}
kunyomi_grouped = {}

# Process each kanji entry
for entry in raw_data:
    kanji = entry["kanji"]
    meanings = entry["meanings"]
    
    # 1. Process ONYOMI (Chinese readings)
    for on in entry.get("onyomi", []):
        # Normalize Katakana to Hiragana (e.g., "セイ" -> "せい")
        hiragana_reading = katakana_to_hiragana(on)
        cleaned_on = clean_reading(hiragana_reading)
        
        if not cleaned_on:
            continue
            
        # Determine the alphabet key block (e.g., "さ" for "せい")
        first_char = cleaned_on[0]
        
        if first_char not in onyomi_grouped:
            onyomi_grouped[first_char] = {}
        if cleaned_on not in onyomi_grouped[first_char]:
            onyomi_grouped[first_char][cleaned_on] = []
            
        onyomi_grouped[first_char][cleaned_on].append({
            "kanji": kanji,
            "meanings": meanings
        })

    # 2. Process KUNYOMI (Native readings)
    for kun in entry.get("kunyomi", []):
        # Ignore prefix/suffix indicators like "-おもて" or "がち-"
        cleaned_kun = clean_reading(kun).replace("-", "")
        
        if not cleaned_kun:
            continue
            
        first_char = cleaned_kun[0]
        
        if first_char not in kunyomi_grouped:
            kunyomi_grouped[first_char] = {}
        if cleaned_kun not in kunyomi_grouped[first_char]:
            kunyomi_grouped[first_char][cleaned_kun] = []
            
        kunyomi_grouped[first_char][cleaned_kun].append({
            "kanji": kanji,
            "meanings": meanings
        })

# Sort the top-level keys alphabetically (あ, い, う, え, お...)
sorted_onyomi = {k: onyomi_grouped[k] for k in sorted(onyomi_grouped.keys())}
sorted_kunyomi = {k: kunyomi_grouped[k] for k in sorted(kunyomi_grouped.keys())}

# Save Onyomi Database
with open("n3_onyomi_grouped.json", "w", encoding="utf-8") as f:
    json.dump(sorted_onyomi, f, indent=2, ensure_ascii=False)

# Save Kunyomi Database
with open("n3_kunyomi_grouped.json", "w", encoding="utf-8") as f:
    json.dump(sorted_kunyomi, f, indent=2, ensure_ascii=False)

print("Success! Created 'n3_onyomi_grouped.json' and 'n3_kunyomi_grouped.json'.")