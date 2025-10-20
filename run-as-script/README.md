<div align="center" style="">
  <br>
  <img src="../webtool/ui/static/banner/banner-6.png"/ style="height: 6em; width: 12em">
  <br>
  <!-- <h1>GeneLM</h1> -->
  GeneLM: Gene Language Model for Translation Initiation Site Prediction in Bacteria
  <br>
  <br>
  <p>****</p>
  <p>GeneLM-Script Runner (split - parallel - merge)</p>
</div>

---

#### Quick start

First of all you need to setup genelm environment tobe able to annotate gene using our model.
```bash
python -m venv .genelm_env
source .genelm_env/bin/activate
pip install -r genelm/requirements.txt 
```
<br>

#### Usage
**1. Single sequence**

Use this when your FASTA contains one record (or when you want to process a specific record by itself). It runs the full AnnotatorPipeline once and writes a single GFF/CSV result.
`--device` lets you force CPU or select a GPU (e.g., cuda:0).
If you pass `--out_dir`, the produced file is copied there; otherwise it stays in `__files__/results`.
```bash
python run_single.py \
  --in_fasta smoke-test/sequence_tiny.fasta \
  --format GFF \
  --device cpu \
  --out_dir __files__/results
```
<br>

**2. Batch (multi-FASTA)**

Use this for a multi-FASTA: it automatically splits the input into per-record FASTAs, runs each one in parallel (set with `--workers`), and then merges all per-record outputs into a single file.

- For GPU, set `--device cuda:0` (or similar) and keep `--workers 1`.
- For CPU, set `--device cpu` and increase `--workers` to match your core count.
  
```bash
python run_batch.py \
  --input_fasta smoke-test/sequence_tiny_mixt.fasta \
  --format GFF \
  --device cpu \
  --workers 8 \
  --job_name test-smoke \
  --output __files__/results/t-smoke.gff
```

- Device control
  - --device cpu → hides GPUs (CUDA_VISIBLE_DEVICES="")
  - --device cuda → auto GPU (as per core.py)
  - --device cuda:0 → pins to GPU 0 (exposes only index 0)

- Workers
  - GPU: --workers 1
  - CPU: --workers ≈ number of cores

- Output
  - Per-chunk outputs go to a temp dir (deleted unless --keep_temp)
  - Final merged file goes to --output path
<br>

**3. HPC (SLURM)**

Use the provided SLURM helper to run the batch workflow on a cluster.
Arguments: `INPUT_FASTA FORMAT DEVICE WORKERS OUT_FILE JOB_NAME`.
Pick DEVICE=cpu for CPU nodes or cuda:0 on a GPU partition (and set `#SBATCH --gres=gpu:1` inside the script if needed).

```bash
sbatch hpc_slurm_example.sh  data/multi.fna GFF cpu 16 __files__/results/merged.gff my_job
```