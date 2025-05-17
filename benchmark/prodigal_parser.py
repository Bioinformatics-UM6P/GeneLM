import re
import os
import sys

def parse_prodigal_genes(file_path):
    output_gff = os.path.splitext(file_path)[0] + ".gff"

    with open(file_path, "r") as infile, open(output_gff, "w") as outfile:
        outfile.write("##gff-version 3\n")

        lines = infile.readlines()
        seq_id = None 
        for i, line in enumerate(lines):
            line = line.strip()
            
            if line.startswith("DEFINITION"):
                match = re.search(r'seqhdr="([^"]+)"', line)
                if match:
                    seq_id = match.group(1)
            elif line.startswith("CDS"):
                match = re.search(r'(\d+)\.\.(\d+)', line)
                complement_match = re.search(r'complement\((\d+)\.\.(\d+)\)', line)
                if match:
                    start, end, strand = int(match.group(1)), int(match.group(2)), "+"
                elif complement_match: 
                    start, end, strand = int(complement_match.group(1)), int(complement_match.group(2)), "-"

                if i + 1 < len(lines) and "/note=" in lines[i + 1]:
                    note_data = lines[i + 1].split("/note=")[-1].strip().replace('"', '')
                else:
                    note_data = ""

                attributes = {}
                for item in note_data.split(";"):
                    key_value = item.split("=")
                    if len(key_value) == 2:
                        attributes[key_value[0]] = key_value[1]

                gff_attributes = f'ID={attributes.get("ID", "unknown")};start_type={attributes.get("start_type", "NA")};stop_type={attributes.get("stop_type", "NA")};gc_cont={attributes.get("gc_cont", "NA")};score={attributes.get("score", "NA")}'
                outfile.write(f"{seq_id}\tProdigal\tCDS\t{start}\t{end}\t.\t{strand}\t0\t{gff_attributes}\n")

    print(f"conversion completed! ")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_genes_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    if not os.path.isfile(input_file):
        print(f"error: File '{input_file}' not found!")
        sys.exit(1)

    parse_prodigal_genes(input_file)
