import pandas as pd

def greek_to_latin(text):
    """Converts Greek text to Latin (English) characters."""

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
    
    result = [greek_map.get(char, char) for char in text]
    return "".join(result)

def get_opponent(row):
    parts = str(row['Match']).split('-', 1)
    if len(parts) < 2:
        return ""

    left, right = parts[0].strip(), parts[1].strip()

    # Normalize strings to compare them safely
    team_norm = str(row['Team']).lower().replace(' ', '').replace('-', '')
    left_norm = left.lower().replace(' ', '').replace('-', '')

    # If the team matches the left side, opponent is right. Otherwise, left.
    return right if team_norm == left_norm else left

def validate_team_points(df):
    """
    For each (Date, Match, Team) group, sums player PTS and checks it against the
    two scores in the Result field (format: '45 - 53'). Drops rows for any team/game
    where the sum doesn't match either score and logs the discrepancy.
    """
    rows_to_drop = []

    for (date, match, result), game_group in df.groupby(['Date', 'Match', 'Result']):
        try:
            parts = str(result).split('-')
            if len(parts) != 2:
                continue
            score_left = int(parts[0].strip())
            score_right = int(parts[1].strip())
        except (ValueError, AttributeError):
            continue

        valid_scores = {score_left, score_right}

        for team, team_group in game_group.groupby('Team'):
            team_pts = pd.to_numeric(team_group['PTS'], errors='coerce').fillna(0).astype(int).sum()
            if team_pts not in valid_scores:
                print(
                    f"[WARN] Points mismatch — {team} | {match} | {date} | "
                    f"computed={team_pts}, result={score_left}-{score_right}. Dropping {len(team_group)} rows."
                )
                rows_to_drop.extend(team_group.index.tolist())

    if rows_to_drop:
        df = df.drop(index=rows_to_drop).reset_index(drop=True)

    return df