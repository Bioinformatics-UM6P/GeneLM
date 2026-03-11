#!/bin/bash
data_path=$1
data_folder=$2
kmer_size=$3
batch_size=$4
num_nodes=$5
exp_id=$6 

# --------------------------------------------------------------------------
mode="-PseudoLabel" # changed this base on production training or test [test or '']
# --------------------------------------------------------------------------

output_dir="output/BaBert_k$kmer_size-TIS$mode"
lr=3e-5 
seed=42
exp_id=$6$mode

echo "The provided kmer is: $kmer_size, data_path is $data_path"

# Set wandb project name for external performance track
export WANDB_PROJECT="TIS_BaBert_k$kmer_size-db_v3$mode"
export WANDB_NAME="dnabert_k$kmer_size"

# Initialize the model path with the base DNABERT model
model_path="zhihan1996/DNA_bert_$kmer_size"
model_path="output/BaBert_k6-TIS-PseudoLabel/checkpoint-186"

# Run training
torchrun --nproc_per_node=$num_nodes --master_port=29503 train_tis_iter.py \
    --model_name_or_path ${model_path} \
    --data_path  $data_path/$data \
    --data_folder $data_folder \
    --kmer ${kmer_size} \
    --run_name DNABERT-kmer${kmer_size} \
    --model_max_length 512 \
    --data_load_batch_size ${batch_size} \
    --gradient_accumulation_steps 1 \
    --learning_rate ${lr} \
    --num_train_epochs 3 \
    --fp16 True \
    --evaluation_strategy epoch \
    --save_strategy epoch \
    --output_dir ${output_dir} \
    --warmup_steps 50 \
    --overwrite_output_dir True \
    --log_level info \
    --find_unused_parameters False \
    --nodes $num_nodes \
    --do_eval True \
    --experimentation_id ${exp_id} \
    --confidence_level 0.6 \
    --unlabeled_data_path ../data/tis/BacteriaTIS-ORFSeq2Class-v3/database \
    --unlabeled_data_file_per_retrieval 10