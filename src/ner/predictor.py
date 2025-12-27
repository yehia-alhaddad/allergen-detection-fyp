from typing import List
import torch


class Predictor:
    def __init__(self, model: torch.nn.Module, id2label: List[str]):
        self.model = model
        self.id2label = id2label

    def predict(self, x: torch.Tensor) -> List[List[str]]:
        self.model.eval()
        with torch.no_grad():
            logits = self.model(x)
            preds = logits.argmax(-1)
        return [[self.id2label[i.item()] for i in row] for row in preds]
