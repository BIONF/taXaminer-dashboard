from Bio import SeqIO
import os


def get_protein_record(g_name, path):
    """
    Get a protein record based on key
    :param g_name: gene Nominator
    :param path: path to dataset
    :return: SeqIO.record
    """
    try:
        with open(path + "/proteins.faa") as handle:
            for record in SeqIO.parse(handle, "fasta"):
                if record.name == "gene-" + g_name:
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

    genes = list(genes)
    for i, gene in enumerate(genes):
        genes[i] = "gene-" + gene

    with open(path + "/proteins.faa") as handle:
        for record in SeqIO.parse(handle, "fasta"):
            if record.name in genes:
                as_sequences.append(record)

    with open(path + "/selected_proteins.fasta", "w") as handle:
        SeqIO.write(as_sequences, handle, "fasta")

    return os.path.abspath(path + "/selected_proteins.fasta")

