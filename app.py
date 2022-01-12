import os
import dash
import dash_bootstrap_components as dbc
import math
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import data_io as milts_files

import numpy as np
import sys
import yaml

# config_path = sys.argv[1]

# read parameters from config file
# config_obj = yaml.safe_load(open(config_path, 'r'))
# output_path=config_obj.get('output_path')# complete path to output directory

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
print("=== Begin File discovery === \n...")
for file in os.listdir(base_path):
    d = os.path.join(base_path, file)
    if os.path.isdir(d):
        datasets.append(d + "/")
        dropdowns.append({'label': d.split("/")[-1], 'value': d + "/"})
print("=== Finished File Discovery ===")

pca_data = pd.read_csv(datasets[0] + "PCA_and_clustering/PCA_results/pca_summary.csv")

# global dataframe
path = datasets[0]
data = pd.read_csv(datasets[0] + "taxonomic_assignment/gene_table_taxon_assignment.csv")

scatter_test = px.scatter_matrix(data, dimensions=['Dim.1', 'Dim.2', 'Dim.3'])

data_frames = {'base': data, 'selection': data}
selected_genes = []


# creating a dictionary of the legend. Values indicate the visibility
list_of_labels = data['plot_label'].tolist()
label_dictionary = dict.fromkeys(list_of_labels, True)
del label_dictionary['Unassigned']
legend_order = list(label_dictionary.keys())


# Init app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "MILTS"

app.layout = dbc.Container(fluid=True, children=[
    dbc.NavbarSimple(
        brand="MILTS",
        brand_href="#",
        color="primary",
        dark=True,
        fluid=True,
    ),
    dbc.Row(
        [
            # wide scatterplot
            dbc.Col(width=8, children=[
                dcc.Graph(
                    id="scatter3d",
                    config={"displayModeBar": True},
                    animate=True,
                    className="plot",
                )]),

            # tabbed side menu
            dbc.Col(width=4, children=[
                dbc.Tabs(children=[
                    dbc.Tab(label='Overview',
                            children=[
                                # Dataset Selection
                                html.Hr(),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Card([
                                            dbc.CardHeader("Select Dataset"),
                                            dcc.Dropdown(
                                                id='dataset_select',
                                                options=dropdowns,
                                                value=dropdowns[0].get('value')
                                            )
                                        ], className="m-2"),
                                        dbc.Card([
                                            dbc.CardHeader("Dataset Summary"),
                                            dcc.Textarea(
                                                id='textarea-info',
                                                value='Textarea',
                                                disabled=True,
                                                style={'height': 200, 'width': 'fill', "verticalAlign": "top",
                                                       'horizontalAlign': 'left'},
                                            ),
                                        ], className="m-2"),
                                        dbc.Card([
                                            dbc.CardHeader("Selected Gene"),
                                            dcc.Textarea(
                                                id='textarea-taxon',
                                                value='Textarea content initialized\nwith multiple lines of text',
                                                disabled=True,
                                                style={'height': 200, 'width': 'fill', "verticalAlign": "top",
                                                       'horizontalAlign': 'left'},
                                            ),
                                        ], className="m-2"),
                                    ], align='center')
                                ], align='end'),
                                # display gene information
                            ], className="m-2"),
                    dbc.Tab([
                        dbc.Card([
                            dbc.CardHeader("Enable/Disable Filters"),
                            dbc.Checkbox(label="Scatterplot legend", className="m-1 form-switch"),
                            dbc.Checkbox(label="e-value", className="m-1 form-switch"),
                            dbc.Checkbox(label="Ignore unassigned", className="m-1 form-switch"),
                            dbc.Checkbox(label="Ignore non-coding", className="m-1 form-switch"),
                            dbc.Checkbox(label="Filter by scaffolds", className="m-1 form-switch"),
                        ], className="m-2"),
                        dbc.Card([
                            dbc.CardHeader("e-value Filter"),
                            dcc.Slider(
                                id='evalue-slider',
                                min=0,
                                max=300,
                                value=0,
                                step=10,
                                marks={0: {'label': 'e^0', 'style': {'color': '#77b0b1'}},
                                       100: {'label': 'e^-100', 'style': {'color': '#77b0b1'}},
                                       200: {'label': 'e^-200', 'style': {'color': '#77b0b1'}},
                                       300: {'label': 'e^-300', 'style': {'color': '#77b0b1'}}},
                                className="m-2",
                            ),
                        ], className="m-2"),
                    ], label="Filter", className="m-2"),
                    dbc.Tab(label='Metrics', children=[
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader("Distribution of Variables"),
                                    dcc.Graph()
                                ])
                            ])
                        ]),
                    ]),
                    # scatter matrix
                    dbc.Tab(label='Scatter Matrix', children=[
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(id='scatter_matrix',
                                          figure=scatter_test,
                                          responsive=True),
                            ])
                        ]),
                    ]),
                ]),
            ]),
        ]
    ),
    html.Hr(),
    dbc.NavbarSimple(
        brand="Data Selection",
        brand_href="#",
        color="primary",
        dark=True,
        fluid=True,
    ),
    dbc.Row([
        dbc.Col(width=8, children=[
            dbc.Tabs([
                dbc.Tab([
                    dbc.Card([
                        # table containing only selected assignments
                        dash_table.DataTable(
                            id='table_selection',
                            columns=[{"name": "Gene Name", "id": "g_name"},
                                     {"name": "Best Hit", "id": "best_hit"},
                                     {"name": "e-value", "id": "bh_evalue"}],
                            data=data.to_dict('records'),
                            sort_action='native',
                            sort_mode='multi',
                        ),
                    ], className="m-2"),
                ], label="Selected Data"),

                dbc.Tab([
                    dbc.Card([
                        # table containing all assignments
                        dash_table.DataTable(
                            id='table_all',
                            columns=[{"name": "Gene Name", "id": "g_name"},
                                     {"name": "Best Hit", "id": "best_hit"},
                                     {"name": "e-value", "id": "bh_evalue"}],
                            data=data.to_dict('records'),
                            sort_action='native',
                            sort_mode='multi',
                        ),
                    ], className="m-2"),
                ], label="Full Dataset"),

                dbc.Tab([
                    dbc.Card([
                        # table containing only selected taxa
                        dash_table.DataTable(
                            id='legend_selection',
                            columns=[{"name": "Gene Name", "id": "g_name"},
                                     {"name": "Taxon", "id": "plot_label"},
                                     {"name": "e-value", "id": "bh_evalue"}],
                            data=data.to_dict('records'),
                            sort_action='native',
                            sort_mode='multi',
                        ),
                    ], className="m-2"),
                ], label="Selected Taxa"),
            ]),
        ]),
        dbc.Col([
            dbc.Tabs([
                dbc.Tab([
                    dbc.Card([
                        dbc.CardHeader("Selection Options"),
                        html.Div([
                            dbc.ButtonGroup(
                                [dbc.Button("Add", color="success", size="md"),
                                 dbc.Button("Neutral", color="secondary", size="md"),
                                 dbc.Button("Remove", color="danger", size="md")],
                                className="d-flex m-1 radio-group btn-block"
                            )
                        ]),
                        html.Div([
                            dbc.Button("Reset entire Selection", color="danger"),
                        ], className="d-grid gap-2 m-1"),
                    ], className="m-2"),
                    dbc.Card([
                        dbc.CardHeader("Search by name"),
                        dbc.Input(
                            id='searchbar',
                            placeholder="Enter Gene Name",
                            invalid=True
                        ),
                    ], className="m-2"),
                ], label="Options", className="m-2"),
                # Download Tab
                dbc.Tab([
                    dbc.Card([
                        dbc.CardHeader("Amino Acid sequence"),
                        dcc.Textarea(
                            id='textarea-sequence',
                            value='Textarea',
                            disabled=True,
                            style={'height': 300},
                        ),
                    ], className="m-2"),
                ], label="Download"),
                dbc.Tab([
                    dbc.Card([
                        dbc.CardHeader("BLAST"),
                    ], className="m-2"),
                ], label="Tools")
            ]),
        ], width=4)
    ]),
])


# Hover event
@app.callback(
    Output('textarea-taxon', 'value'),
    Input('scatter3d', 'clickData'),
    Input('searchbar', 'value'))
def print_hover_data(click_data, search_data):
    """
    Update Basic Information
    :param click_data:
    :param search_data:
    :return:
    """
    if not click_data:
        return "Click a data point to select it"

    # Allow user search
    if search_data:
        my_point = search_data
    else:
        my_point = click_data['points'][0]['customdata'][0]

    # filter data frame
    global selected_genes
    selected_genes.append(my_point)

    gene_data = data.loc[data['g_name'] == my_point]

    output_text = ""
    if gene_data.size != 0:
        output_text += "Label: " + gene_data['plot_label'].item() + "\n"
        output_text += "Gene: " + gene_data['g_name'].item() + " | Scaffold: " + gene_data['c_name'].item() + "\n"
        output_text += "Best hit: " + str(gene_data['best_hit'].item()) + " | e-value: " \
                       + str(gene_data['bh_evalue'].item())
    else:
        output_text = "No matching genes found"
    return str(output_text)


@app.callback(
    Output('textarea-sequence', 'value'),
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
        my_dot = hover_data['points'][0]['customdata'][0]
    global path
    seq = milts_files.get_protein_record(my_dot, path)
    if not seq:
        return "No matching Sequence data"
    else:
        return str(seq.seq)


@app.callback(
    Output('scatter3d', 'figure'),
    Output('scatter_matrix', 'figure'),
    Output('table_selection', 'data'),
    Output('table_all', 'data'),
    Input('evalue-slider', 'value'),
    Input('dataset_select', 'value'),
)
def update_dataframe(value, new_path):
    """
    Update dataset and apply filters
    :param value:
    :param new_path:
    :return:
    """
    global data
    global path
    path = new_path
    data = pd.read_csv(new_path + "taxonomic_assignment/gene_table_taxon_assignment.csv")
    value = 1 * math.e ** (-value)
    my_data = data[data.bh_evalue < value]
    my_fig = px.scatter_3d(my_data, x='Dim.1', y='Dim.2', z='Dim.3', color='plot_label', hover_data=['g_name'])
    my_fig.update_traces(marker=dict(size=3), hovertemplate="<br>".join([
        "%{customdata[0]}"
    ]))

    my_fig.update_layout(legend={'itemsizing': 'constant'},
                         legend_title_text='Taxa')

    scatter_side = px.scatter_matrix(my_data,
                                     dimensions=['Dim.1', 'Dim.2', 'Dim.3'],
                                     custom_data=['g_name'])
    # TODO: Sepparate Selection and "all" data for tables
    return my_fig, scatter_side, data.to_dict('records'), data.to_dict('records')


@app.callback(
    Output('legend_selection', 'data'),
    Input('scatter3d', 'restyleData'))
def display_click_data(selectedData):
    # removing error at the start of the program
    if selectedData is None:
        return data.to_dict('records')

    # updting the legend dictionary with the input
    update_dict = dict(zip(selectedData[1], selectedData[0]["visible"]))
    for i in update_dict:
        if update_dict[i] == "legendonly":
            label_dictionary[legend_order[i]] = False
        else:
            label_dictionary[legend_order[i]] = True

    # assembling output
    new_data = data.copy(deep=True)
    new_data = new_data[new_data['plot_label'] != 'Unassigned']
    for i in label_dictionary:
        if label_dictionary[i] == False:
            new_data = new_data[new_data['plot_label'] != i ]


    return new_data.to_dict('records')


if __name__ == "__main__":
    app.run_server(host='127.0.0.1', port='8050', debug=True)
