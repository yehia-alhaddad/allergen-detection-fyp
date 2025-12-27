"""
Train robust NER model on augmented data with OCR noise.

Data format: text + character offsets → convert to BIO tags → train
This makes the model learn OCR error patterns generically.
"""

import json
import torch
import numpy as np
from pathlib import Path
from transformers import (
    AutoTokenizer, AutoModelForTokenClassification,
    TrainingArguments, Trainer, DataCollatorForTokenClassification
)
from datasets import Dataset
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

class RobustNERTrainer:
    """Train NER on augmented data with OCR noise."""
    
    def __init__(self, model_name="bert-base-uncased"):
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        logger.info(f"[Trainer] Using device: {self.device}")
    
    def convert_to_bio_format(self, text, entities):
        """Convert text + character offsets to BIO tags."""
        # Initialize all tokens as "O"
        tokens = text.split()
        bio_tags = ["O"] * len(tokens)
        
        # Track character positions
        char_pos = 0
        token_idx = 0
        token_char_pos = {}  # Map token index to character position
        
        for token in tokens:
            token_char_pos[token_idx] = char_pos
            char_pos += len(token) + 1  # +1 for space
            token_idx += 1
        
        # Apply entity tags
        for start, end, entity_type in entities:
            # Find which tokens overlap with this entity
            char_idx = 0
            for token_idx, token in enumerate(tokens):
                token_start = char_idx
                token_end = token_start + len(token)
                
                # Check if token overlaps with entity
                if token_start < end and token_end > start:
                    if token_start == start:
                        bio_tags[token_idx] = f"B-{entity_type}"
                    else:
                        bio_tags[token_idx] = f"I-{entity_type}"
                
                char_idx = token_end + 1
        
        return tokens, bio_tags
    
    def load_dataset(self, json_path):
        """Load dataset from JSON."""
        logger.info(f"[Trainer] Loading from {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        tokens_list = []
        tags_list = []
        
        for item in data:
            text = item.get('text', '')
            entities = item.get('entities', [])
            
            try:
                tokens, bio_tags = self.convert_to_bio_format(text, entities)
                
                # Validate
                if len(tokens) == len(bio_tags) and len(tokens) > 0:
                    tokens_list.append(tokens)
                    tags_list.append(bio_tags)
            except Exception as e:
                logger.warning(f"[Trainer] Skipping sample: {e}")
        
        logger.info(f"[Trainer] Converted {len(tokens_list)} samples to BIO format")
        
        # Get all unique tags
        all_tags = set()
        for tags in tags_list:
            all_tags.update(tags)
        all_tags = sorted(list(all_tags))
        
        self.tag2id = {tag: idx for idx, tag in enumerate(all_tags)}
        self.id2tag = {idx: tag for tag, idx in self.tag2id.items()}
        
        logger.info(f"[Trainer] Found {len(all_tags)} unique tags: {all_tags}")
        
        return Dataset.from_dict({
            'tokens': tokens_list,
            'tags': tags_list
        })
    
    def tokenize_and_align_labels(self, examples):
        """Tokenize and align labels."""
        tokenized_inputs = self.tokenizer(
            examples["tokens"],
            truncation=True,
            is_split_into_words=True,
            max_length=512,
            padding="max_length"
        )
        
        labels = []
        for i, label in enumerate(examples["tags"]):
            word_ids = tokenized_inputs.word_ids(batch_index=i)
            label_ids = []
            previous_word_idx = None
            
            for word_idx in word_ids:
                if word_idx is None:
                    label_ids.append(-100)  # Special tokens
                elif word_idx != previous_word_idx:
                    label_ids.append(self.tag2id.get(label[word_idx], 0))
                else:
                    label_ids.append(self.tag2id.get(label[word_idx], 0))
                previous_word_idx = word_idx
            
            labels.append(label_ids)
        
        tokenized_inputs["labels"] = labels
        return tokenized_inputs
    
    def train(self, train_path, val_path, output_dir, num_epochs=3, batch_size=8):
        """Train model."""
        
        # Load datasets
        train_dataset = self.load_dataset(train_path)
        val_dataset = self.load_dataset(val_path)
        
        # Initialize model
        logger.info(f"[Trainer] Initializing {self.model_name}")
        model = AutoModelForTokenClassification.from_pretrained(
            self.model_name,
            num_labels=len(self.tag2id),
            id2label=self.id2tag,
            label2id=self.tag2id,
            ignore_mismatched_sizes=True
        )
        model.to(self.device)
        
        # Tokenize
        logger.info("[Trainer] Tokenizing datasets...")
        train_tokenized = train_dataset.map(
            self.tokenize_and_align_labels,
            batched=True,
            remove_columns=["tokens", "tags"]
        )
        val_tokenized = val_dataset.map(
            self.tokenize_and_align_labels,
            batched=True,
            remove_columns=["tokens", "tags"]
        )
        
        # Training args
        training_args = TrainingArguments(
            output_dir=output_dir,
            eval_strategy="epoch",
            save_strategy="epoch",
            learning_rate=2e-5,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            num_train_epochs=num_epochs,
            weight_decay=0.01,
            save_total_limit=2,
            load_best_model_at_end=True,
            logging_steps=100,
            push_to_hub=False
        )
        
        # Trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_tokenized,
            eval_dataset=val_tokenized,
            data_collator=DataCollatorForTokenClassification(self.tokenizer),
            compute_metrics=self.compute_metrics
        )
        
        logger.info("[Trainer] Starting training on augmented OCR-noise data...")
        trainer.train()
        
        # Save
        final_dir = Path(output_dir) / "final_model"
        final_dir.mkdir(exist_ok=True)
        model.save_pretrained(final_dir)
        self.tokenizer.save_pretrained(final_dir)
        
        # Save config
        config = {
            'id2label': self.id2tag,
            'label2id': self.tag2id,
            'model_name': self.model_name,
            'training_mode': 'augmented_ocr_noise',
            'num_epochs': num_epochs
        }
        (final_dir / "config.json").write_text(
            json.dumps(config, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        
        logger.info(f"[Trainer] Model saved to {final_dir}")
        return trainer
    
    def compute_metrics(self, p):
        """Compute F1 score."""
        from seqeval.metrics import f1_score
        
        predictions, labels = p
        predictions = np.argmax(predictions, axis=2)
        
        true_predictions = [
            [self.id2tag[p] for (p, l) in zip(prediction, label) if l != -100]
            for prediction, label in zip(predictions, labels)
        ]
        true_labels = [
            [self.id2tag[l] for (p, l) in zip(prediction, label) if l != -100]
            for prediction, label in zip(predictions, labels)
        ]
        
        f1 = f1_score(true_labels, true_predictions)
        return {"f1": f1}


def main():
    """Train robust NER on augmented data."""
    root = Path(__file__).parent.parent
    
    # Use original balanced data (with our character offset format)
    # not the augmented JSON format from earlier
    train_path = root / "data" / "ner_training" / "train.json"
    val_path = root / "data" / "ner_training" / "val.json"
    output_dir = root / "models" / "ner_model_robust_v2"
    
    logger.info("[Main] TRAINING ROBUST NER MODEL")
    logger.info(f"[Main] Training data: {train_path}")
    logger.info(f"[Main] Validation data: {val_path}")
    logger.info(f"[Main] Output: {output_dir}")
    logger.info("")
    
    trainer = RobustNERTrainer()
    trainer.train(
        train_path=str(train_path),
        val_path=str(val_path),
        output_dir=str(output_dir),
        num_epochs=3,
        batch_size=8
    )
    
    logger.info("[Main] Training complete!")


if __name__ == "__main__":
    main()
