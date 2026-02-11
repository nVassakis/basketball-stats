import pandas as pd
from bs4 import BeautifulSoup
import os
from io import StringIO

# --- CONFIG ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEAM_SLUG = 'unleash-the-clowns'

INPUT_FOLDER = os.path.join(BASE_DIR, 'data', 'raw', TEAM_SLUG)
OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', f'{TEAM_SLUG}_stats.csv')

def parse_html_file(filepath):
    """Extracts stats from a single HTML file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    # --- GET PLAYER NAME ---
    player_name = "Unknown"
    
    name_tag = soup.find('h1', class_='player-info__name')
    if not name_tag:
        name_tag = soup.find('h2', class_='team-roster__member-name')
        print(f"   Warning: Player name not found in expected tags for {filepath}")
        
    if name_tag:
        raw_name = name_tag.get_text(separator=' ', strip=True)
        player_name = " ".join(raw_name.split())
    else:
        # Fallback: Use filename "Nikos_Vassakis.html" -> "Nikos Vassakis"
        clean_filename = os.path.basename(filepath).replace('.html', '').replace('_', ' ')
        player_name = clean_filename

    print(f"Processing: {player_name}")

    # --- GET TABLE ---
    table = soup.find('table', id='playerDataTable')
    if not table: 
        return None
    
    # --- READ DATA ---
    try:
        df = pd.read_html(StringIO(str(table)), header=1)[0]
    except ValueError:
        return None
    
    # Clean Columns
    cols = ['Date', 'Match', 'EFF', 'PTS', '2FG_MA', '2FG_PCT', '3FG_MA', '3FG_PCT', 
            'FT_MA', 'FT_PCT', 'AST', 'STL', 'BLK', 'REB_TOT', 'REB_OFF', 'REB_DEF', 'TO', 'FLS']
    
    # Validating column count prevents crashes on bad tables
    if len(df.columns) == len(cols):
        df.columns = cols
    else:
        print(f"Skipping {player_name}: Table format mismatch")
        return None

    # Clean percentages
    cols_to_fix = ['2FG_PCT', '3FG_PCT', 'FT_PCT']
    for col in cols_to_fix:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace('%', '')
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    
    # Add Name
    df['Player'] = player_name
    
    return df

def run_pipeline():
    print(f"Starting Parser in: {INPUT_FOLDER}")
    
    # Create processed folder if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    all_players = []
    
    # Loop through files
    if not os.path.exists(INPUT_FOLDER):
        print(f"Error: Folder not found! {INPUT_FOLDER}")
        return

    files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".html")]
    print(f"Found {len(files)} HTML files.")

    for filename in files:
        full_path = os.path.join(INPUT_FOLDER, filename)
        player_df = parse_html_file(full_path)
        
        if player_df is not None and not player_df.empty:
            all_players.append(player_df)

        if player_df is None:
            print(f"   No valid table found in {filename}. Skipping.")  

    if not all_players:
        print(" No data parsed.")
        return

    # Combine
    master_df = pd.concat(all_players, ignore_index=True)
    
    # Final Cleanup: Sort by Name then Date
    master_df['Date'] = pd.to_datetime(master_df['Date'], format='%d/%m/%Y', errors='coerce')
    master_df = master_df.sort_values(['Player', 'Date'])

    # Save
    master_df.to_csv(OUTPUT_FILE, index=False)
    print("-" * 40)
    print(f"Success! Saved stats for {len(all_players)} players.")
    print(f"Location: {OUTPUT_FILE}")

if __name__ == "__main__":
    run_pipeline()