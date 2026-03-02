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

def extract_opponent_name(match_str, team_slug):
    """Extracts the opponent name from the raw Match string"""
    if "Αεροδρομιακ" in match_str and "αεροδρομιακ" not in team_slug.lower():
        return "Aerodromiakos"
    if "Ανηθικ" in match_str and "ανηθικ" not in team_slug.lower():
        return "Anithikoi Pithikoi"
        
    parts = match_str.split('-')
    if len(parts) != 2: 
        return match_str
    
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