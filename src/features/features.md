### Features

### Lineup Context
* **ROSTER_COUNT**: Total number of players dressed and active for the game.
* **SOLID_PLAYER_COUNT**: Number of active players with a historical efficiency (EFF) over 11.
* **BIG_3_EFF_SUM**: Combined season efficiency average of the top 3 players active tonight.
* **ACTIVE_ROSTER_PTS**: Sum of the season scoring averages of all players active tonight.
* **ACTIVE_ROSTER_EFF**: Sum of the season efficiency averages of all players active tonight.
* **ACTIVE_ROSTER_STL**: Sum of the season steal averages of all players active tonight (Lineup Defense).
* **ACTIVE_ROSTER_BLK**: Sum of the season block averages of all players active tonight (Lineup Defense).
* **TEAM_SEASON_AVG_PTS**: The team's overall scoring average for the current season.
* **ROSTER_SCORING_VARIANCE**: The difference between tonight's active lineup's average and the team's season average.

### Team Form
* **TEAM_PTS_last_5 / _season**: Average points scored over the last 5 games and the full season.
* **TEAM_AST_last_5 / _season**: Average assists recorded over the last 5 games and the full season.
* **TEAM_REB_last_5**: Average total rebounds grabbed over the last 5 games.
* **TEAM_3PT_PCT_last_5 / _season**: Mathematically true 3-point percentage over the last 5 games and the full season.
* **TEAM_PTS_ALLOWED_last_5 / _season**: Average points the team has surrendered to opponents (Team Defense).

### Opponent's form
* **OPP_PTS_ALLOWED_last_5 / _season**: Average points the opponent gives up to teams (Defensive Weakness).
* **OPP_REB_ALLOWED_last_5 / _season**: Average rebounds the opponent allows to teams.
* **OPP_3PT_PCT_ALLOWED_season**: Historical 3-point percentage allowed by the opponent's defense.
* **OPP_TEAM_PTS_last_5**: The opponent's recent scoring form.
* **OPP_TEAM_3PT_PCT_last_5 / _season**: The opponent's recent and long-term 3-point shooting threat.

### Opponent's lineup context
* **OPP_ROSTER_COUNT**: Total number of players active for the opponent tonight.
* **OPP_SOLID_PLAYER_COUNT**: Number of "solid" efficiency players active for the opponent tonight.
* **OPP_BIG_3_EFF_SUM**: The star power level of the opponent's top 3 players tonight.
* **OPP_ROSTER_SCORING_VARIANCE**: Indicates if the opponent is missing key scorers tonight.
* **OPP_ACTIVE_ROSTER_STL / _BLK**: The defensive disruption potential of the opponent's active lineup.

### Matchup & Calendar Features
* **H2H_PTS_season**: Average points the primary team scores when facing this specific opponent.
* **MONTH**: The month of the year to capture seasonal trends (e.g., playoff push).
* **DAY_OF_WEEK**: Day of the week to capture schedule-based performance patterns.