import json
import re
import pandas as pd
import required_functionalities as rf


class DataSet:
    """
    Represents a loaded dataset and supports selection
    """
    def __init__(self, path=None):
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
        if path:
            self.original_data = pd.read_csv(path + "taxonomic_assignment/gene_table_taxon_assignment.csv")

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
                print("[WARN] Failed to read taxonomic_hits.txt")

        else:
            # emtpy data for taxonomic_hits
            self.taxonomic_hits = None
            # emtpy standard dataframe
            self.original_data = pd.DataFrame(data=[], columns=['g_name', 'c_name', 'c_num_of_genes', 'c_len',
                                            'c_pct_assemby_len','c_genelenm', 'c_genelensd', 'c_cov_0', 'c_covsd_0',
                                            'c_covdev_0','c_genecovm_0', 'c_genecovsd_0', 'c_pearson_r', 'c_pearson_p',
                                            'c_gc_cont', 'c_gcdev', 'g_len', 'g_lendev_c', 'g_lendev_o', 'g_abspos',
                                            'g_terminal', 'g_single', 'g_cov_0', 'g_covsd_0', 'g_covdev_c_0',
                                            'g_covdev_o_0', 'g_pearson_r_o', 'g_pearson_p_o', 'g_pearson_r_c',
                                            'g_pearson_p_c', 'g_gc_cont', 'g_gcdev_c', 'g_gcdev_o', 'Dim.1',
                                            'Dim.2', 'Dim.3', 'protID', 'lcaID', 'lca', 'best_hitID', 'best_hit',
                                            'bh_evalue', 'corrected_lca', 'taxon_assignment', 'plot_label'])

        # init selection keys
        self.selection_keys = set()

    def get_data_original(self):
        """
        Returns the unmodified dataframe as read from the .csv file on init
        :return: pandas dataframe
        """
        return self.original_data

    def get_plot_data(self, filters, color_root=None):
        """
        Builds a modified dataframe to be fed to plotly
        :param filters: current filters
        :param color_root a color hex string, which define the pole label color.
        :return: a modified dataframe
        """
        original_data = self.original_data
        e_value = filters.get('e-value')
        plot_data = original_data[original_data.bh_evalue < e_value]

        # add
        # color legend
        color_data = pd.DataFrame({'plot_label': plot_data['plot_label'].unique(),
                                   'taxa_color': rf.qualitativeColours(
                                       len(plot_data['plot_label'].unique()), color_root)
                                   })

        plot_data = plot_data.merge(color_data, left_on='plot_label', right_on='plot_label')

        # modify plot label to show appearance data
        taxon_counts = dict(plot_data['plot_label'].value_counts())
        for index, row in plot_data.iterrows():
            new_label = row['plot_label'] + " (" + str(taxon_counts.get(row['plot_label'])) + ")"
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
            my_rows = taxonomic_hits[taxonomic_hits['qseqid'] == protID].copy(deep=True)

            # show only the first hit
            for index, row in my_rows.iterrows():
                # truncate e-value
                my_rows.at[index, 'evalue'] = '{:.3g}'.format(row['evalue'])
                # only return the first name/id
                my_rows.at[index, 'sscinames'] = str(row['sscinames']).split(';')[0]
                my_rows.at[index, 'staxids'] = str(row['staxids']).split(';')[0]
            return my_rows

    def get_selectable_variables(self, table_format=True):
        """
        Get information on all available variables.
        To be used with dash dropdown selectors
        :param: table_format if false return only variable names
        :return: list of dicts or if table_format list of strings
        """
        my_dataset = self.original_data
        variable_items = []

        # glossary data
        with open("./static/glossary.json") as f:
            glossary = json.load(f)

        variables = my_dataset.columns.values.tolist()

        # return only list of keys
        if not table_format:
            return variables

        # build dicts
        for variable in variables:
            clean_name, my_number = self.clean_trailing_indices(variable)

            if clean_name in glossary:
                variable_items.append(
                    {"label": str(glossary[clean_name]['short']) + " " + my_number,
                     "value": str(variable),
                     "title": glossary[clean_name]['details']})
            else:
                variable_items.append(
                    {"label": str(variable), "value": str(variable)})

        return variable_items

    def clean_trailing_indices(self, variable_name):
        """
        Separates the trailing indices of variables
        :param variable_name: Name of the variable (string)
        :return: tuple of name, index
        """
        my_number = re.findall(r"\d+", variable_name)
        number_str = ""
        if len(my_number) > 0:
            number_str = str(my_number[0])

        # remove index
        clean_name = re.sub(r"\d+", "", variable_name)

        return clean_name, number_str

    def export_csv(self, cols, path):
        """
        Export the selection table to .csv
        :param cols:
        :param selection_keys:
        :return:
        """
        original_data = self.original_data

        # ensure out identifier is present
        if 'g_name' not in cols:
            cols.append('g_name')

        # filter cols
        data = original_data[original_data.columns.intersection(cols)]
        # filter rows
        data = data[data['g_name'].isin(list(self.selection_keys))]

        # export .csv
        data.to_csv(path + '/selection.csv', index=False)

        return path + 'selection.csv'
