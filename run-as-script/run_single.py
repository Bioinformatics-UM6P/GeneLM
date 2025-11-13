"""
Run AnnotatorPipeline on a single-FASTA file (one record recommended).
Writes output (CSV or GFF) to __files__/results (as defined in core.py),
then copies it to --out_dir if provided.
"""

import argparse
import os
from pathlib import Path
import shutil
import uuid
import logging
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from genelm.core import AnnotatorPipeline, OUTPUT_DIR as CORE_OUTPUT_DIR  # uses ./__files__/results

def main():
    p = argparse.ArgumentParser(description="Run GeneLM AnnotatorPipeline on a single FASTA.")
    p.add_argument("--in_fasta", required=True, help="Path to a (preferably single-record) FASTA")
    p.add_argument("--format", default="GFF", choices=["GFF", "CSV"], help="Output format")
    p.add_argument("--out_dir", default=None, help="Optional final destination dir")
    p.add_argument("--filename", default=None, help="Optional custom output filename (will auto-append .gff if not)")
    p.add_argument("--device", default=None, help="cpu | cuda | cuda:0 | cuda:1 | (leave unset to auto)")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    if args.device is not None:
        if args.device.lower() == "cpu":
            os.environ["CUDA_VISIBLE_DEVICES"] = ""
        elif args.device.lower().startswith("cuda"):
            if ":" in args.device:
                idx = args.device.split(":")[1]
                os.environ["CUDA_VISIBLE_DEVICES"] = idx
            else:
                pass

    logging.basicConfig(
        filename="__files__/run_single.log",
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    annot = AnnotatorPipeline()
    tasks = {}
    task_uuid = str(uuid.uuid4())
    tasks[task_uuid] = {"status": "Queued", "progress": 0, "result": None, "exec_state": {}}

    in_fasta = Path(args.in_fasta).resolve()
    if not in_fasta.exists():
        raise FileNotFoundError(f"Input FASTA not found: {in_fasta}")

    # core.pipeline writes to CORE_OUTPUT_DIR and returns that path
    try:
        out_path = annot.pipeline(in_fasta, args.format, tasks, task_uuid, logging)
        if out_path is None:
            raise RuntimeError("Pipeline failed (see logs).")

        # Optionally copy to user-out_dir
        if args.out_dir:
            out_dir = Path(args.out_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            
            # patch: https://github.com/Bioinformatics-UM6P/GeneLM/issues/3
            if args.filename:
                ext = ".gff" if args.format.upper() == "GFF" else ".csv"
                final_name = args.filename if args.filename.lower().endswith(ext) else args.filename + ext
                final_path = out_dir / final_name
            else:
                final_path = out_dir / out_path.name
                
            shutil.copy2(out_path, final_path)
            print(str(final_path))
        else:
            print(str(out_path.resolve()))
            
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        

if __name__ == "__main__":
    main()
