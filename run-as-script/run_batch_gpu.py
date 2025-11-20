"""
GPU-aware runner:
1) split multi-FASTA into per-record FASTAs
2) run each via run_single.py (subprocess)
3) assigns each job to an available GPU (0..N)
4) waits if all GPUs are busy
5) merges outputs
"""

import argparse
import subprocess
import tempfile
from pathlib import Path
from Bio import SeqIO
import shutil
import os, uuid
import time

ROOT = Path(__file__).resolve().parents[1]
RUN_SINGLE = ROOT / "run-as-script" / "run_single.py"
MERGER = ROOT / "run-as-script" / "merge_outputs.py"


def write_single_fasta(record, out_dir: Path, index: int):
    rid = record.id.replace(" ", "_")
    fp = out_dir / f"{index:05d}_{rid}.fasta"
    with open(fp, "w") as w:
        SeqIO.write(record, w, "fasta")
    return fp


def run_one(in_fa: Path, fmt: str, out_dir: Path, device: str, verbose: bool, task_uuid: str, job_name: str = "mainjob"):
    cmd = [
        "python", str(RUN_SINGLE),
        "--in_fasta", str(in_fa),
        "--format", fmt,
        "--out_dir", str(out_dir),
        "--device", device,
        "--task_uuid", str(task_uuid),
        "--job_name", str(job_name),
        "--verbose"
    ]
    if verbose:
        cmd += ["--verbose"]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(
            f"run_single failed for {in_fa.name}:\n"
            f"STDOUT:\n{res.stdout}\n"
            f"STDERR:\n{res.stderr}"
        )
    return Path(res.stdout.strip())


def merge_all(paths, fmt: str, merged_out: Path, project_name: str):
    cmd = ["python", str(MERGER), "--inputs", *[str(p) for p in paths], "--output", str(merged_out)]
    if fmt.upper() == "GFF":
        cmd += ["--project", project_name]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(
            f"merge failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
        )
    return Path(res.stdout.strip())


# ---------------------------------------------------------------------------
# NEW: GPU JOB MANAGER
# ---------------------------------------------------------------------------

def detect_gpus():
    try:
        out = subprocess.check_output(["nvidia-smi", "--query-gpu=index", "--format=csv,noheader"])
        gpus = [int(x) for x in out.decode().strip().split("\n")]
        return gpus
    except Exception:
        return []


def wait_for_free_job(jobs):
    """Wait until at least one GPU job finishes."""
    while True:
        alive = [p for p in jobs if p.poll() is None]
        if len(alive) < len(jobs):
            return
        time.sleep(1)


def main():
    ap = argparse.ArgumentParser(description="GPU-based FASTA runner")
    ap.add_argument("--input_fasta", required=True)
    ap.add_argument("--format", default="GFF", choices=["GFF", "CSV"])
    ap.add_argument("--device", default=None, help="cpu | cuda | auto | cuda:0 ...")
    ap.add_argument("--job_name", default="batch_job")
    ap.add_argument("--output", required=True)
    ap.add_argument("--keep_temp", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    
    task_uuid = str(uuid.uuid4())
    

    inp = Path(args.input_fasta).resolve()
    if not inp.exists():
        raise FileNotFoundError(f"Input FASTA not found: {inp}")

    out_path = Path(args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # temp dirs
    workdir = Path(tempfile.mkdtemp(prefix="genelm_gpu_batch_"))
    split_dir = workdir / "split"
    per_out_dir = workdir / "chunk_results"
    split_dir.mkdir(parents=True, exist_ok=True)
    per_out_dir.mkdir(parents=True, exist_ok=True)
    
    if args.keep_temp:
        print("\n" + "="*80)
        print("⚠️  DEBUG MODE ENABLED (--keep_temp)")
        print("Temporary folder was NOT deleted.")
        print(f"Debug folder: {workdir}")
        print("\nInside this folder you will find:")
        print(f"  • split/          — one FASTA file per sequence")
        print(f"  • chunk_results/  — per-sequence GFF/CSV results (from run_single)")
        print(f"  • {workdir}/**/*  — additional GeneLM-related temporary files")
        print("="*80 + "\n")

    # split
    records = list(SeqIO.parse(str(inp), "fasta"))
    split_files = [write_single_fasta(rec, split_dir, i) for i, rec in enumerate(records, start=1)]

    # GPU list
    if args.device and args.device.startswith("cuda"):
        # user forced single device
        gpu_list = [args.device]
    else:
        gpu_ids = detect_gpus()
        gpu_list = [f"cuda:{i}" for i in gpu_ids] if gpu_ids else ["cpu"]

    print(f"Using devices: {gpu_list}")

    # Running jobs with GPU queue
    running_jobs = []    # list of (Popen, fasta_path, device)
    all_jobs = []
    results = []

    for i,fa in enumerate(split_files):
        # Wait until a GPU slot is free
        while len(running_jobs) >= len(gpu_list):
            wait_for_free_job([p for p, _, _ in running_jobs])
            finished_jobs = [(p, f, d) for (p, f, d) in running_jobs if p.poll() is not None]
            running_jobs = [(p, f, d) for (p, f, d) in running_jobs if p.poll() is None]

        # Assign next GPU
        device = gpu_list[len(running_jobs) % len(gpu_list)]

        # Launch job
        cmd = [
            "python", str(RUN_SINGLE),
            "--in_fasta", str(fa),
            "--format", args.format,
            "--out_dir", str(per_out_dir),
            "--device", device,
            "--task_uuid", str(task_uuid),
            "--job_name", "job"+str(i),
            "--verbose"
        ]
        # if args.verbose:
        #     cmd.append("--verbose")

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        all_jobs.append((p, fa, device))
        running_jobs.append((p, fa, device))

    # Collect all results
    for p, fa, device in all_jobs:
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            raise RuntimeError(
                f"Failed on {fa.name} (device {device}):\n"
                f"STDOUT:\n{stdout}\nSTDERR:\n{stderr}"
            )
        results.append(Path(stdout.strip()))

    # Merge
    print(results)
    merged = merge_all(results, args.format, out_path, args.job_name)

    if not args.keep_temp:
        shutil.rmtree(workdir, ignore_errors=True)

    print(str(merged))

if __name__ == "__main__":
    main()
