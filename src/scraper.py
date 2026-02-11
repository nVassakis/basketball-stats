from bs4 import BeautifulSoup
import os
import time
import requests
import re
import random
from urllib.parse import urlparse

# --- CONFIGURATION ---
BASE_URL = "https://www.basketmaniacs.com/team/" 
SEASONS = {
    1: "2023-24",
    2: "2024-25",
    3: "2025-26"
}

# Browser Mask
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_project_root():
    """Calculates project root relative to this script file."""
    # src/scraper.py -> dirname = src/ -> dirname = Project Root
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def download_player(player_data, save_dir):
    name = player_data['name']
    url = player_data['url']
    season = player_data['season'] 

    # Create Season Subfolder inside the specific Team folder
    season_dir = os.path.join(save_dir, season)
    os.makedirs(season_dir, exist_ok=True)
    
    # Create clean filename
    safe_name = re.sub(r'[^\w\u0370-\u03FF_-]', '', name.replace(" ", "_"))
    filename = f"{safe_name}.html"
    save_path = os.path.join(season_dir, filename)
    
    if os.path.exists(save_path):
        print(f" [{season}] Skipping {name} (Already downloaded)")
        return

    print(f"[{season}] Downloading: {name}...", end=" ")
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("✅")
        
        # Polite Sleep
        time.sleep(random.uniform(3, 6))
        
    except Exception as e:
        print(f"Error: {e}")

def run_scraper():
    # --- 1. LOAD TEAMS FROM TXT ---
    base_dir = get_project_root()
    teams_file = os.path.join(base_dir, "teams.txt")

    teams_list = []
    if os.path.exists(teams_file):
        with open(teams_file, "r", encoding="utf-8") as f:
            teams_list = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(teams_list)} teams from file.")
    else:
        raise FileNotFoundError(f"Critical Error: Could not find 'teams.txt' at {teams_file}")

    # --- 2. MASTER LOOP (Iterate through Teams) ---
    for team_slug in teams_list:
        print(f"\n PROCESSING TEAM: {team_slug.upper()}")
        print("=" * 60)
        
        # 2a. Dynamic URL Construction
        team_url = f"{BASE_URL}{team_slug}/"
        
        # 2b. Dynamic Folder Creation
        raw_data_dir = os.path.join(base_dir, 'data', 'raw', team_slug)
        os.makedirs(raw_data_dir, exist_ok=True)
        
        players_to_download = []

        # 2c. Scan Seasons
        for season_id, season_name in SEASONS.items():
            print(f" Scanning Season: {season_name}...", end=" ")
            
            # Add ?season=X
            target_url = f"{team_url}?season={season_id}&tab=roster"
            
            try:
                response = requests.get(target_url, headers=HEADERS) 
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find all player cards
                roster_items = soup.find_all('div', class_='team-roster__item')
                print(f"Found {len(roster_items)} cards.")

                for item in roster_items:
                    link_tag = item.find('a', href=True)
                    if not link_tag: continue
                        
                    player_url = link_tag['href']
                    if not player_url.startswith('http'):
                        player_url = "https://www.basketmaniacs.com" + player_url
                    
                    # Append season ID
                    final_player_url = f"{player_url}?season={season_id}"
                    
                    name_tag = item.find('h2', class_='team-roster__member-name')
                    if name_tag:
                        raw_name = name_tag.get_text(separator=' ', strip=True)
                        clean_name = " ".join(raw_name.split())
                    else:
                        clean_name = "Unknown_" + player_url.split('/')[-1]

                    players_to_download.append({
                        'name': clean_name,
                        'url': final_player_url,
                        'season': season_name
                    })
                
            except Exception as e:
                print(f"\n Error scanning {season_name}: {e}")

        # 2d. Execute Download for this team
        print(f"\n Starting download for {len(players_to_download)} files...")
        for player in players_to_download:
            # Pass the specific team directory to the function
            download_player(player, raw_data_dir) 

    print("\n Process completed")

if __name__ == "__main__":
    run_scraper()