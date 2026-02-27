import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt


# 1. Open the file
with open('/Users/nikos/basketball-stats/data/raw/fragi_stats.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

# 2. Find the specific stats table
table = soup.find('table', id='playerDataTable')

# 3. Read it (header=1 means use the second row for column names)
df = pd.read_html(str(table), header=1)[0]

df.columns = [
    'Date', 'Match', 'EFF', 'PTS', 
    '2FG_MA', '2FG_PCT',   # The first pair
    '3FG_MA', '3FG_PCT',   # The second pair
    'FT_MA',  'FT_PCT',    # The third pair
    'AST', 'STL', 'BLK', 'REB_TOT', 'REB_OFF', 'REB_DEF', 'TO', 'FLS'
]

# 4. Print the key stats to verify
print(df[['Date', 'Match', 'PTS', 'REB_TOT', 'AST', '2FG_MA', '3FG_MA']])

# Convert Date from text to datetime objects
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')

# Remove '%' sign and convert to numbers (float)
cols_to_fix = ['2FG_PCT', '3FG_PCT', 'FT_PCT']
for col in cols_to_fix:
    df[col] = df[col].astype(str).str.replace('%', '')
    # 2. Convert to number (force '-' to become NaN)
    df[col] = pd.to_numeric(df[col], errors='coerce')
    # 3. Replace NaN with 0.0
    df[col] = df[col].fillna(0.0)

# Sort by date (oldest game first) for a correct time-series plot
df = df.sort_values('Date')

print(df.head())
# --- 3. PLOT ---
plt.figure(figsize=(10, 5))
plt.plot(df['Date'], df['2FG_PCT'], marker='o', linestyle='-', color='blue', label='2PT%')
plt.plot(df['Date'], df['3FG_PCT'], marker='o', linestyle='-', color='orange', label='3PT%')
plt.title('Ποσοστό Τριπόντων ανά Παιχνίδι - Φραγκίσκος')
plt.xlabel('Ημερομηνία')
plt.ylabel('Ποσοστό %')
plt.grid(True)
plt.legend()

# Show the plot
plt.show()