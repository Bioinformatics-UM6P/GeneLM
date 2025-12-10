from Bio import SeqIO
from Bio.Seq import Seq
from Bio.Data import CodonTable
import sys, os

def parse_gff(gff_path):
    features = []
    with open(gff_path, "r") as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.strip().split("\t")
            if len(parts) != 9:
                continue

            seqid, source, feature_type, start, end, score, strand, phase, attributes = parts

            # we extract CDS feature
            if feature_type.lower() not in ["cds", "gene"]:
                continue

            # we parse ID or name from attributes
            attrs = dict(
                item.split("=", 1) if "=" in item else (item, "")
                for item in attributes.split(";")
            )

            feature_id = attrs.get("ID", None) or attrs.get("Name", None) or f"{feature_type}_{start}_{end}"

            features.append({
                "seqid": seqid,
                "type": feature_type,
                "start": int(start),
                "end": int(end),
                "strand": strand,
                "id": feature_id
            })
    return features


def extract_sequences(fasta_path, gff_path, output_dir, codon_table=11):
    os.makedirs(output_dir, exist_ok=True)
    
    # input
    genome = SeqIO.to_dict(SeqIO.parse(fasta_path, "fasta"))
    features = parse_gff(gff_path)

    # output setup
    orf_path = os.path.join(output_dir, "predicted_orfs.fasta")
    prot_path = os.path.join(output_dir, "predicted_proteins.fasta")
    orf_out = open(orf_path, "w")
    prot_out = open(prot_path, "w")
    codon_table = CodonTable.unambiguous_dna_by_id[codon_table]  # Bacterial table

    for feat in features:
        seq_record = genome[feat["seqid"]]
        start = feat["start"] - 1  # GFF is 1-based
        end = feat["end"]          # Python slicing is end-exclusive
        
        dna = seq_record.seq[start:end]

        if feat["strand"] == "-":
            dna = dna.reverse_complement()

        # translate
        try:
            protein = dna.translate(table=codon_table, to_stop=True)
        except Exception:
            protein = Seq("")

        # write ORF
        orf_out.write(f">{feat['seqid']}:{feat['start']}-{feat['end']}({feat['strand']}) | {feat['id']}\n")
        orf_out.write(str(dna) + "\n")

        # write protein
        prot_out.write(f">{feat['seqid']}:{feat['start']}-{feat['end']}({feat['strand']}) | {feat['id']}\n{protein}\n")

    orf_out.close()
    prot_out.close()
    print(f"Done! Files written to: {output_dir}")
    print("- predicted_orfs.fasta")
    print("- predicted_proteins.fasta")


if __name__ == "__main__":
    # Usage:
    # python extract_orf_protein.py genome.fasta annotation.gff [output_dir] [--codon_table 11]
    # Convert to simple argument parser handling both positional and optional args
    import argparse
    parser = argparse.ArgumentParser(
        description="Extract ORFs and translated proteins from FASTA + GFF."
    )
    parser.add_argument("fasta", help="Input genome FASTA")
    parser.add_argument("gff", help="GFF annotation")
    parser.add_argument("output_dir", nargs="?", default=".", help="Output directory (optional)")
    parser.add_argument(
        "--codon_table",
        type=int,
        default=11,
        help="NCBI codon table ID (default: 11 — Bacterial/Archaeal)"
    )
    args = parser.parse_args()

    extract_sequences(
        args.fasta,
        args.gff,
        args.output_dir,
        args.codon_table
    )
