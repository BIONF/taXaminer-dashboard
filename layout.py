import json
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dash_table.Format import Format, Scheme


class Layout:
    def get_layout(self, dropdowns):
        """
        Builds an returns a layout
        :param dropdowns: Dropdown options for dataset selection
        :param scatter_test: scatterplot
        :return: dash.Layout component
        """

        # initial table variables
        variable_items = []

        # variable selection diamond data
        taxonomic_hits_vars = []
        taxonomic_cols_initial = []
        taxonomic_hits_names = ['sscinames', 'bitscore', 'evalue', 'pident',
                                'length', 'mismatch', 'gapopen', 'qstart',
                                'qend', 'sstart', 'send', 'staxids']

        # table index for diamond hits
        for col in taxonomic_hits_names:
            # one exception
            if col == "sscinames":
                label = "hit taxon"
            else:
                label = col
            taxonomic_hits_vars.append({"label": col, "value": col})
            taxonomic_cols_initial.append({"name": label, "id": col})

        # colorscales
        try:
            with open("./static/colorscale.json") as c:
                colorscales = dict(json.load(c))
        except FileNotFoundError:
            colorscales = None

        if not colorscales or not colorscales['data'] or len(
                colorscales['data']) == 0:
            colorscales = {"data": [{
                "label": "Rainbow",
                "value": "#DF0101 #FFFF00 #298A08 #00FF00 #01DFD7 #0101DF #F781BE"
            }]}

        layout = dbc.Container(fluid=True, children=[
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Welcome to taXaminer"), close_button=True),
                    dbc.ModalBody(children=[
                        dbc.Card(children=[
                            dbc.CardHeader(id="mod1-head-select",
                                           children="Select a taXaminer dataset from list."),
                            dcc.Dropdown(
                                id='dataset_startup_select',
                                options=dropdowns,
                                placeholder="No dataset selected",
                                clearable=False
                            )
                        ]),

                        dbc.Tooltip(
                            "All records that are stored in default data location (./data) should be available.",
                            target="mod1-head-select",
                            placement="right"),

                    ], className="d-grid gap-4")
                ],
                id="mod1",
                centered=True,
                is_open=True,
            ),
            dbc.NavbarSimple(
                brand="taXaminer",
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
                                                    dbc.CardHeader(
                                                        "Select Dataset"),
                                                    dcc.Dropdown(
                                                        id='dataset_select',
                                                        options=dropdowns,
                                                        placeholder="No Dataset selected"
                                                    )
                                                ], className="m-2"),
                                                dbc.Card([
                                                    dbc.CardHeader(
                                                        "Dataset Summary"),
                                                    dcc.Textarea(
                                                        id='summary',
                                                        value='Textarea',
                                                        disabled=True,
                                                        style={'height': 150,
                                                               'width': 'fill',
                                                               "verticalAlign": "top",
                                                               'horizontalAlign': 'left'},
                                                    ),
                                                ], className="m-2"),
                                                dbc.Card([
                                                    dbc.CardHeader(
                                                        "Selected Gene"),
                                                    dcc.Textarea(
                                                        id='textarea-taxon',
                                                        value='Textarea content initialized\nwith multiple lines of text',
                                                        disabled=True,
                                                        style={'height': 200,
                                                               'width': 'fill',
                                                               "verticalAlign": "top",
                                                               'horizontalAlign': 'left'},
                                                    ),
                                                    html.Div([
                                                        dbc.Button(
                                                            "Find Taxonomy on NCBI",
                                                            id='NCBI',
                                                            href="https://www.ncbi.nlm.nih.gov/",
                                                            external_link=True,
                                                            color='primary',
                                                            target='_blank',
                                                        ),
                                                    ],
                                                        className="d-grid gap-2")
                                                ], className="m-2"),
                                                dbc.Card([
                                                    dbc.CardHeader(
                                                        "Amino Acid Sequence"),
                                                    dcc.Textarea(
                                                        id='textarea-as',
                                                        value='Select a datapoint',
                                                        disabled=True,
                                                        style={'height': 200,
                                                               'width': 'fill',
                                                               "verticalAlign": "top",
                                                               'horizontalAlign': 'left'},
                                                    ),
                                                ], className="m-2")
                                            ], align='center')
                                        ], align='end'),
                                        # display gene information
                                    ], className="m-2"),
                            dbc.Tab([
                                dbc.Card([
                                    # diamond
                                    dbc.CardHeader("Diamond Output"),
                                    dcc.Dropdown(
                                        options=taxonomic_hits_vars,
                                        multi=True,
                                        id='variable-selection-diamond',
                                        value=taxonomic_hits_names,
                                        className="m-2"
                                    ),
                                    html.Div([
                                        dash_table.DataTable(id='table-hits',
                                                             page_size=20,
                                                             style_header={
                                                                 'textAlign': 'left'},
                                                             style_table={
                                                                 'overflowX': 'auto',
                                                                 'height': 'auto'},
                                                             style_cell={
                                                                 'textAlign': 'left'},
                                                             sort_action='native',
                                                             sort_mode='multi',
                                                             columns=taxonomic_cols_initial, )
                                    ], className="m-2")
                                ], className="m-2"),
                            ], label="Diamond Output"),
                            dbc.Tab([
                                dbc.Card([
                                    dbc.CardHeader("e-value Filter"),
                                    dcc.Slider(
                                        id='evalue-slider',
                                        min=0,
                                        max=300,
                                        value=0,
                                        step=10,
                                        marks={0: {'label': 'e^0', 'style': {
                                            'color': '#77b0b1'}},
                                               100: {'label': 'e^-100',
                                                     'style': {
                                                         'color': '#77b0b1'}},
                                               200: {'label': 'e^-200',
                                                     'style': {
                                                         'color': '#77b0b1'}},
                                               300: {'label': 'e^-300',
                                                     'style': {
                                                         'color': '#77b0b1'}}},
                                        className="m-2",
                                    ),
                                ], className="m-2"),
                            ], label="Filter", className="m-2"),
                            dbc.Tab(label='PCA Data', children=[
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Card([
                                            dbc.CardHeader("PCA Data"),
                                            dcc.Graph(
                                                id="contribution",
                                            ),
                                            # info of varibale
                                            dbc.CardHeader(
                                                "Description of variables"),
                                            dcc.Textarea(
                                                id='variable-info',
                                                value='Hover over a Variable to get a short description',
                                                disabled=True,
                                                style={'height': 50,
                                                       'width': 'fill',
                                                       "verticalAlign": "top",
                                                       'horizontalAlign': 'left'},
                                            ),
                                            dcc.Graph(
                                                id="scree",
                                            )
                                        ])
                                    ])
                                ]),
                            ]),
                            # scatter matrix
                            dbc.Tab(label='Scatter Matrix', children=[
                                dbc.Row([
                                    dbc.Col([
                                        dcc.Graph(id='scatter_matrix',
                                                  responsive=True),

                                    ])
                                ]),
                            ]),
                        ]),
                    ]),
                ]
            ),
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        # Dot size selection
                        dbc.Col(children=[
                            html.Span("Dot size (px)"),
                            dcc.Slider(id='slider-dot-size',
                                       min=1,
                                       max=8,
                                       step=1,
                                       value=3
                                       )
                        ]),
                        # colorscale selection
                        dbc.Col([
                            html.Span("Colorscale"),
                            dcc.Dropdown(
                                id='colorscale-select',
                                clearable=False,
                                options=colorscales['data'],
                                value=colorscales['data'][0]['value']
                            )
                        ]),
                    ]),
                ], width=8),
            ]),
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
                                dbc.ButtonGroup([
                                    # sync button
                                    dbc.Button(
                                        html.Span(
                                            ["",
                                             html.I(
                                                 className="fas fa-arrow-down"),
                                             html.Span(
                                                 " Sync table with graph "),
                                             html.I(
                                                 className="fas fa-arrow-down")
                                             ]),
                                        color="primary",
                                        size="md",
                                        id="btn-sync"),
                                    # button to add table contents to selection
                                    dbc.Button([
                                        html.Span(["", html.I(
                                            className="fas fa-plus-circle"),
                                                   html.Span(
                                                       " Add table to selection")])],
                                        color="success",
                                        id="button_add_legend_to_select",
                                    ),
                                    dbc.Button(
                                        html.Span(
                                            ["",
                                             html.I(
                                                 className="fas fa-minus-circle"),
                                             html.Span(
                                                 " Reset Legend "),
                                             html.I(
                                                 className="fas fa-minus-circle")
                                             ]),
                                        color="danger",
                                        size="md",
                                        id="reset-legend"),
                                ]),
                            ]),
                            dbc.Card([
                                # table containing only selected taxa
                                dash_table.DataTable(
                                    id='legend_selection',
                                    columns=[{"name": "Gene Name",
                                              "id": "g_name"},
                                             {"name": "Taxon",
                                              "id": "plot_label"},
                                             {"name": "e-value",
                                              "id": "bh_evalue",
                                              "type": "numeric",
                                              "format": Format(precision=3,
                                                               scheme=Scheme.decimal_or_exponent)}],
                                    page_size=30,
                                    style_header={'textAlign': 'left'},
                                    style_table={
                                        'overflowX': 'auto',
                                        'height': 'auto'},
                                    style_cell={'textAlign': 'left'},
                                    sort_action='native',
                                    sort_mode='multi',
                                ),
                            ], className="m-2"),
                        ], label="Plot Table"),

                        dbc.Tab([
                            dbc.Row([
                                dbc.Col([
                                    dbc.ButtonGroup([
                                        dbc.Button(
                                            html.Span(["", html.I(
                                                className="fas fa-plus-circle")]),
                                            color="success",
                                            size="md",
                                            id="button_add"),
                                        dbc.Button(
                                            html.Span(["", html.I(
                                                className="fas fa-pause-circle")]),
                                            color="secondary",
                                            size="md",
                                            id="button_neutral"
                                        ),
                                        dbc.Button(
                                            html.Span(["", html.I(
                                                className="fas fa-minus-circle")]),
                                            color="danger",
                                            size="md",
                                            id="button_remove"
                                        )],
                                        className="d-flex m-2 radio-group"
                                                  " btn-block"
                                    ),
                                ], width=3),
                                dbc.Col([
                                    dbc.Row([
                                        dbc.ButtonGroup([
                                            dbc.Button([
                                                html.Span(
                                                    ["", html.I(
                                                        className="fas fa-upload"),
                                                     html.Span(
                                                         " Load")])],
                                                color="primary",
                                                id='btn-reload',
                                                n_clicks=0
                                            ),

                                            dbc.Button([
                                                html.Span(["", html.I(
                                                    className="fas fa-trash"),
                                                           html.Span(
                                                               " Reset")])],
                                                color="danger",
                                                id="button_reset"
                                            ),

                                        ], className="d-flex m-2 radio-group"
                                                     " btn-block"),

                                    ]),
                                ]),
                                dbc.Col([
                                    dbc.ButtonGroup([
                                        dbc.Button([
                                            html.Span(
                                                ["", html.I(
                                                    className="fas fa-download"),
                                                 html.Span(" .fasta")])],
                                            color="primary",
                                            outline=True,
                                            id='btn-download'
                                        ),
                                        dbc.Button([
                                            html.Span(
                                                ["", html.I(
                                                    className="fas fa-download"),
                                                 html.Span(
                                                     " .csv")])],
                                            color="primary",
                                            outline=True,
                                            id='btn-csv'
                                        ),
                                    ], className="d-flex m-2 radio-group"
                                                 " btn-block"),
                                    # download
                                    dcc.Download(id="download-selection"),
                                    dcc.Download(id="download-csv"),
                                ]),
                                dbc.Col([
                                    dbc.Row([
                                        dbc.Input(
                                            id='searchbar',
                                            placeholder="Enter Gene Name",
                                            invalid=True,
                                            className="d-flex m-2 radio-group"
                                        ),
                                    ])
                                ], width=2),
                                # table containing only selected assignments
                                dash_table.DataTable(
                                    id='table_selection',
                                    columns=[{"name": "Gene Name",
                                              "id": "g_name"},
                                             {"name": "Best Hit",
                                              "id": "best_hit"},
                                             {"name": "e-value",
                                              "id": "bh_evalue",
                                              "type": "numeric",
                                              "format": Format(precision=3,
                                                               scheme=Scheme.decimal_or_exponent)}],
                                    style_header={'textAlign': 'left'},
                                    style_table={
                                        'overflowX': 'auto',
                                        'height': 'auto'},
                                    style_cell={'textAlign': 'left'},
                                    page_size=30,
                                ),
                            ], className="d-flex m-2"),
                        ], label="Selection Table and Tools"),

                    ], id="table-tabs"),
                ]),
                dbc.Col([
                    dbc.Tabs([
                        dbc.Tab([
                            dbc.Label("Select variables visible in tables:"),
                            dcc.Dropdown(
                                options=variable_items,
                                multi=True,
                                id='variable-selection',
                                # these are the initially displayed variables
                                value=['g_name', 'plot_label', 'bh_evalue']
                            ),
                        ], label="Variables"),
                        # External Tools Tab
                        dbc.Tab([
                            dbc.Card([
                                dbc.CardHeader("External tools"),
                                dbc.CardBody([
                                    dbc.Button(
                                        "NCBI Blast",
                                        href="https://blast.ncbi.nlm.nih.gov/Blast.cgi?PROGRAM=blastp",
                                        external_link=True,
                                        color='primary',
                                        target='_blank',
                                        className='m-2'
                                    ),
                                    dbc.Button(
                                        "HMMER",
                                        href="https://www.ebi.ac.uk/Tools/hmmer/",
                                        external_link=True,
                                        color='primary',
                                        target='_blank',
                                        className='m-2'
                                    ),
                                    dbc.Button(
                                        "CD-Search",
                                        href="https://www.ncbi.nlm.nih.gov/Structure/cdd/wrpsb.cgi",
                                        external_link=True,
                                        color='primary',
                                        target='_blank',
                                        className='m-2'
                                    ),
                                ])
                            ], className="m-2"),
                        ], label="Tools")
                    ]),
                ], width=4)
            ]),
        ])

        # finally, return out layout
        return layout
