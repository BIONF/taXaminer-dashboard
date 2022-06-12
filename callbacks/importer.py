"""
Importer for callbacks split across multiple files
"""
from callbacks import clientside, contig_selection


def import_callbacks(app):
    """
    Import callbacks split across multiple files
    :param app:
    :return:
    """
    clientside.import_callbacks(app)
    contig_selection.import_callbacks(app)

