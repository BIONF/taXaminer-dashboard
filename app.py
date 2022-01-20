import os
import dash
import dash_bootstrap_components as dbc
import math
import layout
from dash import callback_context, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from utility import data_io as milts_files
from utility import dataset as ds
import required_functionalities as rf

"""
DIRECTORY FORMAT:
./data/<name of MILTS run>/gene_info
./data/<name of MILTS run>/PCA_and_clustering
./data/<name of MILTS run>/taxonomic_assignment
./data/<name of MILTS run>/proteins.faa
./data/<name of MILTS run>/taxonomic_hits.txt
"""

output_path = "./data/"
base_path = "./data/"
datasets = []
dropdowns = []

for file in os.listdir(base_path):
    d = os.path.join(base_path, file)
    if os.path.isdir(d):
        datasets.append(d + "/")
        dropdowns.append({'label': d.split("/")[-1], 'value': d + "/"})
print("Datasets", datasets)

my_dataset = ds.DataSet(datasets[0])
path = datasets[0]

# scatter matrix
scatter_test = px.scatter_matrix(my_dataset.get_data_original(),
                                 dimensions=['Dim.1', 'Dim.2', 'Dim.3'])

# creating a dictionary of the legend. Values indicate the visibility
list_of_labels = my_dataset.get_data_original()['plot_label'].tolist()
label_dictionary = dict.fromkeys(list_of_labels, True)
del label_dictionary['Unassigned']
legend_order = list(label_dictionary.keys())

# Global Settings
hover_data = ['plot_label', 'g_name', 'bh_evalue',
              'best_hit', 'taxon_assignment']
is_select_mode = False
is_remove_mode = False
recent_click_data = None
last_selection = None

# Init app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "MILTS"

my_layout = layout.Layout()
app.layout = my_layout.get_layout(dropdowns, scatter_test, my_dataset)


@app.callback(
    Output('textarea-as', 'value'),
    Input('scatter3d', 'clickData'),
    Input('searchbar', 'value'))
def print_seq_data(hover_data, search_data):
    """
    Update Sequence Data
    :param hover_data:
    :param search_data:
    :return:
    """
    if not hover_data:
        return "Hover of a data point to select it"
        # Allow user search
    if search_data:
        my_dot = search_data
    else:
        my_dot = hover_data['points'][0]['customdata'][1]
    global path
    seq = milts_files.get_protein_record(my_dot, path)
    if not seq:
        return "No matching Sequence data"
    else:
        return str(seq.seq)


@app.callback(
    Output('table_selection', 'data'),
    Output('textarea-taxon', 'value'),
    Input('scatter3d', 'clickData'),
    Input('table_selection', 'active_cell'),
    Input('table_all', 'active_cell'),
    Input('searchbar', 'value'),
    Input('button_reset', 'n_clicks'),
    Input('button_add_legend_to_select','n_clicks')
)
def select(click_data, selection_table_cell, all_table_cell, search_data, button_reset,button_add_legend_to_select):
    """
    Common function for different modes of selection from UI elements
    :param click_data: click data from scatterplot
    :param selection_table_cell: cell index from table of selected sequences
    :param all_table_cell: cell index from all table
    :param search_data: value of the searchbar
    :return: updated content for textareas and tables
    """
    my_point = ""
    global recent_click_data
    global last_selection

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    # plot click
    if click_data and click_data != recent_click_data:
        my_point = click_data['points'][0]['customdata'][1]
        recent_click_data = click_data

    # input from table of selected genes
    if selection_table_cell:
        try:
            cell = my_dataset.get_selected_data().iloc[selection_table_cell['row']]['g_name']
            if cell != last_selection:
                my_point = cell
        except IndexError:
            pass

    # input from search bar
    if search_data:
        my_point = search_data

    # Gene information
    gene_data = my_dataset.get_data_original()
    gene_data = gene_data.loc[my_dataset.get_data_original()['g_name']
                              == my_point]

    # generate text
    output_text = ""
    if gene_data.size != 0:
        output_text += "Label: " + gene_data['plot_label'].item() + "\n"
        output_text += "Gene: " + gene_data['g_name'].item() + \
                       " | Scaffold: " + gene_data['c_name'].item() + "\n"
        output_text += "Best hit: " + str(gene_data['best_hit'].item()) + \
                       " | e-value: " + str(gene_data['bh_evalue'].item())
    else:
        output_text = "No matching genes found"

    # select / unselect
    if is_select_mode:
        my_dataset.select(my_point)
    elif is_remove_mode:
        my_dataset.unselect(my_point)

    last_selection = my_point
    if changed_id == 'button_reset.n_clicks':
        my_dataset.reset_selection()

    # add visible taxa to selection
    if changed_id == 'button_add_legend_to_select.n_clicks':
        new_data = my_dataset.get_data_original().copy(deep=True)
        new_data = new_data[new_data['plot_label'] != 'Unassigned']
        for i in label_dictionary:
            if not label_dictionary[i]:
                new_data = new_data[new_data['plot_label'] != i]

        genes_list = new_data['g_name'].tolist()
        for i in genes_list:
            my_dataset.select(i)

    return my_dataset.get_selected_data().to_dict('records'),\
           output_text


@app.callback(
    Output('button_add', 'disabled'),
    Output('button_remove', 'disabled'),
    Output('button_neutral', 'disabled'),
    Input('button_add', 'n_clicks'),
    Input('button_remove', 'n_clicks'),
    Input('button_neutral', 'n_clicks'),
)
def update_selection_mode(button_add, button_remove, button_neutral):
    """
    Decide whether to add or remove data points to selection or do nothing
    :param button_add:
    :param button_remove:
    :param button_neutral:
    :return: bool values to disable certain buttons
    """
    global is_select_mode
    global is_remove_mode

    # fetch button id from context
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    # update global variables
    if changed_id == 'button_add.n_clicks':
        is_select_mode = True
        is_remove_mode = False
    elif changed_id == 'button_remove.n_clicks':
        is_select_mode = False
        is_remove_mode = True
    elif changed_id == 'button_neutral.n_clicks':
        is_select_mode = False
        is_remove_mode = False
    return is_select_mode, is_remove_mode, is_select_mode == is_remove_mode


@app.callback(
    Output('scatter3d', 'figure'),
    Output('scatter_matrix', 'figure'),
    Output('table_all', 'data'),
    Output('summary', 'value'),
    Output('table_selection', 'active_cell'),
    Input('evalue-slider', 'value'),
    Input('dataset_select', 'value'),
)
def update_dataframe(value, new_path):
    """
    Update dataset and apply filters
    :param value: value of e-value slider
    :param new_path: path to dataset
    :return: New values for UI Components
    """
    global hover_data
    global path
    global my_dataset

    # only reload the .csv if the path has changed
    if new_path != path:
        my_dataset = ds.DataSet(new_path)
    data = my_dataset.get_data_original()

    # legend selection
    global label_dictionary, legend_order
    label_dictionary = dict.fromkeys(data['plot_label'].tolist(), True)
    del label_dictionary['Unassigned']
    legend_order = list(label_dictionary.keys())

    # e-value filter
    value = 1 * math.e ** (-value)
    my_data = my_dataset.get_plot_data({'e-value': value})
    my_fig = px.scatter_3d(my_data, x='Dim.1', y='Dim.2', z='Dim.3',
                           color='plot_label', hover_data=hover_data,
                           custom_data=['taxa_color', 'g_name', 'best_hit'])

    my_fig.update_traces(marker=dict(size=3))
    my_fig.update_traces(
        hovertemplate=rf.createHovertemplate(hover_data, 2, 1))
    rf.updateColorTraces(my_fig, 0)

    my_fig.update_layout(legend=dict(title=dict(text='Taxa'),
                                     itemsizing='constant'))

    scatter_side = px.scatter_matrix(my_data,
                                     dimensions=['Dim.1', 'Dim.2', 'Dim.3'],
                                     custom_data=['g_name'])

    # load summary information
    try:
        with open(new_path + 'gene_info/summary.txt') as f:
            summary = f.readlines()
    except FileNotFoundError:
        summary = "File summary.txt not found"
    summary = "".join(summary)

    # update reference path
    path = new_path
    return my_fig, scatter_side, data.to_dict('records'), summary, None


@app.callback(
    Output('legend_selection', 'data'),
    Input('scatter3d', 'restyleData'))
def display_click_data(selectedData):
    """
    function to update the table with the Taxa visble in plot
    :param selectedData:
    :return: updated dataset to build the table new according to the visible parts of the legend
    """
    # removing error at the start of the program
    if selectedData is None:
        return my_dataset.get_data_original().to_dict('records')

    # updating the legend dictionary with the input
    update_dict = dict(zip(selectedData[1], selectedData[0]["visible"]))
    for i in update_dict:
        if update_dict[i] == "legendonly":
            label_dictionary[legend_order[i]] = False
        else:
            label_dictionary[legend_order[i]] = True

    # assembling output
    new_data = my_dataset.get_data_original().copy(deep=True)
    new_data = new_data[new_data['plot_label'] != 'Unassigned']
    for i in label_dictionary:
        if not label_dictionary[i]:
            new_data = new_data[new_data['plot_label'] != i]

    return new_data.to_dict('records')


@app.callback(
    Output('NCBI', 'href'),
    Input('scatter3d', 'clickData'))
def print_link(click_data):
    """
    Build a NCBI search term link upon Button press
    :param click_data: Selected datapoint in scatterplot
    :return: search term link
    """
    # catch invalid data
    if not click_data:
        return ""
    else:
        # build link
        output_link = ""
        output_link += "http://www.ncbi.nlm.nih.gov/taxonomy/?term="
        output_link += click_data['points'][0]['customdata'][2]
        return output_link


@app.callback(
    Output("download-selection", "data"),
    Input('btn-download', 'n_clicks'),
    prevent_initial_call=True
)
def download(click_data):
    """
    Complie a new .fasta file of as-sequences based on the users selection
    :param click_data: data from the corresponding button
    :return: dcc.send_file
    """
    link = milts_files.write_protein_sequences(my_dataset.selection_keys, path)
    return dcc.send_file(link)


if __name__ == "__main__":
    app.run_server(host='127.0.0.1', port='8050', debug=True)
