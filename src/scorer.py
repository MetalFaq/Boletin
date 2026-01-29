from typing import List
import re

def calculate_relevance_score(query: str, keywords: List[str]) -> int:
    """
    Calculates a score based on how many keywords from the guidelines
    appear in the user's query.
    """
    if not query or not keywords:
        return 0
        
    score = 0
    query_lower = query.lower()
    
    # Tokenize query simply
    query_tokens = set(re.findall(r'\w+', query_lower))
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        if keyword_lower in query_tokens:
            score += 2 # Exact word match bonus
        elif keyword_lower in query_lower:
            score += 1 # Partial phrase match
            
    return score
