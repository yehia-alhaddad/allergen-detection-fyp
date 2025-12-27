from typing import List, Dict


class AllergenDetector:
    def __init__(self, synonym_mapper, predictor, confidence_scorer):
        self.synonym_mapper = synonym_mapper
        self.predictor = predictor
        self.confidence_scorer = confidence_scorer

    def detect(self, tokens: List[str]) -> Dict:
        # Prepare input tensor externally in pipeline; here assume tokens already id-encoded
        # This is a facade; real integration will combine NER outputs with rules
        ner_labels = self.predictor.predict(tokens)[0]  # single sample
        ner_allergens = set()
        for tok, label in zip(tokens[0], ner_labels):
            if label.endswith("ALLERGEN"):
                ner_allergens.update(self.synonym_mapper.match(str(tok)))

        text_joined = " ".join([str(t) for t in tokens[0]])
        rule_allergens = self.synonym_mapper.match(text_joined)

        ner_conf = 1.0 if ner_allergens else 0.0
        rule_conf = 1.0 if rule_allergens else 0.0
        conf = self.confidence_scorer.score(ner_conf, rule_conf)

        return {
            "ner_allergens": sorted(ner_allergens),
            "rule_allergens": sorted(rule_allergens),
            "confidence": conf,
        }
