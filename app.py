import os
import dash
import dash_bootstrap_components as dbc
from dash.dash_table.Format import Format, Scheme
from dash.exceptions import PreventUpdate

import layout
from dash import callback_context, dcc
from dash.dependencies import Input, Output, State
import plotly.express as px

# math
import math
import pandas as pd
import numpy as np

# local dependencies
from utility import protein_io as milts_files
from utility import dataset as ds
from utility import transformation
import required_functionalities as rf
import json

import plotly.graph_objs as go

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

# data set globals
path = None
my_dataset = ds.DataSet()

list_of_labels = []
label_dictionary = {}
legend_order = {}

# load glossary once
with open("./static/glossary.json") as f:
    glossary = json.load(f)

# Global Settings
is_select_mode = False
is_remove_mode = False
recent_click_data = None
recent_click_scat_data = None
recent_select_data = None
last_selection = None
is_dataset_switch = False

# Init app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP,
                                                dbc.icons.FONT_AWESOME])
app.title = "MILTS"

my_layout = layout.Layout()
app.layout = my_layout.get_layout(dropdowns)


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
    global path
    if not path:
        raise PreventUpdate

    if not hover_data:
        return "Hover of a data point to select it"
        # Allow user search
    if search_data:
        my_dot = search_data
    else:
        # fetch protID from hover data
        my_dot = hover_data['points'][0]['customdata'][3]
    seq = milts_files.get_protein_record(my_dot, path)
    if not seq:
        return "No matching Sequence data"
    else:
        return str(seq.seq)


@app.callback(
    Output('variable-info', 'value'),
    Input('contribution', 'clickData'))
def show_variable_description_pca(click_data):
    """
    gives a description to each of the variables when their point is clicked in the Graph
    :param click_data:
    :return:
    """

    if not click_data:
        return "Click on a data point to get a short description of the variable"

    my_dot = click_data['points'][0]['customdata'][0]

    if not my_dot:
        return "No matching data"
    else:
        return str(my_dot)


@app.callback(
    Output('table_selection', 'columns'),
    Output('legend_selection', 'columns'),
    Input('variable-selection', 'value'),
    Input('table_selection', 'columns'),
    Input('legend_selection', 'columns'),
    Input('variable-selection', 'options'),
    prevent_initial_call=True
)
def update_table_columns(selected_vars, sel_cols, legend_cols, options):
    """
    Update the column visible in all tabels
    :param selected_vars: selection of dataframe columns to be shown
    :param sel_cols: current cols of 'selected' table
    :param legend_cols: current cols of 'legend'
    :return: columns as list
    """

    # select table columns
    columns = []
    # if selection has changed : build new column list
    available_vars = my_dataset.get_selectable_variables(table_format=False)
    if selected_vars:
        for variable in selected_vars:

            # catch variables from previous dataset not available in current
            if variable not in available_vars:
                continue

            variable_dict = dict(id=variable)
            if variable == "bh_evalue":
                # truncate e-value
                variable_dict['format'] = Format(precision=2,
                                                 scheme=Scheme.decimal_or_exponent)
            variable_dict['type'] = "numeric"

            clean_name, my_number = my_dataset.clean_trailing_indices(variable)

            # use human-readable column names
            if clean_name in glossary:
                var_name = glossary[clean_name]['short'] + " " + my_number
                variable_dict['name'] = var_name
            else:
                variable_dict['name'] = str(variable)

            # add column
            columns.append(variable_dict)

        sel_cols = legend_cols = columns
    return sel_cols, legend_cols


@app.callback(
    Output('table_selection', 'data'),
    Output('textarea-taxon', 'value'),
    Output('table_selection', 'active_cell'),
    Output('table-hits', 'data'),
    Input('scatter3d', 'clickData'),
    Input('scatter_matrix', 'clickData'),
    Input('scatter_matrix', 'selectedData'),
    Input('table_selection', 'active_cell'),
    Input('searchbar', 'value'),
    Input('button_reset', 'n_clicks'),
    Input('button_add_legend_to_select', 'n_clicks'),
    Input('btn-reload', 'n_clicks'),
)
def select(click_data, click_scat_data, select_data, selection_table_cell, search_data,
           button_reset, button_add_legend_to_select, reload):
    """
    Common function for different modes of selection from UI elements
    :param click_data: click data from scatterplot
    :param select_data: select data from scatter matrix
    :param selection_table_cell: cell index from table of selected sequences
    :param search_data: value of the searchbar
    :return: updated content for textareas and tables
    """

    taxonomic_hits = None
    my_point = ""
    prot_id = None
    global recent_click_data
    global recent_click_scat_data
    global recent_select_data
    global last_selection
    global glossary

    global path
    if not path:
        raise PreventUpdate

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    # scatter matrix select
    if select_data and select_data != recent_select_data:
        recent_select_data = select_data
        for it in (select_data['points']):
            # Node that neutral mode will also select.
            if is_remove_mode:
                my_dataset.unselect(it['customdata'][1])
            else:
                my_dataset.select(it['customdata'][1])
    else:
        # Click in scatter matrix to select a single point.
        if click_scat_data and click_scat_data != recent_click_scat_data:
            recent_click_scat_data = click_scat_data
            if is_remove_mode:
                my_dataset.unselect(
                    click_scat_data['points'][0]['customdata'][1])
            else:
                my_dataset.select(
                    click_scat_data['points'][0]['customdata'][1])

    # plot click
    if click_data and click_data != recent_click_data:
        my_point = click_data['points'][0]['customdata'][1]
        recent_click_data = click_data
        prot_id = click_data['points'][0]['customdata'][3]

    # input from table of selected genes
    if selection_table_cell:
        try:
            cell = \
                my_dataset.get_selected_data().iloc[
                    selection_table_cell['row']][
                    'g_name']
            if cell != last_selection:
                my_point = cell
                prot_id = my_dataset.get_protID(my_point)
        except IndexError:
            pass

    # taxonomic hits
    if prot_id:
        taxonomic_hits = my_dataset.get_taxonomic_hits(prot_id)

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
                       " | Contig: " + gene_data['c_name'].item() + "\n"
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

    # load save
    if changed_id == 'btn-reload.n_clicks':
        file_path = path + "savefile.txt"
        save_file = open(file_path, 'r')
        content = save_file.read()
        line_list = content.split("||")
        for i in range(len(line_list)):
            my_dataset.select(line_list[i])

    # create savefile
    if click_data:
        file_path = path + "savefile.txt"
        save_file = open(file_path, 'w+')
        set_data = my_dataset.selection_keys
        list_data = list(set_data)

        for gene in range(len(list_data)):
            save_file.write(list_data[gene] + "||")

    # taxonomic hit table
    if taxonomic_hits is not None:
        # drop unsued rows
        taxonomic_hits.drop(['qseqid', 'sseqid'], axis=1, inplace=True)
        taxonomic_hits = taxonomic_hits.to_dict('records')

    return my_dataset.get_selected_data().to_dict('records'), output_text, None, taxonomic_hits


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
    Output('summary', 'value'),
    Output('contribution', 'figure'),
    Output('scree', 'figure'),
    Output('variable-selection', 'options'),
    Output('btn-sync', 'n_clicks'),
    Input('evalue-slider', 'value'),
    Input('dataset_select', 'value'),
    Input('colorscale-select', 'value'),
    State('slider-dot-size', 'value'),
    State('scatter3d', 'relayoutData')
)
def update_dataframe(value, new_path, color_root, dot_size, relayout):
    """
    Update dataset and apply filters
    :param value: value of e-value slider
    :param new_path: path to dataset
    :param color_root a color hex string, which define the pole label color.
    :param dot_size size of the plot dots.
    :return: New values for UI Components
    """

    global my_dataset
    global path

    # Indicate a change of dataset
    global is_dataset_switch
    is_dataset_switch = True

    # observer which component was updated
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    # update camera / legend?
    update_layout = True
    if changed_id in ['colorscale-select.value', 'slider-dot-size.value']:
        update_layout = False

    # only reload the .csv if the path has changed
    if new_path != path:
        my_dataset = ds.DataSet(new_path)
        path = new_path

    if not path:
        raise PreventUpdate

    data = my_dataset.get_data_original()

    # legend selection
    global label_dictionary, legend_order
    label_dictionary = dict.fromkeys(data['plot_label'].tolist(), True)
    if 'Unassigned' in label_dictionary:
        del label_dictionary['Unassigned']
    legend_order = list(label_dictionary.keys())

    # e-value filter
    value = 1 * math.e ** (-value)
    my_data = my_dataset.get_plot_data({'e-value': value}, color_root)

    my_fig = px.scatter_3d(my_data, x='Dim.1', y='Dim.2', z='Dim.3',
                           color='plot_label',
                           hover_data=['plot_label', 'g_name', 'best_hit',
                                       'bh_evalue', 'taxon_assignment',
                                       'c_name'],
                           custom_data=['taxa_color', 'g_name', 'best_hit',
                                        'protID', 'bh_evalue'])
    # keep existing camera position.
    if relayout and 'scene.camera' in relayout:
        my_fig.update_layout(scene_camera=relayout['scene.camera'])

    my_fig.update_traces(marker=dict(size=dot_size))

    hover_template = "%{customdata[5]} <br> " \
                     "%{customdata[1]} <br>" \
                     "<extra>Best hit: %{customdata[2]} <br>" \
                     "Best hit e-value: %{customdata[4]} <br>" \
                     "Taxonomic assignment: %{customdata[6]} <br>" \
                     "Contig name: %{customdata[7]} <br></extra>"
    my_fig.update_traces(hovertemplate=hover_template)
    rf.SetCustomColorTraces(my_fig, 0)

    # add Demo Button
    my_fig.update_layout(
        legend=dict(title=dict(text='Taxa'), itemsizing='constant'),
        updatemenus=[dict(
            type='buttons',
            y=1, x=1, xanchor='right', yanchor='bottom',
            pad=dict(t=10, r=10),
            buttons=[dict(label='Auto-rotate',
                          method='animate',
                          args=[None, dict(frame=dict(duration=5, redraw=True),
                                           transition=dict(duration=0),
                                           fromcurrent=True,
                                           mode='immediate')]
                          )]
        )])

    # add autorotate frames
    frames = []
    for t in np.arange(0, 6.26, 0.1):
        # camera coordinates of next step
        x, y, z = transformation.rotate_z(-1.25, 2, 0.5, -t)
        frames.append(
            go.Frame(layout=dict(scene_camera_eye=dict(x=x, y=y, z=z))))
    my_fig.frames = frames

    # contribution of variables
    contribution_data = pd.read_csv(
        new_path + "PCA_and_clustering/PCA_results/pca_loadings.csv")
    labels_pca = list(contribution_data.iloc[:, 0])

    # PCA plot
    details_list = []
    for i in labels_pca:
        clean_name, my_number = my_dataset.clean_trailing_indices(i)

        if clean_name in glossary:
            labels_pca[labels_pca.index(i)] = glossary[clean_name]['short'] + " " + my_number
            details_list.append(glossary[clean_name]["details"])
        else:
            details_list.append("")

    pc1 = contribution_data.get("PC1")
    pc2 = contribution_data.get("PC2")
    pc3 = contribution_data.get("PC3")
    pc_len = (len(pc3) if len(pc3) < len(pc1) else len(pc1)) if len(pc1) < len(pc2) else \
        (len(pc3) if len(pc3) < len(pc2) else len(pc2))

    contribution_fig = px.scatter_3d(contribution_data,
                                     title="Contribution of variables",
                                     x="PC1", y="PC2", z="PC3",
                                     range_x=[-1, 1], range_y=[-1, 1],
                                     range_z=[-1, 1],
                                     color=labels_pca,
                                     hover_data=[details_list],
                                     height=550)

    # get points
    point_list_x = []
    point_list_y = []
    point_list_z = []

    for x in range(pc_len):
        point_list_x.append(pc1[x])
        point_list_y.append(pc2[x])
        point_list_z.append(pc3[x])

    # calc x,y,z
    vector_list_x = []
    vector_list_y = []
    vector_list_z = []
    for i in range(pc_len):
        vector_list_x.append(0)
        vector_list_x.append(point_list_x[i])
        vector_list_y.append(0)
        vector_list_y.append(point_list_y[i])
        vector_list_z.append(0)
        vector_list_z.append(point_list_z[i])

    # update Scatter
    contribution_fig.add_traces(go.Scatter3d(name="Arrows", mode="lines",
                                             x=vector_list_x,
                                             y=vector_list_y,
                                             z=vector_list_z,
                                             showlegend=True,
                                             hoverinfo='skip'))

    contribution_fig.update_traces(textposition='top center',
                                   marker_size=5,
                                   hovertemplate=None)
    # legend
    contribution_fig.update_layout(legend=dict(orientation="v",
                                               itemsizing='constant'))

    # scree plot
    pca_data = pd.read_csv(
        new_path + "PCA_and_clustering/PCA_results/pca_summary.csv")
    pca_resolution = 5
    proportion_of_variance = []
    pca_ids = []
    for i in range(1, pca_resolution + 1):
        curr_value = pca_data.get("PC" + str(i))
        pca_ids.append("PC" + str(i))
        proportion_of_variance.append(curr_value[1])

    pca_data = pd.DataFrame(proportion_of_variance, pca_ids)
    scree_fig = px.bar(pca_data,
                       title="Scree Plot",
                       height=300)
    scree_fig.update_layout(yaxis_title="Contribution to total variance",
                            showlegend=False)

    # load summary information
    try:
        with open(new_path + 'gene_info/summary.txt') as f:
            summary = f.readlines()
    except FileNotFoundError:
        summary = "File summary.txt not found"
    summary = "".join(summary)

    # update legend / selection / view flag
    my_fig.layout.uirevision = not update_layout

    # variable selector
    variables = my_dataset.get_selectable_variables()

    # set n_clicks = 0 to toggle plot table reload
    return my_fig, summary, contribution_fig, scree_fig, variables, 0


@app.callback(
    Output('scatter_matrix', 'figure'),
    Input('evalue-slider', 'value'),
    Input('scatter3d', 'figure'),
    Input('table_selection', 'data')
)
def updateScatterMatrix(value, scat_3d, legend):
    """
     Update scatter matrix with current selection.
    :param value: Value of e-value slider.
    :param scat_3d: scat_3d figure to trigger graph updates.
    :param legend: legend_selection columns changes trigger.
    :return:
    """
    global my_dataset
    value = 1 * math.e ** (-value)
    my_data = my_dataset.get_plot_data({'e-value': value})
    scatter_side = px.scatter_matrix(my_dataset.selected_merge(my_data),
                                     dimensions=['Dim.1', 'Dim.2', 'Dim.3'],
                                     color='selected',
                                     custom_data=['selected', 'g_name'])

    scatter_side.update_traces(hovertemplate='%{customdata[1]}<br>%{xaxis.title.text}=%{x}<br>%{yaxis.title.text}=%{'
                                             'y}<extra></extra>',
                               showlegend=False)

    # Override random plotly colors, because they going crazy.
    for it in range(0, len(scatter_side.data)):
        if scatter_side.data[it]['customdata'][0][0]:
            scatter_side.data[it]['marker']['color'] = "#DC143C"
        else:
            pass
            scatter_side.data[it]['marker']['color'] = "#636efa"

    return scatter_side


@app.callback(
    Output('legend_selection', 'data'),
    Input('scatter3d', 'restyleData'),
    Input('btn-sync', 'n_clicks'),
    Input('legend_selection', 'data')
)
def display_click_data(selectedData, n_clicks, curr_data):
    """
    function to update the table with the Taxa visble in plot
    :param selectedData:
    :return: updated dataset to build the table new according to the visible parts of the legend
    """

    # init an empty table on dataset switch
    global is_dataset_switch
    if is_dataset_switch:
        # toggle
        is_dataset_switch = False
        return None

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if changed_id != 'btn-sync.n_clicks':
        return curr_data

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
    prot_ids = []
    key_list = list(my_dataset.selection_keys)

    # replace by protIDs
    for key in key_list:
        prot_ids.append(my_dataset.get_protID(key))
    link = milts_files.write_protein_sequences(prot_ids, path)
    return dcc.send_file(link)


@app.callback(
    Output("download-csv", "data"),
    Input('btn-csv', 'n_clicks'),
    Input('variable-selection', 'value'),
    prevent_initial_call=True
)
def download_csv(click_data, cols):
    """
    Download a section of the pandas dataframe as defined by the selection
    table
    :param click_data:
    :return: dcc.sendfile()
    """

    # don't trigger a download if only the variable selection has changed
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if changed_id == 'variable-selection.value':
        return None

    # build download link
    link = my_dataset.export_csv(cols, path)
    return dcc.send_file(link)


@app.callback(
    Output('table-hits', 'columns'),
    Input('variable-selection-diamond', 'value'),
    prevent_initial_call=True
)
def update_diamond_columns(selected_vars):
    """
    Update the columns of the diamond data table
    :param selected_vars: variables selcted by user
    :return: selected cols as list
    """
    columns = []
    for variable in selected_vars:
        columns.append({"name": variable, "id": variable})
    return columns


app.clientside_callback(
    """
    function( value){
    // Copy the chosen value from dataset_startup_selec to dataset_select
    // :param value: selected dataset
    // :return: tuple with zero to hide the modal and value chosen dataset
    return [false, value]
    }
    """,
    Output("mod1", "is_open"),
    Output("dataset_select", "value"),
    Input("dataset_startup_select", "value"),
    prevent_initial_call=True)

app.clientside_callback("""
    function(fig, restyle, toggle_dot_auto){
        const triggered = dash_clientside.callback_context.triggered.map(t => t.prop_id);

         var scatDiv = document.getElementById('scatter3d')

        if(scatDiv == undefined || scatDiv.children == undefined || scatDiv.children.length < 2){return undefined;}  
        if(fig === undefined || fig['data'] === undefined){return undefined;}
        if(triggered.includes('scatter3d.restyleData')){
        if(restyle !== undefined && restyle[0] !== undefined && restyle[0]['visible'] === undefined){return undefined;}
        }

        var list_visible = []
        var data_size = 0
        for (it = 0; it < fig['data'].length; it++){
            if(fig['data'][it]['visible'] === undefined || fig['data'][it]['visible'] == true){  
                data_size += fig['data'][it]['x'].length
                list_visible.push(fig['data'][it]['name'])
            }
        }
        
        // prevent math error and check auto dot size active 
        if (data_size <= 0 || !toggle_dot_auto){
            return list_visible;
        }
        
        var new_size = Math.round((800*data_size)/Math.pow(data_size, 1.12))/100;
        var update = {'marker.size': new_size};
        window.Plotly.restyle(scatDiv.children[1], update);

        return list_visible;
    }
    """,
                        Output('taxa_info1', 'data'),
                        Input('scatter3d', 'figure'),
                        Input('scatter3d', 'restyleData'),
                        Input('toggle-dot-size', 'value'))

app.clientside_callback("""
    function(toggle_dot_auto, dot_size){
        var scatDiv = document.getElementById('scatter3d')
        if(scatDiv == undefined || scatDiv.children == undefined || scatDiv.children.length < 2){return "";}  
        
        if(!toggle_dot_auto){
            var update = {'marker.size': dot_size};
            window.Plotly.restyle(scatDiv.children[1], update);
        }
        return "";
    }
    """,
                        Output('dummy-1', 'children'),
                        Input('toggle-dot-size', 'value'),
                        Input('slider-dot-size', 'value'))


@app.callback(
    Output('slider-dot-size', 'disabled'),
    Input('toggle-dot-size', 'value'))
def disableDotSizeSlider(toggle_dot_auto):
    return toggle_dot_auto


if __name__ == "__main__":
    app.run_server(host='127.0.0.1', port='8050', debug=True)
