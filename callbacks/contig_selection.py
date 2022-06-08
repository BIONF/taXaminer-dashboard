"""
Callbacks related to contig selection
"""
from dash import Output, Input, callback_context


def import_callbacks(app):
    """
    Import callbacks
    :param app: Dash App
    :return: callbacks
    """
    @app.callback(
        Output("contig_info", "data"),
        Input("button_reset_contigs", "n_clicks"),
        Input("single_contig", "n_clicks"),
        Input("button_all_contigs", "n_clicks"),
        prevent_initial_call=True
    )
    def reset_contigs(reset, single_contig, all_contigs):
        """
        Update the info store. This cause a chained call of update_dataframe()
        :param single_contig:
        :param reset:
        :return:
        """
        changed_id = [p['prop_id'] for p in callback_context.triggered][0]

        # reset
        if changed_id == "button_reset_contigs.n_clicks":
            return {'reset': True, 'select_current': False}

        # select all
        elif changed_id == "button_all_contigs.n_clicks":
            return {'reset': False, 'select_current': False}

        # select only of the currently selected
        else:
            return {'reset': False, 'select_current': True}

