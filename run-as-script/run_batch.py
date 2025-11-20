"""
High-level runner:
1) split multi-FASTA into per-record FASTAs
2) run each via run_single.py (subprocess)
3) merge outputs into a single CSV/GFF
"""

import argparse
import subprocess
import tempfile
from pathlib import Path
from Bio import SeqIO
import shutil
import os, uuid
# from concurrent.futures import ThreadPoolExecutor, as_completed
from concurrent.futures import ProcessPoolExecutor, as_completed

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
        "--task_uuid", str(task_uuid),
        "--job_name", str(job_name),
        "--verbose"
    ]
    if device:
        cmd += ["--device", device]
    if verbose:
        cmd += ["--verbose"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"run_single failed for {in_fa.name}:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}")
    # run_single prints the output path
    return Path(res.stdout.strip())

def merge_all(paths, fmt: str, merged_out: Path, project_name: str):
    cmd = ["python", str(MERGER), "--inputs", *[str(p) for p in paths], "--output", str(merged_out)]
    if fmt.upper() == "GFF":
        cmd += ["--project", project_name]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"merge failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}")
    return Path(res.stdout.strip())

def main():
    ap = argparse.ArgumentParser(description="Split multi-FASTA and run GeneLM per record in parallel, then merge.")
    ap.add_argument("--input_fasta", required=True, help="Multi-FASTA input")
    ap.add_argument("--format", default="GFF", choices=["GFF", "CSV"], help="Output format")
    ap.add_argument("--device", default=None, help="cpu | cuda | cuda:0 | cuda:1 | (auto if unset)")
    ap.add_argument("--workers", type=int, default=1, help="Number of parallel workers (recommend 1 for GPU, >1 for CPU)")
    ap.add_argument("--job_name", default="batch_job", help="Name stamped into merged GFF header")
    ap.add_argument("--output", required=True, help="Final merged output file (.gff or .csv)")
    ap.add_argument("--keep_temp", action="store_true", help="Keep split FASTAs and per-chunk outputs")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    
    task_uuid = str(uuid.uuid4())

    inp = Path(args.input_fasta).resolve()
    if not inp.exists():
        raise FileNotFoundError(f"Input FASTA not found: {inp}")

    out_path = Path(args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # temp working area
    workdir = Path(tempfile.mkdtemp(prefix="genelm_batch_"))
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

    # split FASTA
    records = list(SeqIO.parse(str(inp), "fasta"))
    if not records:
        raise SystemExit("No records found in FASTA.")
    split_files = [write_single_fasta(rec, split_dir, i) for i, rec in enumerate(records, start=1)]

    # parallel runs
    # For GPU: workers=1 is sane. For CPU: increase workers.
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as ex:  #TIME-05:03 # but when we force kill it kill everything
    # with ThreadPoolExecutor(max_workers=args.workers) as ex: #TIME-04:48 # not the case here
        fut2file = {
            ex.submit(run_one, fa, args.format, per_out_dir, args.device, args.verbose, task_uuid, "job"+str(i)): fa
            for i,fa in enumerate(split_files)
        }
        for fut in as_completed(fut2file):
            fa = fut2file[fut]
            try:
                out_file = fut.result()
                results.append(out_file)
            except Exception as e:
                # Stop early and surface error (you may prefer to continue-on-error)
                raise RuntimeError(f"Failed processing {fa.name}: {e}")

    # merge
    merged = merge_all(results, args.format, out_path, args.job_name)

    if not args.keep_temp:
        shutil.rmtree(workdir, ignore_errors=True)
    
    print(str(merged))

if __name__ == "__main__":
    main()
