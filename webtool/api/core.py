import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
from pathlib import Path
import orfipy_core as oc
from Bio import SeqIO
import logging
from uuid import uuid4
import pandas as pd
import datetime
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio
import numpy as np
import os, re, json, gzip, subprocess
from itertools import groupby
import traceback

OUTPUT_DIR = Path("./__files__/results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class AnnotatorPipeline:
    def __init__(self):
        """Initialize models"""
        self.device = torch.cuda.current_device() if torch.cuda.is_available() else 'cpu'
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.batch_size = self.get_optimal_batch_size()
        
        model_cds_checkpoint = "Genereux-akotenou/BacteriaCDS-DNABERT-K6-89M"
        model_tis_checkpoint = "Genereux-akotenou/BacteriaTIS-DNABERT-K6-89M"
        self.model_cds = AutoModelForSequenceClassification.from_pretrained(model_cds_checkpoint).to(self.device)
        self.model_tis = AutoModelForSequenceClassification.from_pretrained(model_tis_checkpoint).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_cds_checkpoint)
        
        logging.info(f"Inference using: {self.device}\n")
        logging.info(f"Optimal batch size: {self.batch_size}")
        
    def get_optimal_batch_size(self):
        if str(self.device.type) == "cuda":
            gpu_properties = torch.cuda.get_device_properties(self.device)
            total_memory = gpu_properties.total_memory // (1024 ** 2)
            free_memory = torch.cuda.mem_get_info()[0] // (1024 ** 2)

            logging.info(f"GPU Total Memory: {total_memory} MB, Free Memory: {free_memory} MB")

            # estimate batch size based on free memory 
            base_batch_size = 64
            memory_per_sample = 15
            max_batch_size = free_memory // memory_per_sample
            optimal_batch_size = min(max_batch_size, 2048)
            return max(optimal_batch_size, 16)
        else:
            return 32
        
    def _generate_kmer(self, sequence: str, k: int, overlap: int = 1):
        return " ".join([sequence[j:j+k] for j in range(0, len(sequence) - k + 1, overlap)])
    
    def _extract_dna(self, sequence, start_pos=None, end_pos=None):
        if start_pos is not None and end_pos is not None:
            return sequence[start_pos:end_pos]
        return sequence
    
    def _update_progress(self, tasks, uuid, progress=0, status="Processing", result=None, state_key=None, state_value=None):
        tasks[uuid]["progress"] = progress
        tasks[uuid]["status"] = status
        if result != None:
            tasks[uuid]["result"] = result
        if state_key != None:
            tasks[uuid]["exec_state"][state_key] = state_value
        
    def _parse_orfs(self, input_data):
        orfs_pos, orfs_neg = [], []
        orf_data = input_data.strip().split('>')[1:]
        
        for entry in orf_data:
            lines = entry.splitlines()
            header = lines[0]
            sequence = ''.join(lines[1:])
            
            # extract start, end, strand, frame, length, start codon, end codon from the header using regex
            match = re.search(r'(\d+)-(\d+)\]\((\+|-)\) type:complete length:(\d+) frame:(-?\d+) start:(\w{3}) stop:(\w{3})', header)
            if match:
                start = int(match.group(1))
                end = int(match.group(2))
                strand = match.group(3)
                length = int(match.group(4))
                frame = int(match.group(5))
                start_codon = match.group(6)
                end_codon = match.group(7)

                if strand == "+":
                    orfs_pos.append({
                        'start': start,
                        'end': end,
                        'strand': strand,
                        'length': length,
                        'frame': frame,
                        'start_codon': start_codon,
                        'end_codon': end_codon,
                        'sequence': sequence
                    })
                elif strand == "-":
                    orfs_neg.append({
                        'start': start,
                        'end': end,
                        'strand': strand,
                        'length': length,
                        'frame': frame,
                        'start_codon': start_codon,
                        'end_codon': end_codon,
                        'sequence': sequence
                    })
        
        return orfs_pos, orfs_neg

    def _prediction(self, model, tokenizer, sequences):
        torch.cuda.empty_cache()
        batch_size = int(self.batch_size/2)
        predictions = []
        
        for i in tqdm(range(0, len(sequences), batch_size), desc="CDS Prediction"):
            batch_sequences = sequences[i:i+batch_size]
            
            # tokenize the batch
            inputs = tokenizer(
                batch_sequences,
                return_tensors="pt",
                max_length=tokenizer.model_max_length,
                padding="max_length",
                truncation=True
            )
            inputs = {key: val.to(self.device) for key, val in inputs.items()}
            
            # predictions
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                predicted_classes = torch.argmax(logits, dim=-1).tolist()
            
            # Collect predictions
            predictions.extend(predicted_classes)

        return predictions
    
    def _prediction_with_logits(self, model, tokenizer, sequences):
        torch.cuda.empty_cache()
        batch_size = int(self.batch_size/2)
        all_logits  = []
        
        for i in tqdm(range(0, len(sequences), batch_size), desc="TIS Prediction"):
            batch_sequences = sequences[i:i+batch_size]
            
            # tokenize the batch
            inputs = tokenizer(
                batch_sequences,
                return_tensors="pt",
                max_length=tokenizer.model_max_length,
                padding="max_length",
                truncation=True
            )
            inputs = {key: val.to(self.device) for key, val in inputs.items()}
            
            # predictions
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits.cpu().numpy()
            
            all_logits.extend(logits)

        return all_logits

    def _cds_input_parser(self, orfs_dict, strand, max_seq_len=510):
        results = []
        if strand == "+":
            positive_orfs   = orfs_dict
            grouped = groupby(sorted(positive_orfs, key=lambda x: x['end']), key=lambda x: x['end'])
            for end_value, group in grouped:
                group = list(group)
                orf = max(group, key=lambda x: x['length'])
                intermediate_starts = [g['start'] for g in group]
                
                if orf['length'] > 100:
                    results.append({
                        "start": orf["start"],
                        "end": orf["end"], 
                        "strand": orf["strand"], 
                        "intermediate_start": intermediate_starts,
                        "start_codon": orf["start_codon"], 
                        "end_codon": orf["end_codon"], 
                        "sequence": self._generate_kmer(orf["sequence"][-max_seq_len:], k=6, overlap=3)
                    })                    
        elif strand == "-":
            negative_orfs   = orfs_dict
            grouped = groupby(sorted(negative_orfs, key=lambda x: x['start']), key=lambda x: x['start'])            
            for start_value, group in grouped:
                group = list(group)
                orf = max(group, key=lambda x: x['length'])
                intermediate_end = [g['end'] for g in group]
                
                if orf['length'] > 100:
                    results.append({
                        "start": orf["start"], 
                        "end": orf["end"], 
                        "strand": orf["strand"], 
                        "intermediate_end": intermediate_end,
                        "start_codon": orf["start_codon"], 
                        "end_codon": orf["end_codon"], 
                        "sequence": self._generate_kmer(orf["sequence"][-max_seq_len:], k=6, overlap=3)
                    })
        return results

    def _tis_input_parser(self, dna_seq, orfs_dict, strand, tis_window=30):
        results = []
        if strand == "+":
            positive_orfs = orfs_dict
            group = 0
            for orf_group in positive_orfs:
                group += 1
                potential_tis_sites = orf_group["intermediate_start"]
                for orf_start in potential_tis_sites:
                    results.append({
                        "sequence": self._generate_kmer(
                            self._extract_dna(dna_seq, orf_start-tis_window, orf_start+tis_window),
                            k=6,
                            overlap=1
                        ),
                        "orf_group": "P"+str(group),
                        "strand": orf_group["strand"],
                        "start": orf_start, 
                        "end": orf_group["end"]
                    })
        elif strand == "-":
            negative_orfs = orfs_dict
            group = 0
            for orf_group in negative_orfs:
                group += 1
                potential_tis_sites = orf_group["intermediate_end"]
                for orf_end in potential_tis_sites:
                    results.append({
                        "sequence": self._generate_kmer(
                            self._extract_dna(dna_seq, -(orf_end+tis_window), -(orf_end-tis_window)),
                            k=6,
                            overlap=1
                        ), 
                        "orf_group": "N"+str(group),
                        "strand": orf_group["strand"],
                        "start": orf_group["start"], 
                        "end": orf_end
                    })
        return results

    def _save_output(self, df: pd.DataFrame, output_format: str, file_path: Path, task_uuid: str):
        output_file = OUTPUT_DIR / f"{file_path.stem}.{output_format.lower()}"
        
        df = df[df["prediction_max_likelihood"] == 1].copy()
        df["start"] = df["start"].astype(int)
        df["start"] = df["start"] + 1
        # df = df.sort_values(by="start", ascending=True)
        df = df.sort_values(by=["seq_id", "start"], ascending=[True, True])
        
        if output_format.upper() == "CSV":
            df.drop(columns=["sequence"], inplace=True)
            df["annotation"] = "NonCDS"
            df.loc[df["prediction_max_likelihood"] == 1, "annotation"] = "CDS"
            df[["seq_id", "annotation", "prediction_max_likelihood", "start", "end", "strand", "orf_group", "prob_cls0", "prob_cls1", "logit_cls0", "logit_cls1"]].to_csv(output_file, index=False)
        elif output_format.upper() == "GFF":
            with output_file.open("w") as f:
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write("##gff-version 3\n")
                f.write(f"##Generated using GeneLM, {current_time}\n")
                f.write(f"##Project Name: test_{str(task_uuid).split('-')[-2]}\n")
                f.write(f"##Job Id: {task_uuid}\n")
                f.write(f"##Tool: GeneLM\n")

                for _, row in df.iterrows():
                    if row['prediction_max_likelihood'] == 1:
                        gff_line = "\t".join([
                            row["seq_id"],
                            "GeneLM",
                            "CDS",
                            str(row["start"]),
                            str(row["end"]),
                            f"{row['prob_cls1']:.4f}",
                            row["strand"],
                            ".",
                            f"ID=orf_{row['orf_group']};Logit_cls0={row['logit_cls0']:.4f};Logit_cls1={row['logit_cls1']:.4f};Prob_cls0={row['prob_cls0']:.4f};Prob_cls1={row['prob_cls1']:.4f};Prediction={row['prediction_max_likelihood']}"
                        ])
                        f.write(gff_line + "\n")
        else:
            raise ValueError("Invalid output format. Choose 'CSV' or 'GFF'.")
        
        return output_file

    def pipeline(self, file_path: Path, output_format: str, tasks: dict, task_uuid: str, logging: logging) -> Path:
        """Runs annotation and updates progress in real-time."""
        
        try:
            # 1. read input file
            self._update_progress(tasks, task_uuid, progress=10, status="Start", result="...", state_key="Start", state_value=0)
            with open(file_path, 'rt') as f:
                fna_data = list(SeqIO.parse(f, "fasta"))
            self._update_progress(tasks, task_uuid, progress=10, status="Start", result="...", state_key="Start", state_value=100)
                
            # NewPatch: ensure only DNA Fasta (not protein)
            valid_dna_chars = set("ACGTUNacgtun")
            for record in fna_data:
                seq_set = set(str(record.seq))
                if not seq_set.issubset(valid_dna_chars):
                    raise ValueError(
                        f"Input FASTA appears to contain non-DNA characters in record '{record.id}'. "
                        "Please provide a nucleotide FASTA file (DNA/RNA, not protein)."
                    )
                    
            # 2. orf extraction
            results = []
            all_bacteria = ""
            for record in fna_data:
                self._update_progress(tasks, task_uuid, progress=20, status="Generating ORF", result="...", state_key="ORF", state_value=1)
                df_list  = []
                seq      = str(record.seq)
                seq_rc   = str(record.seq.reverse_complement())
                bacteria = record.description.split(" ")[0] if record.description.split(" ")[0] != "" else str(uuid4())
                orfs     = oc.start_search(
                    seq,                           #seq
                    seq_rc,                        #seq_rc
                    bacteria,                      #seqname
                    10,                            #minlen
                    10000000,                      #maxlen
                    'b',                           #strand
                    ['TTG', 'CTG', 'ATG', 'GTG'],  #starts
                    ['TAA', 'TAG', 'TGA'],         #stops
                    '1',                           #table
                    True,                          #include_stop
                    False,                         #partial3
                    False,                         #partial5
                    False,                         #between_stops
                    True,                          #nested
                    [False,False,True,False,False] #[bed12, bed, dna, rna, pep]
                )
                self._update_progress(tasks, task_uuid, progress=20, status="Generating ORF", result="...", state_key="ORF", state_value=100)
                orfs_pos_dict, orfs_neg_dict = self._parse_orfs(orfs[2])
                
                # 3. tokenize cds input
                self._update_progress(tasks, task_uuid, progress=40, status="Doing Tokenization", result="...", state_key="Tokenization", state_value=1)
                df1 = self._cds_input_parser(orfs_pos_dict, "+")
                df2 = self._cds_input_parser(orfs_neg_dict, "-")
                seq_cds_pos = [orf["sequence"] for orf in df1]
                seq_cds_neg = [orf["sequence"] for orf in df2]
                self._update_progress(tasks, task_uuid, progress=40, status="Doing Tokenization", result="...", state_key="Tokenization", state_value=100)
                
                # 4. CDS_Classification
                self._update_progress(tasks, task_uuid, progress=60, status="Fist Stage CDS Classification", result="...", state_key="CDS_Classification", state_value=1)
                prediction_cds_pos = self._prediction(self.model_cds, self.tokenizer, seq_cds_pos)
                self._update_progress(tasks, task_uuid, progress=60, status="Fist Stage CDS Classification", result="...", state_key="CDS_Classification", state_value=50)
                prediction_cds_neg = self._prediction(self.model_cds, self.tokenizer, seq_cds_neg)
                self._update_progress(tasks, task_uuid, progress=60, status="Fist Stage CDS Classification", result="...", state_key="CDS_Classification", state_value=100)
                predicted_cds_pos = [d for pred, d in zip(prediction_cds_pos, df1) if pred == 1]
                predicted_cds_neg = [d for pred, d in zip(prediction_cds_neg, df2) if pred == 1]
                
                # 5. TIS_Refinement
                self._update_progress(tasks, task_uuid, progress=80, status="Second Stage TIS Refinement", result="...", state_key="TIS_Refinement", state_value=1)
                df1 = self._tis_input_parser(seq, predicted_cds_pos, "+")
                df2 = self._tis_input_parser(seq_rc, predicted_cds_neg, "-")
                df_list.extend(df1)
                df_list.extend(df2)
                df = pd.DataFrame(df_list, columns=["sequence", "orf_group", "strand", "start", "end"])
                
                seq_kmer_tis = [row["sequence"] for i,row in df.iterrows()]
                all_logits = self._prediction_with_logits(self.model_tis, self.tokenizer, seq_kmer_tis)
                all_data = []
                for logit in all_logits:
                    probs = (np.exp(logit) / np.sum(np.exp(logit))).tolist()
                    all_data.append(logit.tolist() + probs + [0 if probs[0] > probs[1] else 1])
                df_metrics  = pd.DataFrame(all_data, columns=["logit_cls0", "logit_cls1", "prob_cls0", "prob_cls1", "pred_classic"])
                df_combined = pd.concat([df.reset_index(drop=True), df_metrics.reset_index(drop=True)], axis=1)
                self._update_progress(tasks, task_uuid, progress=80, status="Second Stage TIS Refinement", result="...", state_key="TIS_Refinement", state_value=100)
                
                # 6. Post processing: Max likelihood
                self._update_progress(tasks, task_uuid, progress=90, status="Almost done: Postprocessing", result="...", state_key="Postprocessing", state_value=1)
                df_combined["prediction_max_likelihood"] = 0
                df_pred_1 = df_combined[df_combined["pred_classic"] == 1]
                df_combined.loc[df_pred_1.groupby("orf_group")["prob_cls1"].idxmax(), "prediction_max_likelihood"] = 1
                df_combined["seq_id"] = bacteria
                self._update_progress(tasks, task_uuid, progress=90, status="Almost done: Postprocessing", result="...", state_key="Postprocessing", state_value=100)
                
                # 7. Output: Collect results
                results.append(df_combined)
                all_bacteria += bacteria if all_bacteria == "" else ("-" + bacteria)
                
            # 7. Output: format output file and return
            final_df = pd.concat([df for df in results if not df.empty], ignore_index=True)
            self._update_progress(tasks, task_uuid, progress=100, status="Generating output files", result="...", state_key="Output", state_value=50)
            result_path = self._save_output(final_df, output_format, file_path, task_uuid)
            self._update_progress(tasks, task_uuid, progress=100, status="Completed", result=str(result_path), state_key="Output", state_value=100)
            tasks[task_uuid]["exec_state"]["seq_id"] = all_bacteria.replace(' ', '_')
            return result_path
        
        except Exception as e:
            logging.error(f"Unexpected error while reading file: {file_path} - {str(e)}")
            self._update_progress(
                tasks, 
                task_uuid, 
                progress=100, 
                status="Canceled", 
                result=f"Error reading input file: {str(e)}", 
                state_key=None, 
                state_value=None
            )
            return None
        # except Exception as e:
        #     error_details = traceback.format_exc() 
        #     logging.error(f"Unexpected error while reading file: {file_path}\n{error_details}")
        #     self._update_progress(
        #         tasks, 
        #         task_uuid, 
        #         progress=100, 
        #         status="Canceled", 
        #         result=f"Error: {str(e)}", 
        #         state_key=None, 
        #         state_value=None
        #     )
        #     return None