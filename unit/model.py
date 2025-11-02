import os
import re
import csv
import pandas as pd
from copy import deepcopy
from itertools import chain
from collections import Counter
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import json
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import KFold
from docx import Document
from transformers import BertTokenizerFast, DataCollatorWithPadding
from transformers import DataCollatorForTokenClassification
import random
from transformers import EarlyStoppingCallback
import torch.nn.functional as F
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
from sklearn.metrics import precision_score, recall_score
from datasets import Dataset
from seqeval.metrics import classification_report
from sklearn.metrics import precision_score, recall_score, f1_score
import numpy as np
from transformers import AutoTokenizer, AutoModelForTokenClassification, AdamW
from transformers import Trainer, TrainingArguments
from datasets import load_dataset
from transformers import BertTokenizer
from torch import nn
import torch

from sklearn.metrics import accuracy_score


number_of_labels = 21
directory = Args().dataset

data_files_path = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.json')]
dataset = load_dataset('json', data_files=data_files_path)


def add_target_mask(example):
    labels = example["labels"]
    target_mask = [1 if label != "O" else 0 for label in labels]
    example["target_mask"] = target_mask
    return example


dataset = dataset.map(add_target_mask)

label_list = [
    'O',
    'B-Membrane_Name',
    'I-Membrane_Name',
    'B-Membrane_Material',
    'I-Membrane_Material',
    'B-Fill_Name',
    'I-Fill_Name',
    'B-Fill_Ratio',
    'B-Ratio',
    'B-Temperature',
    'I-Temperature',
    'B-Pressure',
    'I-Pressure',
    'B-Gas',
    'B-Separation_factor',
    'B-Permeance',
    'B-Permeance_Unit',
    'I-Permeance_Unit',
    'B-Permeability',
    'B-Permeability_Unit',
    'B-Selectivity',
]

label_map = {
    'O': 0,
    'B-Membrane_Name': 1,
    'I-Membrane_Name': 2,
    'B-Membrane_Material': 3,
    'I-Membrane_Material': 4,
    'B-Fill_Name': 5,
    'I-Fill_Name': 6,
    'B-Fill_Ratio': 7,
    'B-Ratio': 8,
    'B-Temperature': 9,
    'I-Temperature': 10,
    'B-Pressure': 11,
    'I-Pressure': 12,
    'B-Gas': 13,
    'B-Separation_factor': 14,
    'B-Permeance': 15,
    'B-Permeance_Unit': 16,
    'I-Permeance_Unit': 17,
    'B-Permeability': 18,
    'B-Permeability_Unit': 19,
    'B-Selectivity': 20,
}

# Unit list
permeance_units = [
    "mol/m²/s/Pa",
    "cm³/cm²/s/Pa",
    "GPU",  # Gas Permeation Unit
    "barrer",
    "cmHg",
]

gas = [
    'CO2/N2',
    'H2/CO2',
    'CH4/CO2',
    'H2/CH4',
    'H2/N2',
    'C3H6/C3H8',
    'Xe/Kr',
    'O2/N2',
    'CO',
    'CO2',
    'H2',
    'N2',
    'CH4',
    'H2/O2',
    'CH4/N2',
    'O2',
]

id_to_label = {v: k for k, v in label_map.items()}
label2id = label_map
id2label = {v: k for k, v in label2id.items()}


def extract_membrane_names(dataset):
    def add_name_to_set(name_list, name_set):
        """Add the concatenated membrane name to the set and clear the temporary list."""
        if name_list:
            full_name = " ".join(name_list).strip()
            if '­' in full_name:
                name_list.clear()
                return
            # Ensure that the name is not a single special character.
            if not re.fullmatch(r'[%\.,@()/\[\]\-]', full_name):
                name_set.add(full_name)
            name_list.clear()

    membrane_names = set()
    for split in ['train', 'test']:
        for example in dataset.get(split, []):
            tokens = example['tokens']
            labels = example['labels']
            current_name = []
            for token, label in zip(tokens, labels):
                if label == "B-Membrane_Name":
                    add_name_to_set(current_name, membrane_names)
                    current_name.append(token)
                elif label == "I-Membrane_Name":
                    current_name.append(token)
                else:
                    add_name_to_set(current_name, membrane_names)
            add_name_to_set(current_name, membrane_names)
    return sorted(membrane_names)

# Extract membrane name
membrane_names = extract_membrane_names(dataset)


def save_membrane_names_to_file(membrane_names, filepath):
    with open(filepath, 'w', encoding='utf-8') as file:
        for name in membrane_names:
            file.write(name + "\n")


# Save membrane names to file
membrane_names_filepath = "membrane_names.txt"
save_membrane_names_to_file(membrane_names, membrane_names_filepath)


def extract_Fill_Name(dataset):
    def add_name_to_set(name_list, name_set):
        if name_list:
            name_set.add(" ".join(name_list))
            name_list.clear()

    membrane_Fill_Name = set()
    for split in ['train', 'test']:
        for example in dataset.get(split, []):
            tokens = example['tokens']
            labels = example['labels']
            current_name = []
            for token, label in zip(tokens, labels):
                if label == "B-Fill_Name":
                    add_name_to_set(current_name, membrane_Fill_Name)
                    current_name.append(token)
                elif label == "I-Fill_Name":
                    current_name.append(token)
                else:
                    add_name_to_set(current_name, membrane_Fill_Name)
            add_name_to_set(current_name, membrane_Fill_Name)
    return sorted(membrane_Fill_Name)


Fill_Name = extract_Fill_Name(dataset)

def extract_Membrane_Material(dataset):
    def add_name_to_set(name_list, name_set):
        if name_list:
            name_set.add(" ".join(name_list))
            name_list.clear()

    Membrane_Material = set()
    for split in ['train', 'test']:
        for example in dataset.get(split, []):
            tokens = example['tokens']
            labels = example['labels']
            current_name = []
            for token, label in zip(tokens, labels):
                if label == "B-Membrane_Material":
                    add_name_to_set(current_name, Membrane_Material)
                    current_name.append(token)
                elif label == "I-Membrane_Material":
                    current_name.append(token)
                else:
                    add_name_to_set(current_name, Membrane_Material)
            add_name_to_set(current_name, Membrane_Material)
    return sorted(Membrane_Material)


Membrane_Material = extract_Membrane_Material(dataset)

def save_Membrane_Material_to_file(Membrane_Material, filepath):
    with open(filepath, 'w', encoding='utf-8') as file:
        for name in Membrane_Material:
            file.write(name + "\n")



Membrane_Material_filepath = "Membrane_Material.txt"
save_Membrane_Material_to_file(Membrane_Material, Membrane_Material_filepath)


def extract_Ratio(dataset):
    def add_name_to_set(name_list, name_set):
        if name_list:
            name_set.add(" ".join(name_list))
            name_list.clear()

    Ratio = set()
    for split in ['train', 'test']:
        for example in dataset.get(split, []):
            tokens = example['tokens']
            labels = example['labels']
            current_name = []
            for token, label in zip(tokens, labels):
                if label == "B-Ratio":
                    add_name_to_set(current_name, Ratio)
                    current_name.append(token)
                elif label == "I-Ratio":
                    current_name.append(token)
                else:
                    add_name_to_set(current_name, Ratio)
            add_name_to_set(current_name, Ratio)
    return sorted(Ratio)


Ratio = extract_Ratio(dataset)


def save_Ratio_to_file(Ratio, filepath):
    with open(filepath, 'w', encoding='utf-8') as file:
        for name in Ratio:
            file.write(name + "\n")


Ratio_filepath = "Ratio.txt"
save_Ratio_to_file(Ratio, Ratio_filepath)


def extract_Separation_factor(dataset):
    def add_name_to_set(name_list, name_set):
        if name_list:
            name_set.add(" ".join(name_list))
            name_list.clear()

    Separation_factor = set()
    for split in ['train', 'test']:
        for example in dataset.get(split, []):
            tokens = example['tokens']
            labels = example['labels']
            current_name = []
            for token, label in zip(tokens, labels):
                if label == "B-Separation_factor":
                    add_name_to_set(current_name, Separation_factor)
                    current_name.append(token)
                elif label == "I-Separation_factor":
                    current_name.append(token)
                else:
                    add_name_to_set(current_name, Separation_factor)
            add_name_to_set(current_name, Separation_factor)
    return sorted(Separation_factor)


Separation_factor = extract_Separation_factor(dataset)

def save_Separation_factor_to_file(Separation_factor, filepath):
    with open(filepath, 'w', encoding='utf-8') as file:
        for name in Separation_factor:
            file.write(name + "\n")


Separation_factor_filepath = "Separation_factor.txt"
save_Separation_factor_to_file(Separation_factor, Separation_factor_filepath)


def extract_Fill_Ratio(dataset):
    def add_name_to_set(name_list, name_set):
        if name_list:
            name_set.add(" ".join(name_list))
            name_list.clear()

    Fill_Ratio = set()
    for split in ['train', 'test']:
        for example in dataset.get(split, []):
            tokens = example['tokens']
            labels = example['labels']
            current_name = []
            for token, label in zip(tokens, labels):
                if label == "B-Fill_Ratio":
                    add_name_to_set(current_name, Fill_Ratio)
                    current_name.append(token)
                elif label == "I-Fill_Ratio":
                    current_name.append(token)
                else:
                    add_name_to_set(current_name, Fill_Ratio)
            add_name_to_set(current_name, Fill_Ratio)
    return sorted(Fill_Ratio)


Fill_Ratio = extract_Fill_Ratio(dataset)


def save_Fill_Ratio_to_file(Fill_Ratio, filepath):
    with open(filepath, 'w', encoding='utf-8') as file:
        for name in Fill_Ratio:
            file.write(name + "\n")


Fill_Ratio_filepath = "Fill_Ratio.txt"
save_Fill_Ratio_to_file(Fill_Ratio, Fill_Ratio_filepath)


def load_token_library_from_files(
    name_file,
    fill_file,
    material_file=None,
    ratio_file=None,
    sep_factor_file=None,
    fill_ratio_file=None
):
    """Construct the token_library from multiple files: Name, Material, Ratio, and Factor"""
    token_library = {
        "Membrane_Name": [],
        "Fill_Name": [],
        "Membrane_Material": [],
        "Ratio": [],
        "Separation_factor": [],
        "Fill_Ratio": [],
    }

    def read_file(file_path):
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip()]
        return []

    token_library["Membrane_Name"] = read_file(name_file)
    token_library["Fill_Name"] = read_file(fill_file)
    token_library["Membrane_Material"] = read_file(material_file)
    token_library["Ratio"] = read_file(ratio_file)
    token_library["Separation_factor"] = read_file(sep_factor_file)
    token_library["Fill_Ratio"] = read_file(fill_ratio_file)

    return token_library


def extract_entities(tokens, labels):
    spans = []
    i = 0
    while i < len(labels):
        if labels[i].startswith("B-"):
            label_type = labels[i][2:]
            start = i
            i += 1
            while i < len(labels) and labels[i] == f"I-{label_type}":
                i += 1
            spans.append((start, i, label_type))
        else:
            i += 1
    return spans


def span_replace_augment(tokens, labels, token_library, disturb_labels, replace_labels, symbols, augmentation_ratio=0.3):
    """Entity replacement + symbol perturbation"""
    spans = extract_entities(tokens, labels)
    new_tokens = tokens[:]
    new_labels = labels[:]

    offset = 0
    for start, end, label_type in spans:
        real_start = start + offset
        real_end = end + offset
        if "B-" + label_type in replace_labels and random.random() < augmentation_ratio:
            candidates = token_library.get(label_type, [])
            replacement = random.choice(candidates)
            replacement_tokens = list(replacement) if isinstance(replacement, str) else replacement.split()

            replacement_len = len(replacement_tokens)
            original_len = end - start

            new_tokens[real_start:real_end] = replacement_tokens

            new_labels[real_start:real_end] = (
                    ["B-" + label_type] + ["I-" + label_type] * (replacement_len - 1)
            )

            offset += replacement_len - original_len

    for i, (token, label) in enumerate(zip(new_tokens, new_labels)):
        if label in disturb_labels and random.random() < augmentation_ratio * 0.5:
            symbol = random.choice(symbols)
            op = random.choice(["insert", "replace"])
            if op == "insert" and len(token) > 1:
                pos = random.randint(1, len(token) - 1)
                new_tokens[i] = token[:pos] + symbol + token[pos:]
            elif op == "replace":
                pos = random.randint(0, len(token) - 1)
                new_tokens[i] = token[:pos] + symbol + token[pos + 1:]

    return new_tokens, new_labels


def augment_data(
    dataset,
    token_library,
    disturb_labels=("B-Membrane_Name", "I-Membrane_Name", "B-Fill_Name", "I-Fill_Name"),
    replace_labels=( "B-Ratio", "B-Separation_factor", "B-Fill_Ratio"), # "B-Membrane_Material",
    replace_ratio=1.0,
    copy_times=3,
    symbols=None,
    seed=42,
    include_original=True,
):
    """Enhance samples containing labels in `replace_labels` by performing target replacement and symbol perturbation, with an option to retain the original samples"""
    if symbols is None:
        symbols = ["-", "/", "@", "(", ")", "[", "]"]
    random.seed(seed)

    aug_tokens, aug_labels = [], []

    for example in dataset:
        tokens = example["tokens"]
        labels = example["labels"]

        if include_original:
            aug_tokens.append(tokens)
            aug_labels.append(labels)

        sample_label_set = set(labels)
        if any(label in replace_labels for label in sample_label_set):
            for _ in range(copy_times):
                if random.random() < replace_ratio:
                    new_tokens, new_labels = span_replace_augment(
                        tokens=tokens,
                        labels=labels,
                        token_library=token_library,
                        disturb_labels=disturb_labels,
                        replace_labels=replace_labels,
                        symbols=symbols,
                        augmentation_ratio=0.3
                    )
                    aug_tokens.append(new_tokens)
                    aug_labels.append(new_labels)

    return Dataset.from_dict({"tokens": aug_tokens, "labels": aug_labels})


def tokenize_and_align_labels(examples):
    # Tokenization
    tokenized_inputs = tokenizer(
        examples['tokens'],
        truncation=True,
        padding=True,
        is_split_into_words=True,
        max_length=512
    )

    aligned_labels = []
    all_target_masks = []

    for i, label_sequence in enumerate(examples['labels']):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        label_ids = []
        target_mask = []

        numeric_labels = [label_map.get(label, -100) for label in label_sequence]
        previous_word_id = None

        for word_id in word_ids:
            if word_id is None:
                label_ids.append(-100)
                target_mask.append(0)
            elif word_id < len(numeric_labels):
                if word_id != previous_word_id:
                    label_id = numeric_labels[word_id]
                    label_ids.append(label_id)

                    if label_id == label_map.get("O", 0):
                        target_mask.append(0)
                    else:
                        target_mask.append(1)
                else:
                    if numeric_labels[word_id] == -100:
                        label_ids.append(-100)
                        target_mask.append(0)
                    else:
                        label_str = list(label_map.keys())[list(label_map.values()).index(numeric_labels[word_id])]
                        if label_str.startswith("B-"):
                            i_label_str = "I-" + label_str[2:]
                            if i_label_str in label_map:
                                label_ids.append(label_map[i_label_str])
                                target_mask.append(1)
                            else:
                                label_ids.append(-100)
                                target_mask.append(0)
                        else:
                            label_ids.append(-100)
                            target_mask.append(0)
            else:
                label_ids.append(-100)
                target_mask.append(0)

            previous_word_id = word_id

        aligned_labels.append(label_ids)
        all_target_masks.append(target_mask)

    tokenized_inputs["labels"] = aligned_labels
    tokenized_inputs["target_mask"] = all_target_masks
    return tokenized_inputs


def enforce_bio_constraints(tokens, labels):
    corrected_labels = []
    prev_label = "O"
    for token, label in zip(tokens, labels):
        if label.startswith("I-") and not (prev_label.startswith("B-") or prev_label.startswith("I-")):
            corrected_labels.append(label.replace("I-", "B-"))
        else:
            corrected_labels.append(label)
        prev_label = corrected_labels[-1]
    return corrected_labels


def make_model_contiguous(model):
    for param in model.parameters():
        if not param.is_contiguous():
            param.data = param.data.contiguous()


def compute_metrics(p):
    predictions, labels = p
    predictions = predictions.argmax(-1)

    true_preds = []
    true_labels = []

    for pred, label in zip(predictions, labels):
        for p_i, l_i in zip(pred, label):
            if l_i != -100:
                true_preds.append(p_i)
                true_labels.append(l_i)

    return {
        "eval_f1": f1_score(true_labels, true_preds, average="macro"),
        "eval_precision": precision_score(true_labels, true_preds, average="macro"),
        "eval_recall": recall_score(true_labels, true_preds, average="macro")
    }


model_name = "scibert_scivocab_cased"

tokenizer = AutoTokenizer.from_pretrained(model_name)

# Add domain-specific terms to the model's vocabulary
tokenizer.add_tokens(membrane_names)

tokenizer.add_tokens(Fill_Name)

tokenizer.add_tokens(permeance_units)

tokenizer.add_tokens(gas)


class CustomTrainerWithMixedLoss(Trainer):
    def __init__(
        self,
        *args,
        class_weights=None,
        gamma=2.0,
        loss_alpha=None,
        mix_ratio=0.5,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights
        self.gamma = gamma
        self.loss_alpha = loss_alpha if loss_alpha is not None else class_weights
        self.mix_ratio = mix_ratio

    def focal_loss(self, logits, labels):
        device = logits.device
        num_labels = logits.size(-1)

        logits_flat = logits.view(-1, num_labels)
        labels_flat = labels.view(-1)

        labels_flat_masked = labels_flat.clone()
        labels_flat_masked[labels_flat_masked == -100] = 0

        log_probs = nn.functional.log_softmax(logits_flat, dim=-1)
        probs = torch.exp(log_probs)

        labels_one_hot = torch.zeros_like(log_probs).to(device)
        labels_one_hot.scatter_(1, labels_flat_masked.unsqueeze(1), 1)

        pt = (probs * labels_one_hot).sum(dim=1)
        log_pt = (log_probs * labels_one_hot).sum(dim=1)

        if self.loss_alpha is not None:
            alpha = self.loss_alpha.to(device)
            at = (alpha * labels_one_hot).sum(dim=1)
        else:
            at = torch.ones_like(pt)

        loss = -at * ((1 - pt) ** self.gamma) * log_pt

        ignore_mask = labels_flat == -100
        loss = loss.masked_fill(ignore_mask, 0.0)

        valid_count = (~ignore_mask).sum()
        return loss.sum() / valid_count.clamp(min=1)

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits

        ce_loss_fct = nn.CrossEntropyLoss(weight=self.class_weights, ignore_index=-100)
        ce_loss = ce_loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))

        # Focal Loss
        focal_loss = self.focal_loss(logits, labels)

        # Weighted combination
        total_loss = self.mix_ratio * focal_loss + (1 - self.mix_ratio) * ce_loss

        return (total_loss, outputs) if return_outputs else total_loss


def train_model(tokenized_dataset, model, tokenizer, fold, class_weights): # 改class_weights_tensor
    from transformers import Trainer, TrainingArguments

    training_args = TrainingArguments(
        output_dir=f"MembraneBERT/fold_{fold}",
        num_train_epochs=5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        weight_decay=0.05,
        logging_dir=f"./logs/fold_{fold}",

        logging_strategy="steps",
        logging_steps=10,

        evaluation_strategy="epoch",
        report_to="none",
        save_strategy="epoch",
        save_total_limit=1,
        label_smoothing_factor=0.05,
        learning_rate=3e-5,

        lr_scheduler_type="cosine",
        warmup_ratio=0.1,
        load_best_model_at_end=True,
        metric_for_best_model="eval_f1",
        greater_is_better=True,
    )

    data_collator = DataCollatorForTokenClassification(tokenizer)
    # Initialize Trainer
    trainer = CustomTrainerWithMixedLoss(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset['train'],
        eval_dataset=tokenized_dataset['test'],
        data_collator=data_collator,
        tokenizer=tokenizer,
        class_weights=class_weights,
        ###############################################
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
        gamma=2.0,
        loss_alpha=class_weights,
        mix_ratio=0.5
    )

    trainer.train()
    predictions, labels, metrics = trainer.predict(tokenized_dataset['test'])
    true_labels_list = []
    pred_labels_list = []
    token_list = []

    predictions = np.argmax(predictions, axis=2)

    for i in range(len(predictions)):
        input_tokens = tokenized_dataset['test'][i]['tokens']
        mask = tokenized_dataset['test'][i]['target_mask']

        true_labels = [id_to_label[label] for label, m in zip(labels[i], mask) if label != -100 and m == 1]
        raw_pred_labels = [id_to_label[pred] for pred, label, m in zip(predictions[i], labels[i], mask) if
                           label != -100 and m == 1]
        masked_tokens = [token for token, m in zip(input_tokens, mask) if m == 1]

        if len(true_labels) == len(raw_pred_labels) and len(true_labels) > 0:
            true_labels_list.append(true_labels)
            pred_labels_list.append(raw_pred_labels)
            token_list.append(masked_tokens)

    test_report = classification_report(true_labels_list, pred_labels_list, output_dict=True)
    f1_val = test_report['micro avg']['f1-score'] if 'micro avg' in test_report else 0.0
    print("f1_val")
    print(f1_val)

    return f1_val


def random_sample_indices(dataset, val_ratio=0.2, seed=42):
    random.seed(seed)
    all_indices = list(range(len(dataset)))
    random.shuffle(all_indices)

    val_size = int(len(dataset) * val_ratio)
    val_indices = all_indices[:val_size]
    train_indices = all_indices[val_size:]

    return train_indices, val_indices


if 'train' in dataset:
    all_data = dataset['train']
    if isinstance(all_data, list):
        train_data = Dataset.from_dict(all_data)

    all_labels = list(chain.from_iterable(example['labels'] for example in all_data))
    unique_labels = sorted(set(label for label in all_labels if label != -100))

    label2id = label_map
    id2label = {v: k for k, v in label2id.items()}
    number_of_labels = len(label2id)

    train_idx, val_idx = random_sample_indices(all_data, val_ratio=0.2, seed=42)
    train_fold = all_data.select(train_idx)
    val_fold = all_data.select(val_idx)

    # Data augmentation
    token_library = load_token_library_from_files("membrane_names.txt", "membrane_Fill_Name.txt", "Membrane_Material.txt", "Ratio.txt", "Separation_factor.txt", "Fill_Ratio.txt")
    tokenized_train = augment_data(
        dataset=train_fold,
        token_library=token_library,
        disturb_labels=("B-Membrane_Name", "I-Membrane_Name", "B-Fill_Name", "I-Fill_Name"),
        replace_labels=( "B-Membrane_Material", "I-Membrane_Material", "B-Ratio", "B-Separation_factor", "B-Fill_Ratio"),
        copy_times=50
    )
    tokenized_test = val_fold
    tokenized_train = tokenized_train.map(tokenize_and_align_labels, batched=True)
    tokenized_test = tokenized_test.map(tokenize_and_align_labels, batched=True)


    tokenized_dataset = {
        'train': tokenized_train,
        'test': tokenized_test
    }

    ignore_index = -100
    min_weight = 0.2
    max_weight = 3.0
    o_weight = 0.1

    all_labels = []
    for example in tokenized_dataset["train"]:
        labels = example["labels"]
        all_labels.extend([label for label in labels if label != ignore_index])

    label_counts = Counter(all_labels)

    label_count_list = [label_counts.get(i, 1) for i in range(len(label2id))]
    counts_tensor = torch.tensor(label_count_list, dtype=torch.float)

    weights = 1.0 / counts_tensor
    weights = weights / weights.sum() * len(weights)
    weights = torch.clamp(weights, min=min_weight, max=max_weight)
    ###############################################
    boost_factor = 1.5

    # for label_name in ['B-Membrane_Material', 'I-Membrane_Material']:
    #     idx = label2id.get(label_name)
    #     if idx is not None:
    #         weights[idx] = min(weights[idx] * boost_factor, max_weight)

    o_index = label2id.get('O', None)
    if o_index is not None:
        weights[o_index] = o_weight

    class_weights = weights

    model = AutoModelForTokenClassification.from_pretrained(
        model_name,
        num_labels=len(label2id),
        id2label=id2label,
        label2id=label2id
    )


    model.config.label2id = label2id
    model.config.id2label = id2label
    model.config.num_labels = len(label2id)
    model.resize_token_embeddings(len(tokenizer))

    train_model(tokenized_dataset, model, tokenizer, fold=0, class_weights=class_weights)

else:
    raise ValueError("Training dataset not found!")
