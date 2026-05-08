from typing import Tuple, Optional, List

class PostprocessingLayer:
    def __init__(self, threshold: float = 0.80, min_margin: float = 0.03):
        self.threshold = threshold
        self.min_margin = min_margin

    def decide(self, results: List[tuple]) -> Tuple[Optional[str], float, bool]:
        """
        results: list of tuples (name, similarity) sorted descending.
        Returns (name_or_None, confidence, recognized_bool)
        """
        if not results:
            return None, 0.0, False

        top_name, top_score = results[0]
        second_score = results[1][1] if len(results) > 1 else None
        if second_score is None:
            margin_ok = True
        else:
            margin_ok = (top_score - second_score) >= self.min_margin

        recognized = (top_score >= self.threshold) and margin_ok
        return top_name, top_score, recognized
