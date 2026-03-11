#!/bin/bash
##SBATCH --job-name=CDS-BacteriaBERT_dbv2_exp1
#SBATCH --time=24:00:00                
#SBATCH --account=<ID>-<ID>-default-gpu
#SBATCH --partition=gpu                 
#SBATCH --qos=default-gpu
#SBATCH --gres=gpu:1                  
#SBATCH --output=sbatchlogs/toubkallogs/%j.out 
##SBATCH --output=sbatchlogs/toubkalmini/%j.out 

# Virtual environment
source ~/.bashrc
conda activate dnabert

# Run the script
bash train_cds_annotator.sh ../data/cds/BacteriaCDS-ORFSeq2Class-v2/ database 6 512 1 cds_exp1
# experiment
#bash train_cds_annotator.sh ../data/cds/BacteriaCDS-ORFSeq2Class-v2/ balanced_v2 6 512 1 cds_exp2
# experiment
# bash train_tis_annotator.sh ../data/tis/BacteriaTIS-ORFSeq2Class-v3/ balanced 6 512 1 tis_exp3b
# experiment
#bash train_tis_annotator.sh ../data/tis/BacteriaTIS-ORFSeq2Class-v5/ database 6 2048 1 tis_exp5
# experiment
#bash train_tis_iter.sh ../data/verified-genome/tis_iter/ database 6 256 1 tis_iter
# experiment
#papermill train_tis_iter.ipynb train_tis_iter-out.ipynb
#bash train_tis_annotator.sh ../data/verified-genome2/tis/ database 6 512 1 tis_full
