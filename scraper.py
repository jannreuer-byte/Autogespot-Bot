import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

DATA_FILE = "spots.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def fetch_spots():
    url = "https://www.autogespot.com/spots"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Fehler beim Abruf: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"Netzwerkfehler: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    new_spots = []

    # Sucht nach den Spot-Einträgen auf Autogespot
    for item in soup.select("article, div.spot-item, .spot-item"):
        try:
            link_tag = item.select_one("a[href*='/spots/']")
            if not link_tag:
                continue

            spot_url = link_tag.get("href")
            if not spot_url.startswith("http"):
                spot_url = "https://www.autogespot.com" + spot_url

            title_tag = item.select_one(".spot-item__title, .title, h3, h2")
            title = title_tag.get_text(strip=True) if title_tag else "Unbekanntes Fahrzeug"

            location_tag = item.select_one(".spot-item__location, .location")
            location = location_tag.get_text(strip=True) if location_tag else "Unbekannter Ort"

            img_tag = item.select_one("img")
            img_url = ""
            if img_tag:
                img_url = img_tag.get("src") or img_tag.get("data-src") or ""

            spot_id = spot_url.rstrip("/").split("/")[-1]

            new_spots.append({
                "id": spot_id,
                "title": title,
                "location": location,
                "url": spot_url,
                "image": img_url,
                "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
            })
        except Exception as e:
            continue

    return new_spots

def main():
    existing_spots = load_data()
    existing_ids = {s["id"] for s in existing_spots}

    fetched_spots = fetch_spots()
    added_count = 0

    for spot in fetched_spots:
        if spot["id"] not in existing_ids:
            existing_spots.insert(0, spot)
            existing_ids.add(spot["id"])
            added_count += 1

    if added_count > 0:
        print(f"{added_count} neue Spots hinzugefügt.")
        save_data(existing_spots[:500])  # Speichert maximal 500 Einträge
    else:
        print("Keine neuen Spots gefunden.")

if __name__ == "__main__":
    main()
