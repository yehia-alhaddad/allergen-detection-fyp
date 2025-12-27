from typing import List, Dict
import torch
from torch.utils.data import Dataset


class NERDataset(Dataset):
    def __init__(self, samples: List[Dict], vocab: Dict[str, int], label2id: Dict[str, int]):
        self.samples = samples
        self.vocab = vocab
        self.label2id = label2id

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        item = self.samples[idx]
        tokens = [self.vocab.get(t.lower(), self.vocab.get("<unk>", 0)) for t in item["tokens"]]
        labels = [self.label2id[item_label] for item_label in item["labels"]]
        return torch.tensor(tokens, dtype=torch.long), torch.tensor(labels, dtype=torch.long)
