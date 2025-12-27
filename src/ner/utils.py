from typing import List, Dict
from collections import Counter


def build_vocab(samples: List[Dict], min_freq: int = 1) -> Dict[str, int]:
    counter = Counter()
    for s in samples:
        counter.update([t.lower() for t in s["tokens"]])
    vocab = {"<pad>": 0, "<unk>": 1}
    for tok, freq in counter.items():
        if freq >= min_freq:
            vocab[tok] = len(vocab)
    return vocab


def encode_labels(label2id: Dict[str, int]) -> List[str]:
    id2label = [None] * len(label2id)
    for k, v in label2id.items():
        id2label[v] = k
    return id2label
