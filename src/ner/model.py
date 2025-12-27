from typing import Tuple
import torch
import torch.nn as nn


class BiLSTMCRF(nn.Module):
    def __init__(self, vocab_size: int, tagset_size: int, embedding_dim: int = 100, hidden_dim: int = 128):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim // 2, bidirectional=True, batch_first=True)
        self.fc = nn.Linear(hidden_dim, tagset_size)
        # Simplified: using cross-entropy instead of full CRF for stub

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        emb = self.embedding(x)
        out, _ = self.lstm(emb)
        logits = self.fc(out)
        return logits
