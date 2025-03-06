# Finetune Directory Structure

This directory contains the files and folders related to model finetuning operations.

## Directory Structure

GeneLM/
├── webtool/
├── ├── start.py
├── ├── input/
├── ├── ├── verified_sequence/
├── ├── ├── ├── Escherichia_coli_K_12_substr__MG1655_uid57779/
├── ├── ├── ├── ├── sequence.fasta
├── ├── ├── ├── ├── ncbi.gff
├── ├── ├── ├── ├── verified.gff
├── ├── ├── ├── Halobacterium_salinarum_R1_uid61571/
├── ├── ├── ├── ├── sequence.fasta
├── ├── ├── ├── ├── ncbi.gff
├── ├── ├── ├── ├── verified.gff
├── ├── ├── ├── Natronomonas_pharaonis_DSM_2160_uid58435/
├── ├── ├── ├── ├── sequence.fasta
├── ├── ├── ├── ├── ncbi.gff
├── ├── ├── ├── ├── verified.gff
├── ├── ├── ├── Roseobacter_denitrificans_Och114/
├── ├── ├── ├── ├── sequence.fasta
├── ├── ├── ├── ├── ncbi.gff
├── ├── ├── ├── ├── verified.gff
├── ├── ├── ├── Mycobacterium_tuberculosis_H37Rv_uid57777/
├── ├── ├── ├── ├── sequence.fasta
├── ├── ├── ├── ├── ncbi.gff
├── ├── ├── ├── ├── verified.gff
├── ├── ├── short_sequence/
├── ├── ├── ├── sequence_tiny.fasta
├── ├── ├── ├── sequence.fasta
├── ├── ├── ├── sequence_small.fasta
├── ├── ├── ├── sequence_tiny_mixt.fasta
├── ├── requirements.txt
├── ├── api/
├── ├── ├── api.py
├── ├── ├── core.py
├── ├── ├── .DS_Store
├── ├── ├── __files__/
├── ├── ├── ├── tasks/
├── ├── ├── ├── ├── tasks_checkpoint.json
├── ├── ├── ├── results/
├── ├── ├── ├── ├── 52c41020-1b1a-4d6e-91f1-1212280aba34_sequence_tiny.gff
├── ├── ├── ├── ├── da1ed61b-5472-45ef-9f95-80e734f0dc48_sequence_tiny.gff
├── ├── ├── ├── ├── e50ba69d-06e9-408e-8276-cb41dbd7eee3_sequence_tiny.gff
├── ├── ├── ├── ├── 658686f8-ead0-447b-a744-599aba2009e2_sequence_tiny.gff
├── ├── ├── ├── ├── 368e770f-22b7-4d30-bf92-7c04f31117fa_sequence_tiny.gff
├── ├── ├── ├── ├── 311bbd07-8c74-4dc4-b466-526e073e3c42_tmp93lr7eu1.gff
├── ├── ├── ├── ├── b123b99d-8d15-4525-8629-b59e12d5ab81_sequence_tiny.gff
├── ├── ├── ├── ├── aeb65387-a132-499a-8b87-02154dc01f4f_sequence_tiny.gff
├── ├── ├── ├── ├── 7eae971f-48d1-41a7-a09e-8f24070f1026_sequence_tiny.gff
├── ├── ├── ├── ├── ecc41774-f945-44e0-848a-d6c56b5ae932_tmp6w5alf0q.gff
├── ├── ├── ├── ├── a44ccadf-e2dd-49ce-a63c-5ffccfb965b2_sequence_tiny.gff
├── ├── ├── ├── ├── 113bbbe3-81fd-4991-a9a7-2d7384a7edcb_tmp7xli8w61.gff
├── ├── ├── ├── ├── 772dd4ba-4d2f-40ad-9fa4-c14b222f30b8_sequence_tiny.gff
├── ├── ├── ├── ├── 6ff65de7-3e3c-4e49-9def-68cef8a3bd4c_tmpag3sqtpw.gff
├── ├── ├── ├── ├── 7016557f-7b19-4dab-a3df-34792640eddc_sequence_tiny.gff
├── ├── ├── ├── ├── f0e37d8e-1ad6-4942-a22c-4b1d31cbde48_sequence_tiny.gff
├── ├── ├── ├── ├── 3c9d00f4-3593-4ab2-8a69-3787879fed86_sequence_tiny.gff
├── ├── ├── ├── ├── a1222fdc-e500-465b-8c8d-69319f655666_tmpiv8z0k9l.gff
├── ├── ├── ├── ├── 82f4a1a7-8f0c-467d-b3f8-0eeef9f2201e_tmpp110029f.gff
├── ├── ├── ├── ├── d6224a71-5696-41cb-a748-853993963e2b_sequence_tiny.gff
├── ├── ├── ├── ├── 8dd7111d-6077-4796-98b3-e7178296ca2d_sequence_tiny.gff
├── ├── ├── ├── uploads/
├── ├── ├── ├── ├── a1222fdc-e500-465b-8c8d-69319f655666_tmpiv8z0k9l.fasta
├── ├── ├── ├── ├── d6224a71-5696-41cb-a748-853993963e2b_sequence_tiny.fasta
├── ├── ├── ├── ├── 6e76a805-0beb-429c-a46f-fce6df065a4a_sequence_tiny.fasta
├── ├── ├── ├── ├── aeb65387-a132-499a-8b87-02154dc01f4f_sequence_tiny.fasta
├── ├── ├── ├── ├── 7016557f-7b19-4dab-a3df-34792640eddc_sequence_tiny.fasta
├── ├── ├── ├── ├── a44ccadf-e2dd-49ce-a63c-5ffccfb965b2_sequence_tiny.fasta
├── ├── ├── ├── ├── 8dd7111d-6077-4796-98b3-e7178296ca2d_sequence_tiny.fasta
├── ├── ├── ├── ├── 368e770f-22b7-4d30-bf92-7c04f31117fa_sequence_tiny.fasta
├── ├── ├── ├── ├── e9889d11-61fd-44fb-9cc8-bfbae2d3ffc8_sequence_tiny.fasta
├── ├── ├── ├── ├── 2d416b22-7c10-4d78-a3df-edc5ddb60a5e_sequence_tiny.fasta
├── ├── ├── ├── ├── b123b99d-8d15-4525-8629-b59e12d5ab81_sequence_tiny.fasta
├── ├── ├── ├── ├── 82f4a1a7-8f0c-467d-b3f8-0eeef9f2201e_tmpp110029f.fasta
├── ├── ├── ├── ├── 52c41020-1b1a-4d6e-91f1-1212280aba34_sequence_tiny.fasta
├── ├── ├── ├── ├── f28bec1c-9348-43a5-a04f-73ca6ee42c68_sequence_tiny.fasta
├── ├── ├── ├── ├── 658686f8-ead0-447b-a744-599aba2009e2_sequence_tiny.fasta
├── ├── ├── ├── ├── 7eae971f-48d1-41a7-a09e-8f24070f1026_sequence_tiny.fasta
├── ├── ├── ├── ├── da1ed61b-5472-45ef-9f95-80e734f0dc48_sequence_tiny.fasta
├── ├── ├── ├── ├── c00b4828-7844-4550-9f9d-1aa4013e5a69_sequence_tiny.fasta
├── ├── ├── ├── ├── 3c9d00f4-3593-4ab2-8a69-3787879fed86_sequence_tiny.fasta
├── ├── ├── ├── ├── f887cca8-66b7-4892-8a1b-799281408781_sequence_tiny.fasta
├── ├── ├── ├── ├── b3263022-0c4e-4407-b029-1db84b3b42ca_sequence_tiny.fasta
├── ├── ├── ├── ├── 772dd4ba-4d2f-40ad-9fa4-c14b222f30b8_sequence_tiny.fasta
├── ├── ├── ├── ├── ecc41774-f945-44e0-848a-d6c56b5ae932_tmp6w5alf0q.fasta
├── ├── ├── ├── ├── f0e37d8e-1ad6-4942-a22c-4b1d31cbde48_sequence_tiny.fasta
├── ├── ├── ├── ├── 113bbbe3-81fd-4991-a9a7-2d7384a7edcb_tmp7xli8w61.fasta
├── ├── ├── ├── ├── 311bbd07-8c74-4dc4-b466-526e073e3c42_tmp93lr7eu1.fasta
├── ├── ├── ├── ├── e50ba69d-06e9-408e-8276-cb41dbd7eee3_sequence_tiny.fasta
├── ├── ├── ├── ├── 18ea8761-5242-4960-8a80-91e5a09e4fd7_tmp2c5pz62y.fasta
├── ├── ├── ├── ├── 6ff65de7-3e3c-4e49-9def-68cef8a3bd4c_tmpag3sqtpw.fasta
├── ├── ├── ├── api.log
├── ├── setup.sh
├── ├── ui/
├── ├── ├── app.py
├── ├── ├── static/
├── ├── ├── ├── rolling.gif
├── ├── ├── ├── results.png
├── ├── ├── ├── demo-gene-prediction-prokaryotes.mp4
├── ├── ├── ├── sequence_tiny.fasta
├── ├── ├── ├── hero.png
├── ├── ├── ├── web_tool_2b.png
├── ├── ├── ├── web_tool_merged.png
├── ├── ├── ├── benchmark_table.png
├── ├── ├── ├── dna.jpg
├── ├── ├── ├── app.png
├── ├── ├── ├── TIS_vs_Prodigal-old.png
├── ├── ├── ├── TIS_vs_Prodigal.png
├── ├── ├── ├── cta.png
├── ├── ├── ├── web_tool_1b.png
├── ├── ├── ├── task.png
├── ├── ├── ├── .DS_Store
├── ├── ├── .DS_Store
├── ├── README.md
├── ├── evaluation/
├── ├── ├── Escherichia_coli_K_12_substr__MG1655_uid57779/
├── ├── ├── ├── prodigal.genes
├── ├── ├── ├── ncbi.gff
├── ├── ├── ├── prodigal.gff
├── ├── ├── ├── verified.gff
├── ├── ├── ├── our_tool.gff
├── ├── ├── prodigal_parser.py
├── ├── ├── Halobacterium_salinarum_R1_uid61571/
├── ├── ├── ├── prodigal.genes
├── ├── ├── ├── ncbi.gff
├── ├── ├── ├── prodigal.gff
├── ├── ├── ├── verified.gff
├── ├── ├── ├── our_tool.gff
├── ├── ├── Natronomonas_pharaonis_DSM_2160_uid58435/
├── ├── ├── ├── prodigal.genes
├── ├── ├── ├── ncbi.gff
├── ├── ├── ├── prodigal.gff
├── ├── ├── ├── verified.gff
├── ├── ├── ├── our_tool.gff
├── ├── ├── Roseobacter_denitrificans_Och114/
├── ├── ├── ├── prodigal.genes
├── ├── ├── ├── ncbi.gff
├── ├── ├── ├── prodigal.gff
├── ├── ├── ├── verified.gff
├── ├── ├── ├── our_tool.gff
├── ├── ├── Mycobacterium_tuberculosis_H37Rv_uid57777/
├── ├── ├── ├── prodigal.genes
├── ├── ├── ├── ncbi.gff
├── ├── ├── ├── prodigal.gff
├── ├── ├── ├── verified.gff
├── ├── ├── ├── our_tool.gff
├── ├── ├── benchmarck.ipynb
├── finetune/
├── ├── train-pipeline/
├── ├── ├── data/
├── ├── ├── ├── verified-genome2/
├── ├── ├── ├── ├── tis/
├── ├── ├── ├── ├── ├── data_summary.json
├── ├── ├── ├── ├── ├── database/
├── ├── ├── ├── ├── ├── ├── bacteria_4.csv
├── ├── ├── ├── ├── ├── ├── bacteria_5.csv
├── ├── ├── ├── ├── ├── ├── bacteria_3.csv
├── ├── ├── ├── ├── ├── ├── bacteria_1.csv
├── ├── ├── ├── ├── ├── ├── bacteria_2.csv
├── ├── ├── ├── ├── ├── data_index.json
├── ├── ├── ├── ├── ├── balanced/
├── ├── ├── ├── ├── ├── ├── bacteria_4.csv
├── ├── ├── ├── ├── ├── ├── bacteria_5.csv
├── ├── ├── ├── ├── ├── ├── bacteria_3.csv
├── ├── ├── ├── ├── ├── ├── bacteria_1.csv
├── ├── ├── ├── ├── ├── ├── bacteria_2.csv
├── ├── ├── ├── ├── ├── data_summary.json.lock
├── ├── ├── ├── ├── cds/
├── ├── ├── ├── ├── ├── data_summary.json
├── ├── ├── ├── ├── ├── database/
├── ├── ├── ├── ├── ├── ├── bacteria_4.csv
├── ├── ├── ├── ├── ├── ├── bacteria_5.csv
├── ├── ├── ├── ├── ├── ├── bacteria_3.csv
├── ├── ├── ├── ├── ├── ├── bacteria_1.csv
├── ├── ├── ├── ├── ├── ├── bacteria_2.csv
├── ├── ├── ├── ├── ├── balanced/
├── ├── ├── ├── ├── ├── ├── bacteria_4.csv
├── ├── ├── ├── ├── ├── ├── bacteria_5.csv
├── ├── ├── ├── ├── ├── ├── bacteria_3.csv
├── ├── ├── ├── ├── ├── ├── bacteria_1.csv
├── ├── ├── ├── ├── ├── ├── bacteria_2.csv
├── ├── ├── ├── ├── ├── data_summary.json.lock
├── ├── ├── ├── tis/
├── ├── ├── ├── ├── BacteriaTIS-ORFSeq2Class-v4/
├── ├── ├── ├── ├── ├── data_summary.json
├── ├── ├── ├── ├── ├── data_index.json
├── ├── ├── ├── ├── ├── data_summary.json.lock
├── ├── ├── ├── ref/
├── ├── ├── ├── ├── assembly_summary.note
├── ├── ├── ├── cds/
├── ├── ├── ├── ├── BacteriaCDS-ORFSeq2Class-v2/
├── ├── ├── ├── ├── ├── data_summary.json
├── ├── ├── ├── ├── ├── data_index.json
├── ├── ├── ├── ├── ├── data_summary.json.lock
├── ├── ├── requirements.txt
├── ├── ├── finetune/
├── ├── ├── ├── train_tis_annotator.py
├── ├── ├── ├── sbatchlogs/
├── ├── ├── ├── ├── toubkallogs/
├── ├── ├── ├── ├── ├── 3298108.out
├── ├── ├── ├── ├── ├── 3295763.out
├── ├── ├── ├── ├── ├── 3295762.out
├── ├── ├── ├── ├── ├── 3315205.out
├── ├── ├── ├── ├── ├── 3305713.out
├── ├── ├── ├── ├── ├── 3305244.out
├── ├── ├── ├── ├── ├── 3309554.out
├── ├── ├── ├── ├── ├── 3293384.out
├── ├── ├── ├── ├── ├── 3305717.out
├── ├── ├── ├── ├── ├── 3305047.out
├── ├── ├── ├── ├── ├── 3295761.out
├── ├── ├── ├── ├── ├── 3305702.out
├── ├── ├── ├── ├── ├── 3305418.out
├── ├── ├── ├── ├── ├── 3305843.out
├── ├── ├── ├── ├── ├── 3305055.out
├── ├── ├── ├── ├── ├── 3305417.out
├── ├── ├── ├── ├── ├── 3298195.out
├── ├── ├── ├── ├── ├── 3295502.out
├── ├── ├── ├── ├── ├── 3289123.out
├── ├── ├── ├── ├── ├── 3305705.out
├── ├── ├── ├── ├── ├── 3291336.out
├── ├── ├── ├── ├── ├── 3295114.out
├── ├── ├── ├── ├── ├── 3305419.out
├── ├── ├── ├── ├── ├── 3293389.out
├── ├── ├── ├── ├── ├── 3305243.out
├── ├── ├── ├── ├── ├── 3305242.out
├── ├── ├── ├── ├── ├── 3305416.out
├── ├── ├── ├── ├── ├── 3293209.out
├── ├── ├── ├── ├── ├── 3309470.out
├── ├── ├── ├── ├── ├── 3305709.out
├── ├── ├── ├── ├── ├── 3302129.out
├── ├── ├── ├── ├── ├── 3295500.out
├── ├── ├── ├── ├── ├── 3305706.out
├── ├── ├── ├── ├── checkpoint/
├── ├── ├── ├── ├── ├── tis_iter-PseudoLabel/
├── ├── ├── ├── ├── ├── ├── unlabeled_checkpoint.json
├── ├── ├── ├── ├── ├── ├── operations.log
├── ├── ├── ├── ├── ├── ├── train_count.json
├── ├── ├── ├── ├── ├── ├── train_state.log
├── ├── ├── ├── ├── ├── ├── test_count.json
├── ├── ├── ├── ├── ├── ├── eval_count.json
├── ├── ├── ├── ├── ├── tis_exp3b-b/
├── ├── ├── ├── ├── ├── ├── operations.log
├── ├── ├── ├── ├── ├── ├── train_count.json
├── ├── ├── ├── ├── ├── ├── train_state.log
├── ├── ├── ├── ├── ├── ├── test_count.json
├── ├── ├── ├── ├── ├── ├── eval_count.json
├── ├── ├── ├── ├── ├── cds_exp1/
├── ├── ├── ├── ├── ├── ├── operations.log
├── ├── ├── ├── ├── ├── ├── train_count.json
├── ├── ├── ├── ├── ├── ├── train_state.log
├── ├── ├── ├── ├── ├── ├── test_count.json
├── ├── ├── ├── ├── ├── ├── train_idx_checkpoint.json
├── ├── ├── ├── ├── ├── ├── eval_count.json
├── ├── ├── ├── ├── ├── tis_exp3/
├── ├── ├── ├── ├── ├── ├── operations.log
├── ├── ├── ├── ├── ├── ├── train_count.json
├── ├── ├── ├── ├── ├── ├── train_state.log
├── ├── ├── ├── ├── ├── ├── test_count.json
├── ├── ├── ├── ├── ├── ├── eval_count.json
├── ├── ├── ├── ├── ├── tis_full-full-verified/
├── ├── ├── ├── ├── ├── ├── operations.log
├── ├── ├── ├── ├── ├── ├── train_count.json
├── ├── ├── ├── ├── ├── ├── train_state.log
├── ├── ├── ├── ├── ├── ├── test_count.json
├── ├── ├── ├── ├── ├── ├── eval_count.json
├── ├── ├── ├── ├── ├── cds_exp2-b/
├── ├── ├── ├── ├── ├── ├── operations.log
├── ├── ├── ├── ├── ├── ├── train_count.json
├── ├── ├── ├── ├── ├── ├── train_state.log
├── ├── ├── ├── ├── ├── ├── test_count.json
├── ├── ├── ├── ├── ├── ├── train_idx_checkpoint.json
├── ├── ├── ├── ├── ├── ├── eval_count.json
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
├── ├── generate_structure.py
├── ├── README.md
├── ├── data-pipeline/
├── ├── ├── DataStats_CompleteGenome.ipynb
├── ├── ├── Data_Extraction.ipynb
├── .gitignore
├── README.md




1. Place your raw training data in the `data/raw` directory
2. Use scripts in `scripts/preprocess` to prepare your data
3. Configure your training parameters in `scripts/train`
4. Run training scripts to finetune models
5. Find your trained models in the `models/final` directory
6. Monitor progress through logs in the `logs` directory

## Notes

- Keep large data files and model checkpoints out of version control
- Use `.gitignore` to exclude large binary files
- Consider using data version control (DVC) for managing large files