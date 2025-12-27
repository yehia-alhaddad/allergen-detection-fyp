from typing import Dict


class ConfidenceScorer:
    def __init__(self, weights: Dict[str, float] | None = None):
        self.weights = weights or {"ner": 0.7, "rules": 0.3}

    def score(self, ner_conf: float, rule_conf: float) -> float:
        return self.weights["ner"] * ner_conf + self.weights["rules"] * rule_conf
