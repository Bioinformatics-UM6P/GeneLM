# --------------------------------------------------------------
# IMPORT 
# --------------------------------------------------------------
import numpy as np
import pandas as pd
import os, csv, copy, json, logging, sys
from dataclasses import dataclass, field
from typing import Any, Optional, Dict, Sequence, Tuple, List, Union
import random
from collections import Counter
import threading
import concurrent.futures

import torch, transformers, sklearn, datasets
from datasets import Dataset

from peft import (
    LoraConfig,
    get_peft_model,
    get_peft_model_state_dict,
)

import warnings
warnings.simplefilter("ignore", FutureWarning)

# --------------------------------------------------------------
# CUDA & File size 
# --------------------------------------------------------------
print("CUDA available:", torch.cuda.is_available())
maxInt = sys.maxsize
while True:
    try:
        csv.field_size_limit(maxInt)
        print(f"field size limit: {maxInt}")
        break
    except OverflowError:
        maxInt = int(maxInt/10)

# --------------------------------------------------------------
# CLASS ARGS 
# --------------------------------------------------------------
@dataclass
class ModelArguments:
    model_name_or_path: Optional[str] = field(default="facebook/opt-125m")
    use_lora: bool = field(default=False, metadata={"help": "whether to use LoRA"})
    lora_r: int = field(default=8, metadata={"help": "hidden dimension for LoRA"})
    lora_alpha: int = field(default=32, metadata={"help": "alpha for LoRA"})
    lora_dropout: float = field(default=0.05, metadata={"help": "dropout rate for LoRA"})
    lora_target_modules: str = field(default="query,value", metadata={"help": "where to perform LoRA"})

@dataclass
class DataArguments:
    data_path: str = field(default=None, metadata={"help": "Path to the training data."})
    data_folder: str = field(default="database", metadata={"help": "Type of database: either 'balanced' or 'database'"})
    kmer: int = field(default=-1, metadata={"help": "k-mer for input sequence. -1 means not using k-mer."})

@dataclass
class TrainingArguments(transformers.TrainingArguments):
    cache_dir: Optional[str] = field(default=None)
    run_name: str = field(default="run")
    optim: str = field(default="adamw_torch")
    model_max_length: int = field(default=512, metadata={"help": "Maximum sequence length."})
    gradient_accumulation_steps: int = field(default=1)
    per_device_train_batch_size: int = field(default=1)
    per_device_eval_batch_size: int = field(default=1)
    num_train_epochs: int = field(default=1)
    fp16: bool = field(default=False)
    logging_steps: int = field(default=100)
    save_steps: int = field(default=100)
    eval_steps: int = field(default=100)
    evaluation_strategy: str = field(default="steps"),
    warmup_steps: int = field(default=50)
    weight_decay: float = field(default=0.01)
    learning_rate: float = field(default=1e-4)
    save_total_limit: int = field(default=3)
    load_best_model_at_end: bool = field(default=False)
    output_dir: str = field(default="output")
    find_unused_parameters: bool = field(default=False)
    checkpointing: bool = field(default=False)
    dataloader_pin_memory: bool = field(default=False)
    eval_and_save_results: bool = field(default=True)
    save_model: bool = field(default=False)
    seed: int = field(default=42)
    nodes: int = field(default=1)
    do_eval: bool = field(default=True)
    data_load_batch_size: int = field(default=1)
    experimentation_id: str = field(default="Experimentation_id")
    confidence_level: float = field(default=0.1)
    unlabeled_data_path: str = field(default="/path/to/data")
    unlabeled_data_file_per_retrieval: int = field(default=2)

# --------------------------------------------------------------
# GENERAL UTILS 
# --------------------------------------------------------------
def init_logger(experimentation_id):
    exp_folder = f"./sbatchlogs/checkpoint/{experimentation_id}"
    os.makedirs(exp_folder, exist_ok=True)

    logger1 = logging.getLogger('basic logger')
    logger1.setLevel(logging.INFO)
    file_handler1 = logging.FileHandler(os.path.join(exp_folder, 'operations.log'))
    file_handler1.setLevel(logging.INFO)
    formatter1 = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
    file_handler1.setFormatter(formatter1)
    logger1.addHandler(file_handler1)

    logger2 = logging.getLogger('progress logger')
    logger2.setLevel(logging.INFO)
    file_handler2 = logging.FileHandler(os.path.join(exp_folder, 'train_state.log'))
    file_handler2.setLevel(logging.INFO)
    formatter2 = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
    file_handler2.setFormatter(formatter2)
    logger2.addHandler(file_handler2)

    return logger1, logger2

def read_json(path):
    with open(path, 'r') as json_file:
        data = json.load(json_file)
    return data

def safe_save_model_for_hf_trainer(trainer: transformers.Trainer, output_dir: str):
    """
    Collects the state dict and dump to disk.
    """
    state_dict = trainer.model.state_dict()
    if trainer.args.should_save:
        cpu_state_dict = {key: value.cpu() for key, value in state_dict.items()}
        del state_dict
        trainer._save(output_dir, state_dict=cpu_state_dict)  # noqa

def generate_kmer(sequences: list, labels: list, k: int, overlap:int=1, distributed_training:bool=False, chunck_size=100000, logger: logging = logging):
    """
    Generate k-mer string from DNA sequence.
    """
    # utils
    def kmer(sequence: str, k: int, overlap: int):
        return " ".join([sequence[j:j+k] for j in range(0, len(sequence) - k + 1, overlap)])
    
    if not distributed_training:
        return [kmer(sequences[i], k, overlap) for i in range(len(sequences))], labels
    else:
        rank = torch.distributed.get_rank()
        world_size = torch.distributed.get_world_size()

        if rank == 0:
            kmer_seq = [kmer(sequences[i], k, overlap) for i in range(len(sequences))]
        else:
            kmer_seq = None 

        # broadcast k-mer data from rank 0 to all other ranks
        kmer_list = [kmer_seq]
        torch.distributed.broadcast_object_list(kmer_list, src=0)
        kmer_seq = kmer_list[0]  
        
        # partition the data among ranks
        total_size  = len(kmer_seq)
        start_idx   = rank * (total_size // world_size)
        end_idx     = (rank + 1) * (total_size // world_size) if rank != world_size - 1 else total_size
        kmer_subset = kmer_seq[start_idx:end_idx]
        label_subset = labels[start_idx:end_idx]
        logger.warning(f"Rank {rank}: Assigned data indices {start_idx} to {end_idx}")
        return kmer_subset, label_subset

# --------------------------------------------------------------
# TRAINER UTILS
# --------------------------------------------------------------
class IterableDataset(torch.utils.data.IterableDataset):
    def __init__(
        self, base_folder: str, files_list: list, tokenizer, kmer: int = -1, nodes: int = 1, shuffle: bool = False, 
        batch_size: int = 10_000_000_000, logger: logging = logging, train_logger: logging = logging, db_type: str = "train", 
        data_count_save_path: str = "", checkpoint_idx_path: str = "",
        confidence_level: float = 0.1, unlabeled_data_path: str = "", unlabeled_data_file_per_retrieval: int = 2
    ):
        self.folder_path = base_folder
        self.tokenizer = tokenizer
        self.kmer = kmer
        self.nodes = nodes
        self.batch_size = batch_size
        self.files = sorted([os.path.join(self.folder_path, file) for file in files_list if file.endswith('.csv')])
        self.files_counts = len(self.files)
        self.shuffle = shuffle
        self.num_labels = None
        self.type = db_type
        self.logger = logger
        self.train_logger = train_logger
        self.save_event = threading.Event()
        self.save_pace = 50 # estimation for current df 80 save
        self.checkpoint_idx_path = checkpoint_idx_path
        self.special_recovery = (checkpoint_idx_path != "" and db_type == "train") # where have have to coninu training after src timeout
        self.data_count_save_path = data_count_save_path
        self.confidence_level = confidence_level
        self.unlabeled_data_path = unlabeled_data_path
        self.unlabeled_data_file_per_retrieval = unlabeled_data_file_per_retrieval
        self.unlabeled_checkpoint_path = data_count_save_path.replace("train_count.json", "unlabeled_checkpoint.json")
        #with open(self.unlabeled_checkpoint_path, 'w') as f:
        #    json.dump(1, f)

        if shuffle:
            from random import shuffle
            shuffle(self.files)

        # checkpoint train 
        # -----------------------
        if self.special_recovery:
            with open(self.checkpoint_idx_path, 'r') as f:
                last_checkpoint_idx = json.load(f)
            with open(self.checkpoint_idx_path, 'w') as f:
                json.dump(0, f)
        else:
            last_checkpoint_idx = 0
        self.last_checkpoint_idx = last_checkpoint_idx
        # -----------------------
        
        # Precompute dataset size
        self.total_size = self._compute_size(data_count_save_path)

    def count_lines_in_file(self, file):
        with open(file, 'r') as f:
            return sum(1 for _ in f) - 1

    def _compute_size(self, output_file_path):
        if self.type == "train" and self.last_checkpoint_idx != 0:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                line_counts = list(executor.map(self.count_lines_in_file, self.files[self.last_checkpoint_idx:]))
            return sum(line_counts)
        else:
            if os.path.exists(output_file_path):
                with open(output_file_path, 'r') as f:
                    saved_line_counts = json.load(f)
                return saved_line_counts
            else:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    line_counts = list(executor.map(self.count_lines_in_file, self.files[self.last_checkpoint_idx:]))
                total_line_count = sum(line_counts)
                with open(output_file_path, 'w') as f:
                    json.dump(total_line_count, f)
                return total_line_count            
    
    def __len__(self):
        return self.total_size

    def process_batch(self, batch):
        texts = batch["sequence"].tolist()
        labels = batch["label"].tolist()

        if self.kmer != -1:
            self.logger.warning(f"Generating {self.kmer}-mer...")
            texts, labels = generate_kmer(texts, labels, self.kmer, overlap=1, distributed_training=(self.nodes > 1))

        labels_tensor = torch.tensor(labels, dtype=torch.long)
        if self.num_labels is None:
            self.num_labels = len(set(labels))

        return {"input_ids": texts, "labels": labels_tensor}

    def __iter__(self):
        """ Iterate over CSV files and process them in chunks. """
        if self.type == "train" and self.last_checkpoint_idx == 0:
            self.train_logger.info(f"###"*20)
        if self.type == "train" and self.last_checkpoint_idx != 0:
            self.train_logger.info(f"Continue on same epoch...")

        for i, file in enumerate(self.files[self.last_checkpoint_idx:]):
            self.save_event.clear()
            self.logger.warning(f"Loading bacteria CSV: {os.path.basename(file)}")

            chunks = list(pd.read_csv(file, chunksize=self.batch_size))
            for idx, chunk in enumerate(chunks):
                chunk = chunk[~chunk["sequence"].isna()]
                if idx == len(chunks) - 1 and (i+1)%self.save_pace == 0:
                    if self.type == "train":
                        self.save_event.set()
                yield self.process_batch(chunk)
            
            if self.type == "train":
                self.train_logger.info(f"{i+1}/{self.files_counts} - Fully used {file} for training")
            if self.type == "train" and idx == len(chunks) - 1:
                self.save_event.clear()
            
        # end of epoch
        self.last_checkpoint_idx = 0
        # end of epoch: augment data with unlabeled
        # -----------------------------------------
        # with open(self.unlabeled_checkpoint_path, 'r') as f:
        #     unlabeled_idx = json.load(f)
        # new_data_path = [os.path.join(self.unlabeled_data_path, f"bacteria_{i}.csv") for i in range(unlabeled_idx, self.unlabeled_data_file_per_retrieval+unlabeled_idx+1)]
        # -----------------------------------------


                
class ModelSaveCallback(transformers.TrainerCallback):
    def __init__(self, dataset, trainer, output_dir):
        self.dataset = dataset
        self.trainer = trainer
        self.folder  = output_dir

    def on_step_end(self, args, state, control, **kwargs):
        if self.dataset.save_event.is_set():
            print("[Signal received]: Safe model saving ...")
            self.trainer.save_state()
            safe_save_model_for_hf_trainer(trainer=self.trainer, output_dir=self.folder+"-train_checkpoint")
        return control  

@dataclass
class CustomDataCollator(object):
    """
    Collate examples for supervised fine-tuning.
    """
    tokenizer: transformers.PreTrainedTokenizer

    def __call__(self, batch_instance: Sequence[Dict]):
        texts  = batch_instance[0]["input_ids"]
        labels = batch_instance[0]["labels"]

        # Tokenize the texts in the batch
        output = self.tokenizer(
            texts,
            return_tensors="pt",
            padding="longest",
            truncation=True,
            max_length=self.tokenizer.model_max_length
        )

        input_ids = output["input_ids"]
        attention_mask = output["attention_mask"]
        labels = torch.as_tensor(labels, dtype=torch.long)

        return dict(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )

# --------------------------------------------------------------
# EVAL UTILS
# --------------------------------------------------------------
def sklearn_metric(predictions: np.ndarray, labels: np.ndarray):
    valid_mask = labels != -100
    valid_predictions = predictions[valid_mask]
    valid_labels = labels[valid_mask]
    return {
        "accuracy": sklearn.metrics.accuracy_score(valid_labels, valid_predictions),
        "f1": sklearn.metrics.f1_score(
            valid_labels, valid_predictions, average="macro", zero_division=0
        ),
        "matthews_correlation": sklearn.metrics.matthews_corrcoef(
            valid_labels, valid_predictions
        ),
        "precision": sklearn.metrics.precision_score(
            valid_labels, valid_predictions, average="macro", zero_division=0
        ),
        "recall": sklearn.metrics.recall_score(
            valid_labels, valid_predictions, average="macro", zero_division=0
        ),
    }

def preprocess_logits_for_metrics(logits:Union[torch.Tensor, Tuple[torch.Tensor, Any]], _):
    # Unpack logits if it's a tuple
    if isinstance(logits, tuple):  
        logits = logits[0]

    # Reshape logits to 2D if needed
    if logits.ndim == 3:
        logits = logits.reshape(-1, logits.shape[-1])

    return torch.argmax(logits, dim=-1)

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    return sklearn_metric(predictions, labels)

# --------------------------------------------------------------
# TRAINING
# --------------------------------------------------------------
def train():
    parser = transformers.HfArgumentParser((ModelArguments, DataArguments, TrainingArguments))
    model_args, data_args, training_args = parser.parse_args_into_dataclasses()
    data_index = read_json(os.path.join(data_args.data_path, "data_index.json"))

    # init loggin dir
    logger1, progress_logger = init_logger(training_args.experimentation_id)

    # model
    model = transformers.AutoModelForSequenceClassification.from_pretrained(
        model_args.model_name_or_path,
        cache_dir=training_args.cache_dir,
        num_labels=2,
        trust_remote_code=True,
    )
    print(model)

    # tokenizer
    tokenizer = transformers.AutoTokenizer.from_pretrained(
        model_args.model_name_or_path,
        cache_dir=training_args.cache_dir,
        model_max_length=training_args.model_max_length,
        padding_side="right",
        use_fast=True,
        trust_remote_code=True,
    )

    # configure LoRA
    if model_args.use_lora:
        lora_config = LoraConfig(
            r=model_args.lora_r,
            lora_alpha=model_args.lora_alpha,
            target_modules=list(model_args.lora_target_modules.split(",")),
            lora_dropout=model_args.lora_dropout,
            bias="none",
            task_type="SEQ_CLS",
            inference_mode=False,
        )
        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()

    # init distributed training
    if torch.distributed.is_available():
        rank = torch.distributed.get_rank()
        world_size = torch.distributed.get_world_size()
        logger1.warning(f"Distributed training initialized: rank {rank}/{world_size}.")
    else:
        rank, world_size = 0, 1

    # utils for trainer
    data_count_path = f"./sbatchlogs/checkpoint/{training_args.experimentation_id}/"
    data_collator = CustomDataCollator(tokenizer=tokenizer)
    train_dataset = IterableDataset(
        base_folder=os.path.join(data_args.data_path, data_args.data_folder),
        files_list=data_index['train'],
        tokenizer=tokenizer, 
        kmer=data_args.kmer,
        nodes=training_args.nodes,
        shuffle=False, # to continue if toubkal time out 
        batch_size=training_args.data_load_batch_size,
        logger=logger1, 
        train_logger=progress_logger, 
        db_type="train",
        data_count_save_path=data_count_path+"train_count.json",
        #checkpoint_idx_path=data_count_path+"train_idx_checkpoint.json",
        confidence_level = training_args.confidence_level,
        unlabeled_data_path = training_args.unlabeled_data_path,
        unlabeled_data_file_per_retrieval = training_args.unlabeled_data_file_per_retrieval
    )
    eval_dataset = IterableDataset(
        base_folder=os.path.join(data_args.data_path, data_args.data_folder),
        files_list=data_index['dev'],
        tokenizer=tokenizer, 
        kmer=data_args.kmer,
        nodes=training_args.nodes,
        shuffle=False,
        batch_size=training_args.data_load_batch_size,
        logger=logger1, 
        db_type="dev",
        data_count_save_path=data_count_path+"eval_count.json"
    )
    test_dataset = IterableDataset(
        base_folder=os.path.join(data_args.data_path, data_args.data_folder),
        files_list=data_index['test'],
        tokenizer=tokenizer, 
        kmer=data_args.kmer,
        nodes=training_args.nodes,
        shuffle=False,
        batch_size=training_args.data_load_batch_size,
        logger=logger1, 
        db_type="test",
        data_count_save_path=data_count_path+"test_count.json"
    )

    # define trainer
    trainer = transformers.Trainer(
        model=model,
        tokenizer=tokenizer,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        preprocess_logits_for_metrics=preprocess_logits_for_metrics,
        compute_metrics=compute_metrics,
        data_collator=data_collator,
    )
    save_callback = ModelSaveCallback(dataset=train_dataset, trainer=trainer, output_dir=training_args.output_dir)
    trainer.add_callback(save_callback)
    trainer.train()

    if training_args.save_model:
        trainer.save_state()
        safe_save_model_for_hf_trainer(trainer=trainer, output_dir=training_args.output_dir)

    # get the evaluation results from trainer
    if training_args.eval_and_save_results:
        results_path = os.path.join(training_args.output_dir, "results", training_args.run_name)
        results = trainer.evaluate(eval_dataset=test_dataset)
        os.makedirs(results_path, exist_ok=True)
        with open(os.path.join(results_path, "eval_results.json"), "w") as f:
            json.dump(results, f)

if __name__ == "__main__":
    train()