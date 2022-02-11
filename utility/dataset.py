import pandas as pd
import required_functionalities as rf


class DataSet:
    """
    Represents a loaded dataset and supports selection
    """
    def __init__(self, path):
        # column names according to the diamond documentation
        taxonomic_hits_rows = ['qseqid', 'sseqid', 'pident', 'length',
                               'mismatch', 'gapopen', 'qstart', 'qend',
                               'sstart', 'send', 'evalue', 'bitscore',
                               'staxids', 'sscinames']
        # manually assert datatypes to save computing time
        taxonomic_hits_dtypes = {'qseqid': str, 'sseqid': str, 'pident': float,
                                 'lenght': int, 'mismatch': int,
                                 'gapopen': int, 'qstart': int, 'gend': int,
                                 'sstart': int, 'send': int, 'evalue': float,
                                 'bitscore': float, 'staxids': str,
                                 'sscinames': str}

        # read data
        self.original_data = pd.read_csv(
            path + "taxonomic_assignment/gene_table_taxon_assignment.csv")

        # fetch taxonomic hits, this may take a while
        try:
            self.taxonomic_hits = pd.read_csv(path + 'taxonomic_hits.txt',
                                              header=None,
                                              encoding='unicode_escape',
                                              sep='\t',
                                              names=taxonomic_hits_rows,
                                              dtype=taxonomic_hits_dtypes,
                                              skip_blank_lines=True)
        except ValueError:
            self.taxonomic_hits = None
            print("Failed to read taxonomic_hits.txt, the file might be corrupted!")

        # init selection keys
        self.selection_keys = set()

    def get_data_original(self):
        """
        Returns the unmodified dataframe as read from the .csv file on init
        :return: pandas dataframe
        """
        return self.original_data

    def get_plot_data(self, filters):
        """
        Builds a modified dataframe to be fed to plotly
        :param filters: current filters
        :return: a modified dataframe
        """
        original_data = self.original_data
        e_value = filters.get('e-value')
        plot_data = original_data[original_data.bh_evalue < e_value]

        # add
        # color legend
        color_data = pd.DataFrame(
            {'plot_label': plot_data['plot_label'].unique(),
             'taxa_color': rf.qualitativeColours(
                 len(plot_data['plot_label'].unique()))})
        plot_data = plot_data.merge(color_data, left_on='plot_label',
                                    right_on='plot_label')

        # modify plot label to show appearance data
        taxon_counts = dict(plot_data['plot_label'].value_counts())
        for index, row in plot_data.iterrows():
            new_label = row['plot_label'] + " (" + str(
                taxon_counts.get(row['plot_label'])) + ")"
            plot_data.at[index, 'plot_label'] = new_label
        return plot_data

    def selected_merge(self, data=None):
        """
         Get a pandas dataframe of currently 'selected' column.
        :param data: A pandas dataframe to use.
        :return: Complete and supplemented  pandas dataframe.
        """
        if data is None:
            data = self.original_data

        if len(self.selection_keys) == 0:
            return data.assign(selected=False)

        if len(self.selection_keys) == len(data.index):
            return data.assign(selected=True)

        return (data[~data['g_name'].isin(self.selection_keys)].assign(selected=False)).append(
                data[data['g_name'].isin(self.selection_keys)].assign(selected=True))

    def get_selected_data(self, data=None):
        """
        Get a pandas dataframe of currently selected rows
        :param data: A pandas dataframe to use.
        :return: Filtered pandas dataframe.
        """
        if data is None:
            data = self.original_data

        if len(self.selection_keys) == 0:
            cols = data.columns
            empty_frame = pd.DataFrame(columns=cols)
            return empty_frame
        # select by keys
        return data[data['g_name'].isin(self.selection_keys)]

    def get_unselected_data(self, data=None):
        """
        Get a pandas dataframe of currently not selected rows.
        :param data: A pandas dataframe to use.
        :return: Filtered pandas dataframe.
        """
        if data is None:
            data = self.original_data

        if len(self.selection_keys) == 0:
            return data
        # select by keys
        return data[~data['g_name'].isin(self.selection_keys)]

    def select(self, key):
        """
        Add a key to the selection
        :param key: the g_name
        :return:
        """
        self.selection_keys.add(key)

    def unselect(self, key):
        """
        Remove a key from the selection
        :param key: th g_name
        :return:
        """
        try:
            self.selection_keys.remove(key)
        except KeyError:
            print("Can't unselect a not selected element: " + key)

    def reset_selection(self):
        """
        Dump all keys
        :return:
        """
        self.selection_keys = set()

    def get_protID(self, gene_name):
        """
        Fetch the protID associated with a given g_name
        :param gene_name:
        :return:
        """
        original_data = self.original_data
        my_id = original_data.loc[original_data['g_name'] == gene_name][
            'protID'].item()
        return my_id

    def get_taxonomic_hits(self, protID):
        """
        Fetch rows from taxonomic_hits.txt matching the protID
        :param protID: protID observed
        :return: pandas dataframe
        """
        taxonomic_hits = self.taxonomic_hits
        if taxonomic_hits is None:
            return None
        else:
            # return a proper copy (avoid SettingWithCopyWarning)
            return taxonomic_hits[taxonomic_hits['qseqid'] == protID].copy(deep=True)


