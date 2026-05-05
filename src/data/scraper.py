import os, time, random, csv, requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_team_games():
    base_dir = os.path.join(os.getcwd(), 'data', 'raw')
    csv_path = os.path.join(base_dir, 'master_games_index.csv')
    
    with open("config/teams.txt", "r", encoding="utf-8") as f:
        teams = [line.strip() for line in f if line.strip()]

    for team in teams:
        print(f"Processing {team}...")
        team_dir = os.path.join(base_dir, 'teams', team)
        games_dir = os.path.join(team_dir, 'games')
        os.makedirs(games_dir, exist_ok=True)
        
        team_page = os.path.join(team_dir, 'team_page.html')
        
        # 1. Download Team Page (refresh to discover new games)
        res = requests.get(f"https://www.basketmaniacs.com/team/{team}/", headers=HEADERS)
        with open(team_page, 'w', encoding='utf-8') as f: f.write(res.text)
        time.sleep(random.uniform(2, 4))
            
        # 2. Parse Game Links
        with open(team_page, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            
        # Assuming game links contain '/match/'
        game_links = set([a['href'] for a in soup.find_all('a', href=True) if '/match/' in a['href']])
        
        # 3. Download Games & Update Index
        for url in game_links:
            game_id = url.strip('/').split('/')[-1]
            game_file = os.path.join(games_dir, f"{game_id}.html")
            
            if not os.path.exists(game_file):
                res = requests.get(url, headers=HEADERS)
                with open(game_file, 'w', encoding='utf-8') as f: f.write(res.text)
                
                with open(csv_path, 'a', newline='', encoding='utf-8') as c:
                    csv.writer(c).writerow([url, team, game_file])
                    
                time.sleep(random.uniform(3, 5)) # Be polite to the server
            
            print(f"Saved game {list(game_links).index(url) + 1} out of {len(game_links)}")

        # Check that the number of saved HTML files matches the number of game links
        saved_files = len([f for f in os.listdir(games_dir) if f.endswith('.html')])
        if saved_files != len(game_links):
            print(f"Mismatch for {team}: expected {len(game_links)} files, found {saved_files}. Stopping.")
            break

if __name__ == "__main__":
    scrape_team_games()