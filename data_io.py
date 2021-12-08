from Bio import SeqIO


def get_protein_record(g_name):
    with open("./data/proteins.faa") as handle:
        for record in SeqIO.parse(handle, "fasta"):
            if record.name == "gene-" + g_name:
                return record
