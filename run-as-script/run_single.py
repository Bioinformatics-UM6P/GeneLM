"""
Run AnnotatorPipeline on a single-FASTA file.
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
import subprocess

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
    p.add_argument("--task_uuid", default=None, help="Task unique uuid (optional/auto-generated)")
    p.add_argument("--job_name", default="[single_job]", help="Job unique name (optional)")
    p.add_argument("--keep_temp", action="store_true")
    # new feature
    p.add_argument(
        "--extract_orf_protein",
        action="store_true",
        help="After annotation finishes, extract ORF & protein FASTA files."
    )
    p.add_argument(
        "--codon_table",
        type=int,
        default=11,
        help="NCBI codon table ID (default: 11 — Bacterial/Archaeal)"
    )
    
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

    tasks = {}
    task_uuid = str(uuid.uuid4()) if not args.task_uuid else str(args.task_uuid)
    tasks[task_uuid] = {"status": "Queued", "progress": 0, "result": None, "exec_state": {}}
    
    logging.basicConfig(
        filename=f"./__files__/results/exec_{'-'.join(task_uuid.split("-")[:2])}_{args.job_name}.log",
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    annot = AnnotatorPipeline()
    
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
            gff_final = final_path
            
            shutil.copy2(out_path, final_path)
            print(str(final_path))
        else:
            gff_final = out_path
            print(str(out_path.resolve()))
            
        # cleanup temp folder
        if not args.keep_temp:
            annot.cleanup(task_uuid)
        else:
            print('TEMP FOLDER FOR DEBUG: ')
            print(f'-  /__files__/results/{task_uuid}]')
            print(f'-  /__files__/results/exec_{'-'.join(task_uuid.split("-")[:2])}_{args.job_name}.log]')
            
        # --------------------------------------------------------------
        # OPTIONAL: Extract ORFs + Proteins by calling external script
        # --------------------------------------------------------------
        if args.extract_orf_protein and args.format.upper() == "GFF":
            print("[ORF-PROTEIN] Running extract_orf_protein.py ...")

            script_path = Path(__file__).parent / "extract_orf_protein.py"
            output_dir = args.out_dir if args.out_dir else "."

            cmd = [
                sys.executable,
                str(script_path),
                str(in_fasta),
                str(gff_final),
                str(output_dir),
                "--codon_table", str(args.codon_table)
            ]

            try:
                subprocess.run(cmd, check=True)
                print(f"[ORF-PROTEIN] Extraction completed → {output_dir}")
            except subprocess.CalledProcessError:
                print("[ORF-PROTEIN] Extraction failed! Check extract_orf_protein.py")

            
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        

if __name__ == "__main__":
    main()
