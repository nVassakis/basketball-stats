import pandas as pd
import sqlite3

# --- Helper Functions ---
def get_season_avg(x): return x.shift(1).expanding(min_periods=1).mean()
def get_season_sum(x): return x.shift(1).expanding(min_periods=1).sum()
def get_last_5_avg(x): return x.shift(1).rolling(5, min_periods=1).mean()
def get_last_5_sum(x): return x.shift(1).rolling(5, min_periods=1).sum()

def engineer_team_features():
    conn = sqlite3.connect('data/basketball.db')
    
    print("Loading raw stats...")
    df = pd.read_sql("SELECT * FROM raw_stats", conn)
    df['DATE'] = pd.to_datetime(df['DATE'], format='%d/%m/%Y')
    df = df.sort_values('DATE').reset_index(drop=True)

    # Calculate USG
    df['USG'] = df['2FG_A'] + df['3FG_A'] + df['FT_A']

     # ---------------------------------------------------------
    # Step 1: Calculate Lineup Context
    # ---------------------------------------------------------
    player_season_gb = df.groupby(['PLAYER', 'SEASON'])
    
    for col in ['PTS', 'EFF', 'STL', 'BLK']:
        df[f'PLAYER_{col}_AVG'] = player_season_gb[col].transform(get_season_avg)

    df['PLAYER_GAMES_PLAYED'] = player_season_gb.cumcount()
    df['IS_SOLID_PLAYER'] = (df['PLAYER_EFF_AVG'] > 11).astype(int)
    df['EFF_RANK'] = df[df['PLAYER_GAMES_PLAYED'] >= 3].groupby(['DATE', 'TEAM'])['PLAYER_EFF_AVG'].rank(ascending=False, method='first')

    # ---------------------------------------------------------
    # Step 2: Aggregation
    # ---------------------------------------------------------
    print("Aggregating into Team Totals...")

    team_df = df.groupby(['SEASON', 'DATE', 'MATCH', 'TEAM', 'OPPONENT']).agg(
        TEAM_PTS=('PTS', 'sum'),
        TEAM_AST=('AST', 'sum'), 
        TEAM_REB=('REB_TOT', 'sum'),
        TEAM_STL=('STL', 'sum'),
        TEAM_BLK=('BLK', 'sum'), 
        TEAM_TO=('TO', 'sum'),
        TEAM_USG=('USG', 'sum'), 
        ROSTER_COUNT=('PLAYER', 'count'), 
        SOLID_PLAYER_COUNT=('IS_SOLID_PLAYER', 'sum'),
        BIG_3_EFF_SUM=('PLAYER_EFF_AVG', lambda x: x[df.loc[x.index, 'EFF_RANK'] <= 3].sum()),
        ACTIVE_ROSTER_PTS=('PLAYER_PTS_AVG', 'sum'),
        ACTIVE_ROSTER_EFF=('PLAYER_EFF_AVG', 'sum'),
        ACTIVE_ROSTER_STL=('PLAYER_STL_AVG', 'sum'),
        ACTIVE_ROSTER_BLK=('PLAYER_BLK_AVG', 'sum'),
        TEAM_3PM=('3FG_M', 'sum'), 
        TEAM_3PA=('3FG_A', 'sum')
    ).reset_index().sort_values('DATE').reset_index(drop=True)

    team_df['TEAM_SEASON_AVG_PTS'] = team_df.groupby(['TEAM', 'SEASON'])['TEAM_PTS'].transform(get_season_avg)
    team_df['ROSTER_SCORING_VARIANCE'] = team_df['ACTIVE_ROSTER_PTS'] - team_df['TEAM_SEASON_AVG_PTS']
    
    # Drop games with less than 21 points: Missed games or bad data
    team_df = team_df[team_df['TEAM_PTS'] >= 21].reset_index(drop=True)

    team_df = pd.merge(team_df, team_df[['DATE', 'MATCH', 'TEAM', 'TEAM_PTS']].rename(columns={'TEAM': 'OPPONENT', 'TEAM_PTS': 'OPP_PTS_GAME'}), on=['DATE', 'MATCH', 'OPPONENT'], how='left')
    
    # Calendar Features
    team_df['MONTH'] = team_df['DATE'].dt.month
    team_df['DAY_OF_WEEK'] = team_df['DATE'].dt.dayofweek

    # ---------------------------------------------------------
    # Step 3: Team Form (Short & Long Term)
    # ---------------------------------------------------------
    t_gb = team_df.groupby('TEAM')
    t_season_gb = team_df.groupby(['TEAM', 'SEASON'])

    for col in ['TEAM_PTS', 'TEAM_AST', 'TEAM_REB', 'OPP_PTS_GAME']:
        team_df[f'{col.replace("OPP_PTS_GAME", "TEAM_PTS_ALLOWED")}_last_5'] = t_gb[col].transform(get_last_5_avg)
        if col != 'TEAM_REB':
            team_df[f'{col.replace("OPP_PTS_GAME", "TEAM_PTS_ALLOWED")}_season'] = t_season_gb[col].transform(get_season_avg)

    team_df['TEAM_3PT_PCT_last_5'] = (t_gb['TEAM_3PM'].transform(get_last_5_sum) / t_gb['TEAM_3PA'].transform(get_last_5_sum)).fillna(0)
    team_df['TEAM_3PT_PCT_season'] = (t_season_gb['TEAM_3PM'].transform(get_season_sum) / t_season_gb['TEAM_3PA'].transform(get_season_sum)).fillna(0)

    # ---------------------------------------------------------
    # Step 4: Oponnents stats
    # ---------------------------------------------------------
    opp_gb = team_df.groupby('OPPONENT')
    opp_season_gb = team_df.groupby(['OPPONENT', 'SEASON'])

    for col in ['TEAM_PTS', 'TEAM_REB']:
        team_df[f'OPP_{col.replace("TEAM_", "")}_ALLOWED_last_5'] = opp_gb[col].transform(get_last_5_avg)
        team_df[f'OPP_{col.replace("TEAM_", "")}_ALLOWED_season'] = opp_season_gb[col].transform(get_season_avg)

    team_df['OPP_3PT_PCT_ALLOWED_season'] = (opp_season_gb['TEAM_3PM'].transform(get_season_sum) / opp_season_gb['TEAM_3PA'].transform(get_season_sum)).fillna(0)

    # Opponent's Active Lineup & Form
    cols_to_mirror = ['TEAM_PTS_last_5', 'TEAM_3PT_PCT_last_5', 'TEAM_3PT_PCT_season', 'ROSTER_COUNT', 'SOLID_PLAYER_COUNT', 'BIG_3_EFF_SUM', 'ROSTER_SCORING_VARIANCE', 'ACTIVE_ROSTER_STL', 'ACTIVE_ROSTER_BLK']
    opp_stats = team_df[['DATE', 'MATCH', 'TEAM'] + cols_to_mirror].rename(columns={'TEAM': 'OPPONENT', **{c: f"OPP_{c}" for c in cols_to_mirror}})
    
    # Attach to the main dataframe
    team_df = pd.merge(team_df, opp_stats, on=['DATE', 'MATCH', 'OPPONENT'], how='left')

    # How many points does the team score against this specific opponent
    team_df['H2H_PTS_season'] = team_df.groupby(['TEAM', 'OPPONENT', 'SEASON'])['TEAM_PTS'].transform(get_season_avg)

    # ---------------------------------------------------------
    # Step 6: Save
    # ---------------------------------------------------------

# ---------------------------------------------------------
    # Step 5.9: Final Column Selection
    # ---------------------------------------------------------
    # Keep only the columns that exist in the dataframe
    features = [
        'SEASON', 'DATE', 'MONTH', 'DAY_OF_WEEK', 'MATCH', 'TEAM', 'OPPONENT', 'TEAM_PTS',
        'ROSTER_COUNT', 'SOLID_PLAYER_COUNT', 'BIG_3_EFF_SUM',
        'ACTIVE_ROSTER_EFF', 'ACTIVE_ROSTER_STL', 'ACTIVE_ROSTER_BLK',
        'TEAM_PTS_last_5', 'TEAM_AST_last_5', 'TEAM_REB_last_5',
        'TEAM_3PT_PCT_last_5', 'TEAM_PTS_ALLOWED_last_5',
        # Opponent
        'OPP_ROSTER_COUNT', 'OPP_SOLID_PLAYER_COUNT', 'OPP_BIG_3_EFF_SUM',
        'OPP_ROSTER_SCORING_VARIANCE', 'OPP_ACTIVE_ROSTER_STL', 'OPP_ACTIVE_ROSTER_BLK',
        'OPP_TEAM_PTS_last_5', 'OPP_TEAM_3PT_PCT_last_5',
        'OPP_PTS_ALLOWED_last_5', 'OPP_REB_ALLOWED_last_5',
        'OPP_3PT_PCT_ALLOWED_season',
    ]

    final_df = team_df[[c for c in features if c in team_df.columns]]

    print("Saving team features to database...")
    final_df.to_sql('ml_team_features', conn, if_exists='replace', index=False)
    print("Success! Process completed.")
    conn.close()

if __name__ == "__main__":
    engineer_team_features()