from typing import Iterable
import torch
from torch.utils.data import DataLoader
import torch.nn as nn
from torch.optim import Adam


class Trainer:
    def __init__(self, model: torch.nn.Module, lr: float = 1e-3):
        self.model = model
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = Adam(model.parameters(), lr=lr)

    def train_epoch(self, dataloader: DataLoader) -> float:
        self.model.train()
        total_loss = 0.0
        for x, y in dataloader:
            logits = self.model(x)
            # flatten time dimension for loss
            loss = self.criterion(logits.view(-1, logits.shape[-1]), y.view(-1))
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            total_loss += loss.item()
        return total_loss / max(1, len(dataloader))

    def eval_epoch(self, dataloader: DataLoader) -> float:
        self.model.eval()
        total_loss = 0.0
        with torch.no_grad():
            for x, y in dataloader:
                logits = self.model(x)
                loss = self.criterion(logits.view(-1, logits.shape[-1]), y.view(-1))
                total_loss += loss.item()
        return total_loss / max(1, len(dataloader))
