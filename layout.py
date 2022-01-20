import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table


class Layout:
    def get_layout(self, dropdowns, scatter_test, my_dataset):
        """
        Builds an returns a layout
        :param dropdowns: Dropdown options for dataset selection
        :param scatter_test: scatterplot
        :param my_dataset: initial dataset
        :return: dash.Layout component
        """

        layout = dbc.Container(fluid=True, children=[
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
                            className="plot"
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
                                                        id='summary',
                                                        value='Textarea',
                                                        disabled=True,
                                                        style={'height': 150, 'width': 'fill', "verticalAlign": "top",
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
                                                    html.Div([
                                                        dbc.Button(
                                                            "Find Best hit on NCBI",
                                                            id='NCBI',
                                                            href="https://www.ncbi.nlm.nih.gov/",
                                                            external_link=True,
                                                            color='primary',
                                                            target='_blank',
                                                        ),
                                                    ], className="d-grid gap-2")
                                                ], className="m-2"),
                                                dbc.Card([
                                                    dbc.CardHeader("Amino Acid Sequence"),
                                                    dcc.Textarea(
                                                        id='textarea-as',
                                                        value='Select a datapoint',
                                                        disabled=True,
                                                        style={'height': 200,
                                                               'width': 'fill', "verticalAlign": "top",
                                                               'horizontalAlign': 'left'},
                                                    ),
                                                ], className="m-2")
                                            ], align='center')
                                        ], align='end'),
                                        # display gene information
                                    ], className="m-2"),
                            dbc.Tab([
                                dbc.Card([
                                    dbc.CardHeader("Enable/Disable Filters"),
                                    dbc.Checkbox(label="Scatterplot legend",
                                                 className="m-1 form-switch"),
                                    dbc.Checkbox(label="e-value",
                                                 className="m-1 form-switch"),
                                    dbc.Checkbox(label="Ignore unassigned",
                                                 className="m-1 form-switch"),
                                    dbc.Checkbox(label="Ignore non-coding",
                                                 className="m-1 form-switch"),
                                    dbc.Checkbox(label="Filter by scaffolds",
                                                 className="m-1 form-switch"),
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
                                            dbc.CardHeader("Distribution "
                                                           "of Variables"),
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
                                    columns=[{"name": "Gene Name",
                                              "id": "g_name"},
                                             {"name": "Best Hit",
                                              "id": "best_hit"},
                                             {"name": "e-value",
                                              "id": "bh_evalue"}],
                                    data=my_dataset.get_data_original().to_dict('records'),
                                ),
                            ], className="m-2"),
                        ], label="Selected Data"),

                        dbc.Tab([
                            dbc.Card([
                                # table containing all assignments
                                dash_table.DataTable(
                                    id='table_all',
                                    columns=[{"name": "Gene Name",
                                              "id": "g_name"},
                                             {"name": "Best Hit",
                                              "id": "best_hit"},
                                             {"name": "e-value",
                                              "id": "bh_evalue"}],
                                    data=my_dataset.get_data_original().to_dict('records'),
                                    sort_action='native',
                                    sort_mode='multi',
                                ),
                            ], className="m-2"),
                        ], label="Full Dataset"),

                        dbc.Tab([
                            dbc.Card([
                                # button to add visible points to selection
                                dbc.Button("Click here to Add the contents of this table to the download selection", color="success",
                                           size="md",
                                           id="button_add_legend_to_select"),

                                # table containing only selected taxa
                                dash_table.DataTable(
                                    id='legend_selection',
                                    columns=[{"name": "Gene Name",
                                              "id": "g_name"},
                                             {"name": "Taxon",
                                              "id": "plot_label"},
                                             {"name": "e-value",
                                              "id": "bh_evalue"}],
                                    data=my_dataset.get_data_original().to_dict('records'),
                                    sort_action='native',
                                    sort_mode='multi',
                                ),
                            ], className="m-2"),
                        ], label="Taxa visible in plot"),
                    ]),
                ]),
                dbc.Col([
                    dbc.Tabs([
                        dbc.Tab([
                            dbc.Card([
                                dbc.CardHeader("Selection Options"),
                                html.Div([
                                    dbc.ButtonGroup(
                                        [dbc.Button("Add", color="success",
                                                    size="md",
                                                    id="button_add"),
                                         dbc.Button("Neutral",
                                                    color="secondary",
                                                    size="md",
                                                    id="button_neutral"),
                                         dbc.Button("Remove", color="danger",
                                                    size="md",
                                                    id="button_remove")],
                                        className="d-flex m-1 radio-group"
                                                  " btn-block"
                                    )
                                ]),
                                html.Div([
                                    dbc.Button("Reset entire Selection",
                                               id="button_reset",
                                               color="danger"),
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
                            html.Div([
                                dbc.Button(
                                    "Download selected amino acid sequences as .fasta",
                                    id='btn-download',
                                    color='primary',
                                    target='_blank',
                                ),
                            ], className="d-grid gap-2"),
                            dcc.Download(id="download-selection")
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

        # finally, return out layout
        return layout
