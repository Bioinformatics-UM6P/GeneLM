"""
Merge multiple CSV or GFF files into one.
- CSV: assumes identical columns; keeps header from first, appends rows from others.
- GFF: writes a single header block, then concatenates all feature lines
       (skipping '##' meta lines in per-chunk files).
"""

import datetime
import argparse
from pathlib import Path

def merge_csv(files, out_file):
    first = True
    with open(out_file, "w") as w:
        for f in files:
            with open(f, "r") as r:
                for i, line in enumerate(r):
                    if first:
                        w.write(line)
                    else:
                        if i == 0:
                            continue  # skip header
                        w.write(line)
            first = False

def merge_gff(files, out_file, project_name="merged_job"):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(out_file, "w") as w:
        # Single merged header
        w.write("##gff-version 3\n")
        w.write(f"##Generated using GeneLM (merged), {current_time}\n")
        w.write(f"##Project Name: {project_name}\n")
        w.write(f"##Tool: GeneLM\n")
        w.write(f"##DOI: https://doi.org/10.1093/bib/bbaf311\n")
        w.write(f"##Web: https://bioinformatics.um6p.ma/platform\n")
        w.write("\n")
        for f in files:
            with open(f, "r") as r:
                for line in r:
                    if line.startswith("##"):
                        continue
                    w.write(line)

def main():
    ap = argparse.ArgumentParser(description="Merge multiple CSV/GFF into one.")
    ap.add_argument("--inputs", nargs="+", required=True, help="List of CSV or GFF files")
    ap.add_argument("--output", required=True, help="Path to merged file")
    ap.add_argument("--project", default="merged_job", help="Project name to stamp in GFF header")
    args = ap.parse_args()

    in_paths = [Path(p) for p in args.inputs]
    if not in_paths:
        raise SystemExit("No input files.")

    exts = {p.suffix.lower() for p in in_paths}
    if len(exts) != 1 or exts.pop() not in {".csv", ".gff"}:
        raise SystemExit("All inputs must share the same extension: .csv or .gff")

    ext = in_paths[0].suffix.lower()
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if ext == ".csv":
        merge_csv(in_paths, out_path)
    else:
        merge_gff(in_paths, out_path, args.project)

    print(str(out_path.resolve()))

if __name__ == "__main__":
    main()
