#!/usr/bin/env bash

# -----------------------------------------
# SLURM Job Options 
# -----------------------------------------
#SBATCH --job-name=genelm_batch
#SBATCH --output=logs/genelm_batch_%j.out
#SBATCH --error=logs/genelm_batch_%j.err
#SBATCH --time=36:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
# For GPU nodes (uncomment if needed):
##SBATCH --gres=gpu:1

# -----------------------------------------
# Activate env
# -----------------------------------------
# module load anaconda
source activate genelm_env

# -----------------------------------------
# Run
# -----------------------------------------
set -euo pipefail
INPUT_FASTA="$1"            # e.g., data/bacteria.fna
FORMAT="${2:-GFF}"          # GFF or CSV
DEVICE="${3:-cpu}"          # cpu | cuda | cuda:0
WORKERS="${4:-8}"           # recommend 1 for GPU, >=CPU cores for CPU
OUT="${5:-__files__/results/merged.gff}"  # final merged path
JOB_NAME="${6:-slurm_batch}"
mkdir -p logs

python run_batch.py \
  --input_fasta "$INPUT_FASTA" \
  --format "$FORMAT" \
  --device "$DEVICE" \
  --workers "$WORKERS" \
  --job_name "$JOB_NAME" \
  --output "$OUT" \
  --verbose
