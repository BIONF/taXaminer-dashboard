from Bio import SeqIO
import os


def get_protein_record(prot_id, path):
    """
    Get a protein record based on key
    :param prot_id: protein ID as used in proteins.faa
    :param path: path to dataset
    :return: SeqIO.record
    """
    try:
        with open(path + "/proteins.faa") as handle:
            for record in SeqIO.parse(handle, "fasta"):
                if record.name == prot_id:
                    return record
    except FileNotFoundError:
        return None


def write_protein_sequences(genes, path):
    """
    Compile a .fasta from a selection of sequences from proteins.faa
    :param genes: gene nominators
    :param path:path to proteins.faa
    :return:filesystem path to new file
    """
    as_sequences = []

    with open(path + "/proteins.faa") as handle:
        for record in SeqIO.parse(handle, "fasta"):
            if record.name in genes:
                as_sequences.append(record)

    with open(path + "/selected_proteins.fasta", "w") as handle:
        SeqIO.write(as_sequences, handle, "fasta")

    return os.path.abspath(path + "/selected_proteins.fasta")

