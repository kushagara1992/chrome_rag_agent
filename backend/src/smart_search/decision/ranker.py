"""Result ranking."""
from typing import List
from datetime import datetime
from loguru import logger
from smart_search.decision.schemas import RankedResult, RankingStrategy

class Ranker:
    """Ranks results."""
    
    @staticmethod
    def rank_results(results, strategy="relevance", min_score=0.0):
        """Rank results."""
        filtered = [r for r in results if r.score >= min_score]
        logger.debug(f"Filtered to {len(filtered)} results")
        
        ranked = []
        for rank, result in enumerate(filtered, 1):
            if strategy == "relevance":
                final_score = result.score
            elif strategy == "recency":
                final_score = Ranker._calculate_recency_score(result.timestamp)
            else:
                rel = result.score
                rec = Ranker._calculate_recency_score(result.timestamp)
                final_score = 0.7 * rel + 0.3 * rec
            
            ranked_result = RankedResult(
                result=result,
                relevance_score=result.score,
                recency_score=Ranker._calculate_recency_score(result.timestamp),
                final_score=final_score,
                rank=rank
            )
            ranked.append(ranked_result)
        
        ranked.sort(key=lambda x: x.final_score, reverse=True)
        for i, r in enumerate(ranked, 1):
            r.rank = i
        
        return ranked
    
    @staticmethod
    def _calculate_recency_score(timestamp: datetime) -> float:
        """Calculate recency score."""
        age_days = (datetime.now() - timestamp).days
        
        if age_days < 1:
            return 1.0
        elif age_days < 7:
            return 0.8
        elif age_days < 30:
            return 0.6
        else:
            return 0.3
