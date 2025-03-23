## Note

<div style="color: red;">Note: The contents of finetune/data-pipeline/* and finetune/train-pipeline/* have been excluded from this release. We will make the full code pipeline for self-training—including data preprocessing and training scripts—publicly available soon to allow full reproducibility of our work.</div>

## Finetune Directory Structure

This directory contains the files and folders related to model finetuning operations.

### Directory Structure

```log
GeneLM/
├── finetune/
├── ├── train-pipeline/
├── ├── ├── data/
├── ├── ├── ├── verified-genome2/
├── ├── ├── ├── ├── tis/
├── ├── ├── ├── ├── cds/
├── ├── ├── ├── ├── ├── data_summary.json
├── ├── ├── ├── ├── ├── database/
├── ├── ├── ├── ├── ├── balanced/
├── ├── ├── ├── tis/
├── ├── ├── ├── ├── BacteriaTIS-ORFSeq2Class-v4/
├── ├── ├── ├── ├── ├── data_summary.json
├── ├── ├── ├── ├── ├── data_index.json
├── ├── ├── ├── ref/
├── ├── ├── ├── ├── assembly_summary.note
├── ├── ├── ├── cds/
├── ├── ├── ├── ├── BacteriaCDS-ORFSeq2Class-v2/
├── ├── ├── ├── ├── ├── data_summary.json
├── ├── ├── ├── ├── ├── data_index.json
├── ├── ├── requirements.txt
├── ├── ├── finetune/
├── ├── ├── ├── train_tis_annotator.py
├── ├── ├── ├── sbatchlogs/
├── ├── ├── ├── train_cds_annotator.py
├── ├── ├── ├── train_cds_annotator.sh
├── ├── ├── ├── train_tis_iter.py
├── ├── ├── ├── train_tis_iter.sh
├── ├── ├── ├── train_tis_iter.ipynb
├── ├── ├── ├── submit_job.sh
├── ├── ├── ├── train_tis_annotator.sh
├── ├── ├── mount_remote_database.sh
├── ├── ├── dnabert_env.yml
├── ├── ├── utils/
├── ├── ├── ├── logger_tis.log
├── ├── ├── ├── 02-Data_Partitioner-TIS.ipynb
├── ├── ├── ├── 01-Data_Partitioner-CDS.ipynb
├── ├── ├── ├── logger.log
├── ├── ├── ├── 01-Inference-CDS.ipynb
├── ├── ├── ├── 01-Forcasting-CDS.ipynb
├── ├── ├── ├── 01-Analyse-CDS.ipynb
├── ├── ├── ├── 01-Inference-CDS-out.ipynb
├── ├── ├── ├── 03-Analyse-VERIFIED.ipynb
├── ├── ├── ├── 02-Analyse-TIS.ipynb
├── ├── README.md
├── ├── data-pipeline/
├── ├── ├── DataStats_CompleteGenome.ipynb
├── ├── ├── Data_Extraction.ipynb
```