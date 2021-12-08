import time
import dash
import dash_bootstrap_components as dbc
import math
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
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

output_path = "./data/"

pca_data = pd.read_csv(output_path + "PCA_and_clustering/PCA_results/pca_summary.csv")

# prep data
pca_resolution = 5
proportion_of_variance = []
pca_ids = []
for i in range(1, pca_resolution + 1):
    curr_value = pca_data.get("PC" + str(i))
    pca_ids.append("PC" + str(i))
    proportion_of_variance.append(curr_value[1])

# Compile dataframe and graph
pca_data = pd.DataFrame(proportion_of_variance, pca_ids)
pca_fig = px.bar(pca_data, width=300)
pca_fig.update_layout(showlegend=False)

# reading data and creating preliminary python version of 3D plot
data = pd.read_csv(output_path + "taxonomic_assignment/gene_table_taxon_assignment.csv")
fig = px.scatter_3d(data, x='Dim.1', y='Dim.2', z='Dim.3', labels={},
                    color='plot_label', hover_data=['g_name'])
fig.update_traces(marker=dict(size=3))

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "MILTS"

app.layout = dbc.Container(fluid=True, children=[
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Page 1", href="#")),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("More pages", header=True),
                    dbc.DropdownMenuItem("Page 2", href="#"),
                    dbc.DropdownMenuItem("Page 3", href="#"),
                ],
                nav=True,
                in_navbar=True,
                label="More",
            ),
        ],
        brand="NavbarSimple",
        brand_href="#",
        color="primary",
        dark=True,
        fluid=True,
    ),
    dbc.Row(
        [
            dbc.Col(width=9, children=[
                dcc.Graph(
                    id="scatter3d",
                    config={"displayModeBar": True},
                    animate=True,
                    figure=fig,
                    className="plot",
                )]),
            dbc.Col(children=[
                dbc.Tabs(children=[
                    dbc.Tab(label='Overview',
                            children=[
                                dbc.Row([
                                    html.H5(children="General Information"),
                                    dcc.Textarea(
                                        id='textarea-taxon',
                                        value='Textarea content initialized\nwith multiple lines of text',
                                        disabled=True,
                                        style={'height': 200, 'width': 'fill', "verticalAlign": "top",
                                               'horizontalAlign': 'left',
                                               'marginLeft': '11px'},
                                    ),
                                ]),
                                dbc.Row([
                                    dbc.Col([
                                        html.H5("Sequence Data"),
                                        html.Div(
                                            [
                                                dbc.Button(
                                                    "View Raw Sequence",
                                                    id="collapse-button",
                                                    color="primary",
                                                    n_clicks=0,
                                                    className="d-grid col-12 mb-3",
                                                ),
                                                dbc.Collapse(
                                                    dbc.Card(
                                                        dbc.CardBody([
                                                            dcc.Textarea(
                                                                id='textarea-sequence',
                                                                value='Textarea content initialized\nwith multiple lines of text',
                                                                disabled=True,
                                                                style={'width': '100%', 'height': 300,
                                                                       "verticalAlign": "top",
                                                                       'horizontalAlign': 'center'},
                                                            ),
                                                        ])),
                                                    id="collapse",
                                                    is_open=False,
                                                ),
                                            ]
                                        ),
                                    ]),
                                ], align='center'),
                            ]),
                    dbc.Tab(label='Filter',
                            children=[
                                dbc.Row([
                                    dbc.Col(align='end', children=[
                                        html.H4("Search gene identifier"),

                                        dbc.Col(
                                            dbc.Input(id='searchbar',
                                                      placeholder="Enter Gene Name",
                                                      invalid=True),
                                            className="mb-3",
                                        ),
                                        dbc.Col(dbc.Button("Submit", color="primary", id='clear-search'),
                                                width="auto", className='mb-3'),
                                    ]),
                                ]),
                                html.H5(children="Filter by e-value",
                                        style={"text-align": "center"}),
                                dbc.Row([
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
                                    ),
                                ]),
                            ]),
                    dbc.Tab(label='Metrics', children=[
                        html.Div([
                            dcc.Graph(figure=pca_fig)
                        ], style={'display': 'inline-block', 'width': '70%', 'horizontalAlign': 'center'})
                    ]),
                ]),
            ]),
        ]
    ),
])


# Hover event
@app.callback(
    Output('textarea-taxon', 'value'),
    Input('scatter3d', 'hoverData'),
    Input('searchbar', 'value'))
def print_hover_data(hover_data, search_data):
    if not hover_data:
        return "Hover of a data point to select it"

    # Allow user search
    if search_data:
        my_point = search_data
    else:
        my_point = hover_data['points'][0]['customdata'][0]

    # filter data frame
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
    Input('scatter3d', 'hoverData'),
    Input('searchbar', 'value'))
def print_seq_data(hover_data, search_data):
    if not hover_data:
        return "Hover of a data point to select it"
        # Allow user search
    if search_data:
        my_dot = search_data
    else:
        my_dot = hover_data['points'][0]['customdata'][0]
    seq = milts_files.get_protein_record(my_dot)
    if not seq:
        return "No matching Sequence data"
    else:
        return str(seq.seq)


@app.callback(
    Output('scatter3d', 'figure'),
    Input('evalue-slider', 'value'))
def update_dataframe(value):
    value = 1 * math.e ** (-value)
    my_data = data[data.bh_evalue < value]
    print(value)
    my_fig = px.scatter_3d(my_data, x='Dim.1', y='Dim.2', z='Dim.3', color='plot_label', hover_data=['g_name'])
    my_fig.update_traces(marker=dict(size=3))
    return my_fig


@app.callback(
    Output('searchbar', 'value'),
    Input('clear-search', 'n_clicks'))
def reset_searchbar(n_clicks):
    return None


@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


if __name__ == "__main__":
    app.run_server(host='127.0.0.1', port='8050', debug=True)
