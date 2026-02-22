import pandas as pd
import sqlite3

def engineer_features():
    db_path = 'data/basketball.db'
    conn = sqlite3.connect(db_path)

    print("Loading raw stats...")
    df = pd.read_sql("SELECT * FROM raw_stats", conn)

    # Sort the data chronologically
    df['DATE'] = pd.to_datetime(df['DATE'])
    df = df.sort_values(by=['DATE']).reset_index(drop=True)

    # Calculate 'USG' (Usage) - Total shots taken
    df['USG'] = df['2FG_A'] + df['3FG_A'] + df['FT_A']

    # ---------------------------------------------------------
    # Step 1: Short-Term Form -> Last 3 Games
    # ---------------------------------------------------------
    print("Calculating Short-Term Form...")

    # .shift(1) hides today's game. .rolling(3) looks at the last 3 games.
    def get_last_3_avg(series):
        return series.shift(1).rolling(window=3, min_periods=1).mean()
    
    # Apply the formula to each player individually using groupby
    df['PTS_last_3'] = df.groupby('PLAYER')['PTS'].transform(get_last_3_avg)
    df['EFF_last_3'] = df.groupby('PLAYER')['EFF'].transform(get_last_3_avg)
    df['USG_last_3'] = df.groupby('PLAYER')['USG'].transform(get_last_3_avg)


    # ---------------------------------------------------------
    # Step 2: Long-Term Form -> Season Average
    # ---------------------------------------------------------
    print("Calculating Season Baselines...")
    
    # .expanding() means "take the average of ALL previous games in the group"
    def get_season_avg(series):
        return series.shift(1).expanding(min_periods=1).mean()

    # Group by both Player AND Season (so the math resets every new year)
    df['PTS_season_avg'] = df.groupby(['PLAYER', 'SEASON'])['PTS'].transform(get_season_avg)
    df['REB_season_avg'] = df.groupby(['PLAYER', 'SEASON'])['REB_TOT'].transform(get_season_avg)
    df['EFF_season_avg'] = df.groupby(['PLAYER', 'SEASON'])['EFF'].transform(get_season_avg)
    df['AST_season_avg'] = df.groupby(['PLAYER', 'SEASON'])['AST'].transform(get_season_avg)

    # ---------------------------------------------------------
    # Step 3: Player vs. Opponent History
    # ---------------------------------------------------------
    print("Calculating Historical Matchups...")
    
    # How well does this player usually play against this specific team
    df['PTS_vs_OPP_hist'] = df.groupby(['PLAYER', 'OPPONENT'])['PTS'].transform(get_season_avg)
    df['EFF_vs_OPP_hist'] = df.groupby(['PLAYER', 'OPPONENT'])['EFF'].transform(get_season_avg)

    # ---------------------------------------------------------
    # Step 4: Opponent Vulnerability
    # ---------------------------------------------------------
    print("Calculating Opponent Vulnerability...")
    
    # How well does the OPPONENT defend
    df['OPP_PTS_ALLOWED_PER_PLAYER'] = df.groupby(['OPPONENT', 'SEASON'])['PTS'].transform(get_season_avg)
    df['OPP_REB_ALLOWED_PER_PLAYER'] = df.groupby(['OPPONENT', 'SEASON'])['REB_TOT'].transform(get_season_avg)

    # ---------------------------------------------------------
    # Step 5: Save the ML-Ready Data
    # ---------------------------------------------------------
    print("Saving features to database...")
    
    # Save features to a new table
    # We don't overwrite the raw data
    df.to_sql('ml_features', conn, if_exists='replace', index=False)
    print("Success! Feature engineering complete.")
    conn.close()

if __name__ == "__main__":
    engineer_features()
