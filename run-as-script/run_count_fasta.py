"""
Count number of FASTA records in a given file.
Usage:
    python run_count_fasta.py --input myfile.fasta
    
Extended(in shell):
    COUNT=$(python run_count_fasta.py -i smoke-test/sequence_tiny_mixt.fasta)
    NUM_WORKERS=$(( COUNT < 100 ? COUNT : 100 ))
    
    Then print doing: `echo $NUM_WORKERS` or use `$NUM_WORKERS` direclty in you sub-script
"""

import argparse
from Bio import SeqIO
from pathlib import Path
import sys

def main():
    parser = argparse.ArgumentParser(description="Count number of FASTA records.")
    parser.add_argument("--input", "-i", required=True, help="Path to FASTA file")
    args = parser.parse_args()

    fasta_path = Path(args.input)
    if not fasta_path.exists():
        print(f"Error: File not found: {fasta_path}", file=sys.stderr)
        sys.exit(1)

    try:
        count = sum(1 for _ in SeqIO.parse(str(fasta_path), "fasta"))
        print(count)   # <-- print ONLY the number
    except Exception as e:
        print(f"Error reading FASTA: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
