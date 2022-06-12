"""This file contains clientside callbacks"""

from dash import Output, Input, State


def import_callbacks(app):
    """
    Import callbacks
    :param app: Dash App
    :return: callbacks
    """
    app.clientside_callback("""
        // Setting the manual point size
        // :param toggle_dot_auto:  dot size mode switch bool
        // :param dot_size: new dot size value form slider
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

    app.clientside_callback("""
        // Setting the automatic point size 
        // :param fig scatter3d figure
        // :param restyle scatter3d restyleData 
        // :param toggle_dot_auto:  dot size mode switch bool
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
        function(lay, fig){
            // Fix a sync camera issues between plotly an python dash. 
            // :param lay is from dash plot relayoutData
            // :param fig scatter3d figure

            var main_scat = document.getElementById('scatter3d')
            if(fig !== undefined && fig['layout'] !== undefined && main_scat !== undefined && main_scat.children[1]._fullLayout !== undefined){            
                fig['layout']['scene']['camera'] = main_scat.children[1]._fullLayout['scene']['camera']
            }
            return "";
        }
        """,
                            Output('dummy-2', 'children'),
                            Input('scatter3d', 'relayoutData'),
                            State('scatter3d', 'figure'))

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

