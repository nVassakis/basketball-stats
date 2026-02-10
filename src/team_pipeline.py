import pandas as pd
from bs4 import BeautifulSoup
import os

# CONFIG
TEAM_FOLDER = 'data/raw/'
OUTPUT_FILE = 'data/processed/team_stats_master.csv'

def parse_html_file(filepath):
    """Extracts stats from a single HTML file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    # Get Player Name
    name_tag = soup.find('h1', class_='player-info__name')
    raw_name = name_tag.get_text(separator=' ', strip=True)
    player_name = " ".join(raw_name.split())
    print(f"Processing player: {player_name}")

    # Get Table
    table = soup.find('table', id='playerDataTable')
    if not table: return None
    
    # Read Data
    df = pd.read_html(str(table), header=1)[0]
    
    # Clean Data 
    cols = ['Date', 'Match', 'EFF', 'PTS', '2FG_MA', '2FG_PCT', '3FG_MA', '3FG_PCT', 
            'FT_MA', 'FT_PCT', 'AST', 'STL', 'BLK', 'REB_TOT', 'REB_OFF', 'REB_DEF', 'TO', 'FLS']
    df.columns = cols

    # 5. Clean percentages
    cols_to_fix = ['2FG_PCT', '3FG_PCT', 'FT_PCT']
    for col in cols_to_fix:
        # Remove %, convert to numeric, turn '-' into 0.0
        df[col] = df[col].astype(str).str.replace('%', '')
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    
    # Add the Player Name column
    df['Player'] = player_name
    print(df.head())
    
    return df

def run_pipeline():
    all_players = []
    
    # Loop through every file in the folder
    for filename in os.listdir(TEAM_FOLDER):
        if filename.endswith(".html"):
            print(f"Processing: {filename}...")
            full_path = os.path.join(TEAM_FOLDER, filename)
            
            player_df = parse_html_file(full_path)
            if player_df is not None:
                all_players.append(player_df)

    # Combine all into one big dataframe
    master_df = pd.concat(all_players, ignore_index=True)
    
    # Final cleanup
    master_df['Date'] = pd.to_datetime(master_df['Date'], format='%d/%m/%Y', errors='coerce')
    master_df = master_df.sort_values(['Player', 'Date'])

    # Save
    master_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Success! Saved stats for {len(all_players)} players to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_pipeline()