import pandas as pd
import sqlite3
import os

def ingest_data():
    csv_path = 'data/processed/full_stats_master.csv'
    db_path = 'data/basketball.db'

    print(f"Reading data from {csv_path}...")
    df = pd.read_csv(csv_path)

    # Connect to SQLite 
    print("Connecting to SQLite database...")
    conn = sqlite3.connect(db_path)

    # Push the dataframe to a SQL table named 'raw_stats'
    print("Writing data to 'raw_stats' table...")
    df.to_sql('raw_stats', conn, if_exists='replace', index=False)

    # Verify the ingestion
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM raw_stats")
    row_count = cursor.fetchone()[0]
    
    print(f"Success! {row_count} rows ingested into the database.")
    conn.close()


if __name__ == "__main__":
    ingest_data()