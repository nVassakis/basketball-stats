import pandas as pd
from bs4 import BeautifulSoup
import os
from io import StringIO
import json

# --- CONFIG ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_ROOT = os.path.join(BASE_DIR, 'data', 'raw')
OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'teams_stats_master.csv')

def greek_to_latin(text):
    """
    Converts Greek text to Latin (English) characters.
    Handles accents and common distinct mappings (e.g., 'Θ' -> 'Th', 'Ξ' -> 'X').
    """
    # if not isinstance(text, str):
    #     return text

    greek_map = {
        # Lowercase
        'α': 'a', 'ά': 'a', 'β': 'v', 'γ': 'g', 'δ': 'd', 'ε': 'e', 'έ': 'e',
        'ζ': 'z', 'η': 'i', 'ή': 'i', 'θ': 'th', 'ι': 'i', 'ί': 'i', 'ϊ': 'i', 'ΐ': 'i',
        'κ': 'k', 'λ': 'l', 'μ': 'm', 'ν': 'n', 'ξ': 'x', 'ο': 'o', 'ό': 'o',
        'π': 'p', 'ρ': 'r', 'σ': 's', 'ς': 's', 'τ': 't', 'υ': 'u', 'ύ': 'u', 'ϋ': 'u', 'ΰ': 'u',
        'φ': 'f', 'χ': 'ch', 'ψ': 'ps', 'ω': 'o', 'ώ': 'o',
        
        # Uppercase
        'Α': 'A', 'Ά': 'A', 'Β': 'V', 'Γ': 'G', 'Δ': 'D', 'Ε': 'E', 'Έ': 'E',
        'Ζ': 'Z', 'Η': 'I', 'Ή': 'I', 'Θ': 'Th', 'Ι': 'I', 'Ί': 'I', 'Ϊ': 'I',
        'Κ': 'K', 'Λ': 'L', 'Μ': 'M', 'Ν': 'N', 'Ξ': 'X', 'Ο': 'O', 'Ό': 'O',
        'Π': 'P', 'Ρ': 'R', 'Σ': 'S', 'Τ': 'T', 'Υ': 'Y', 'Ύ': 'Y', 'Ϋ': 'Y',
        'Φ': 'F', 'Χ': 'Ch', 'Ψ': 'Ps', 'Ω': 'O', 'Ώ': 'O',

        # Add these to prevent crashes on valid formatting:
        ' ': ' ', 
        '-': '-',
        '.': '.',
        "'": "'"
    }
    
    # Sort keys by length (descending) to handle multi-char replacements like 'Th' or 'Ps' correctly if needed,
    # though here we are doing char-by-char. For 'Th' output, standard replacement works fine.
    
    result = []
    for char in text:
        result.append(greek_map.get(char, char)) # Default to original char if not in map
        
    return "".join(result)

def parse_html_file(filepath, team_slug, season_id):
    """Extracts stats from a single HTML file"""
    try:
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

        print(f"Processing: {player_name} ({team_slug} | {season_id})")

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

        # Splitting columns like "3/5" into "3FG_M" and "3FG_A"
        ma_cols = ['2FG_MA', '3FG_MA', 'FT_MA']
        for col in ma_cols:
            if col in df.columns:
                prefix = col.replace('_MA', '') # result: '2FG_MA'->'2FG'
                
                # Split and expand into two temp columns
                split_df = df[col].astype(str).str.split(r'[/]', expand=True)
                
                # Assign Made (_M) and Attempted (_A) columns, coerce errors to NaN then fill with 0
                if split_df.shape[1] == 2:
                    df[f'{prefix}_M'] = pd.to_numeric(split_df[0], errors='coerce').fillna(0).astype(int)
                    df[f'{prefix}_A'] = pd.to_numeric(split_df[1], errors='coerce').fillna(0).astype(int)
                else:
                    raise ValueError(f"Error parsing {col} for {player_name}: Something went wrong with splitting.")
        
        #Drop original MA columns after splitting
        df = df.drop(columns=ma_cols)

        # Clean percentages
        cols_to_fix = ['2FG_PCT', '3FG_PCT', 'FT_PCT']
        for col in cols_to_fix:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('%', '')
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

        # --- Handle opponent column ---
        if 'Match' in df.columns:
            df['Match'] = df['Match'].astype(str).str.strip()
            
            def get_opp(row):
                # Manual handling of these teams
                match_str = row['Match']
                if "Αεροδρομιακ" in match_str and "αεροδρομιακ" not in team_slug.lower():
                    return "Aerodromiakos"
                if "Ανηθικ" in match_str and "ανηθικ" not in team_slug.lower():
                    return "Anithikoi Pithikoi"
                    
                # Split by dash
                parts = match_str.split('-')
                
                if len(parts) != 2: 
                    raise ValueError(f"Match splitting went wrong for {player_name}: {row['Match']}")
                
                my_identifier = team_slug.lower().replace('-', '').replace(' ', '')

                if "αεροδρομ" in my_identifier:
                    my_identifier = "αεροδρομιακος"
                if "protheas" in my_identifier:
                    my_identifier = "proteas"

                part1_clean = parts[0].lower().replace(' ', '')
                if my_identifier in part1_clean:
                    return parts[1].strip()
                else:
                    return parts[0].strip()

            df['Opponent'] = df.apply(get_opp, axis=1)

        # Add Metadata
        df['Player'] = player_name.strip()
        df['Team'] = team_slug.strip() 
        df['Season'] = season_id.strip()

        # Drop 'Match' if you don't want the original string anymore
        # df = df.drop(columns=['Match'])
        
        # Add Name, Team, Season
        df['Player'] = player_name.strip()
        df['Team'] = team_slug.strip() 
        df['Season'] = season_id.strip()
        
        return df

    except Exception as e:
        print(f"Error parsing file {filepath}: {e}")
        return None

def run_pipeline():
    print(f"Starting Batch Parser in: {INPUT_ROOT}")
    
    # Create processed folder if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    all_players = []
    
    # Check root folder
    if not os.path.exists(INPUT_ROOT):
        print(f"Error: Folder not found! {INPUT_ROOT}")
        return

    # Loop 1: Teams
    for team_slug in os.listdir(INPUT_ROOT):
        team_path = os.path.join(INPUT_ROOT, team_slug)
        
        # Loop 2: Seasons
        for season_id in os.listdir(team_path):
            season_path = os.path.join(team_path, season_id)
            
            if not os.path.isdir(season_path) or season_id.startswith('.'):
                continue

            # Loop 3: Files
            files = [f for f in os.listdir(season_path) if f.endswith(".html")]
            
            for filename in files:
                full_path = os.path.join(season_path, filename)
                
                # Parse with metadata
                player_df = parse_html_file(full_path, team_slug, season_id)
                
                if player_df is not None and not player_df.empty:
                    all_players.append(player_df)
                elif player_df is None:
                    print(f"   No valid table found in {filename}. Skipping.")
                    pass 

    if not all_players:
        print("No data parsed.")
        return

    # Combine
    master_df = pd.concat(all_players, ignore_index=True)

    print("Translating Player Names...")
    master_df['Player'] = master_df['Player'].apply(greek_to_latin)

    # Load the JSON Mapping
    mapping_file = os.path.join(BASE_DIR,'team_mapping.json')
    with open(mapping_file, 'r', encoding='utf-8') as f:
        team_mapping = json.load(f)
    print("Mapping loaded successfully.")

    # Apply mapping to the Team column
    master_df['Team'] = master_df['Team'].map(team_mapping).fillna(master_df['Team'])

    # Apply Mapping to team-name columns
    master_df['Team'] = master_df['Team'].replace(team_mapping)
    master_df['Opponent'] = master_df['Opponent'].replace(team_mapping)

    # Final Cleanup: Sort by Team, Player, then Date
    master_df['Date'] = pd.to_datetime(master_df['Date'], format='%d/%m/%Y', errors='coerce')
    master_df['YEAR'] = master_df['Date'].dt.year.fillna(0).astype(int)
    master_df['MONTH'] = master_df['Date'].dt.month.fillna(0).astype(int)
    master_df['DAY'] = master_df['Date'].dt.day.fillna(0).astype(int)
    master_df = master_df.sort_values(['Team', 'Player', 'Date'])

    final_columns = [
        'Season', 'Date', 'YEAR', 'MONTH', 'DAY', 
        'Player', 'Match','Team', 'Opponent', 
        'EFF', 'PTS', 
        'FT_M', 'FT_A', 'FT_PCT', 
        '2FG_M', '2FG_A', '2FG_PCT', 
        '3FG_M', '3FG_A', '3FG_PCT', 
        'AST', 'STL', 'BLK', 
        'REB_TOT', 'REB_OFF', 'REB_DEF', 
        'TO', 'FLS'
    ]

    cols_to_keep = [c for c in final_columns if c in master_df.columns]
    master_df = master_df[cols_to_keep]
    master_df.columns = master_df.columns.str.upper()

    # Save
    master_df.to_csv(OUTPUT_FILE, index=False)
    print("-" * 40)
    print(f"Success! Saved stats for {len(all_players)} files.")
    print(f"Location: {OUTPUT_FILE}")

if __name__ == "__main__":
    run_pipeline()