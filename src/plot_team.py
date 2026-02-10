import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# 1. Load the Master Data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'team_stats_master.csv')

df = pd.read_csv(CSV_PATH)

# 2. Configure the Plot Style
sns.set_theme(style="whitegrid")

def plot_stat_leaders(stat='PTS'):
    """Plots the average of a specific stat for each player"""
    
    # Calculate Average per Player
    avg_df = df.groupby('Player')[stat].mean().reset_index()
    avg_df = avg_df.sort_values(stat, ascending=False)
    
    plt.figure(figsize=(10, 6))
    
    # Create Bar Chart
    sns.barplot(data=avg_df, x=stat, y='Player', palette='viridis')
    
    plt.title(f'Team Leaders: Average {stat}', fontsize=16)
    plt.xlabel(f'Average {stat}')
    plt.ylabel('')
    plt.tight_layout()
    plt.show()

def plot_trend_over_time(stat='PTS'):
    """Plots the trend of a stat over time for all players"""
    plt.figure(figsize=(12, 6))
    
    # Line Chart with a different color (hue) for each player
    sns.lineplot(data=df, x='Date', y=stat, hue='Player', marker='o')
    
    plt.title(f'{stat} Over Time', fontsize=16)
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left') # Move legend outside
    plt.tight_layout()
    plt.show()

# --- COMMAND CENTER ---
# Uncommon/Comment out the one you want to run:

# Option A: Who is the best scorer?
# plot_stat_leaders('PTS')

# Option B: Who is scoring more lately?
plot_trend_over_time('PTS')

# Option C: Who is the best 3-point shooter? (Efficiency)
# plot_stat_leaders('3FG_PCT')