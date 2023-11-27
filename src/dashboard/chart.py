import os
import dash
import numpy as np
import plotly.graph_objs as go
import plotly.express as px


from dotenv import load_dotenv
from dash import dcc, ctx
from dash import html
from dash import dash_table
from omegaconf import OmegaConf

# from dashboard.assets import metr_la_network
from dashboard.utils.data_loader import load_dataframes, get_plotly_figure

load_dotenv()
# External recources
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
mapbox_access_token = os.getenv("mapbox_access_token")

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Read sample data
np.random.seed(1)
# df = metr_la_network
# df.rename(columns={i: str(i) for i in range(207)}, inplace=True)
# Get categories of sampel data set
config = OmegaConf.load("conf/production.yml")
df = load_dataframes(window=config.init_window)



# Layout definition for bar chart
layout_bar = go.Layout(
    xaxis=dict(tickangle=-45),
    yaxis=dict(fixedrange=True),
    barmode='stack',
    showlegend=False,
    margin={'r': 5,
            't': 20,
            'b': 80,
            'l': 40,
            'pad': 0},
)

# Layout definition for map
layout_map = go.Layout(
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=dict(
            lat=52,
            lon=10
        ),
        pitch=0,
        zoom=6
    ),
    showlegend=False,
    margin={'r': 20,
            't': 20,
            'b': 5,
            'l': 5,
            'pad': 0},
)

# Define dashboard layout
app.layout = html.Div(children=[
    html.H1(children='Dashboard Spatio-Temporal Data'),
    dash_table.DataTable(
        id='table',
        columns=[
            {'name': col, 'id': col} for col in df.columns
        ],
        data=df.to_dict('records'),
        page_size=10,
        style_table={"overflow-x": "auto"},
    ),
    dcc.Graph(figure=get_plotly_figure(df)),
    html.Div(
            # Map

                [
                    dcc.Graph(
                        id='point-map',
                        config={
                            'scrollZoom': True,
                            'showTips': True
                        },
                        figure=px.scatter_mapbox(
                            df, lon="lat", lat="lang", color="count", color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=4, mapbox_style="carto-positron"
                        ).update_layout(
                            hovermode='closest',
                            mapbox=dict(
                                accesstoken=mapbox_access_token,
                                bearing=0,
                                center=go.layout.mapbox.Center(
                                    lon=df["lat"].mean(),
                                    lat=df["lang"].mean()
                                ),
                                pitch=0,
                                zoom=10
                            )
                        ),style=layout_map)
        ],
                style={'width': '100%'}
    ),
    # html.Div(
    #     [
    #         html.Div(
    #             [
    #                 html.Div(children="Select categories:"),
    #                 dcc.Dropdown(
    #                     id='dropdown',
    #                     options=list(range(207)),
    #                     value=['ALL'],
    #                     clearable=False,
    #                     multi=True
    #                 ),
    #             ],
    #             className='three columns',
    #             style={'width': '30%'}
    #         ),
    #         html.Div(
    #             [
    #                 html.Div(children="Enter temporal aggregation window (eg 3H/1D/2W/3M/...):"),
    #                 dcc.Input(
    #                     id='aggregation',
    #                     placeholder='Enter a value...',
    #                     type='text',
    #                     value='1M'
    #                 ),
    #             ],
    #             className='three columns',
    #             style={'width': '30%'}
    #         ),
    #         html.Div(
    #             [
    #                 html.Div(children="Enter Node Id (eg,. 1, 2,3,4, ...). -1 means All nodes"),
    #                 dcc.Input(
    #                     id='node_id',
    #                     placeholder='Enter a value...',
    #                     type='number',
    #                     value='-1'
    #                 ),
    #             ],
    #             className='three columns',
    #             style={'width': '30%'}
    #         ),
    #     ],
    #     className='row'
    # ),
    # html.Hr(),
    # html.Div(
    #     [
    #         html.Div(
    #             [
    #                 # Timeserie                
    #                 dcc.Graph(id='timeseries', figure={
    #                         'data': [go.Scatter(x=df.index, y=df["0"], mode='lines',)],
    #                         "layout": layout_time_series
    #                     }),
    #                 dcc.DatePickerRange(
    #                     id='date-picker',
    #                     min_date_allowed=df.index.min().date(),
    #                     max_date_allowed=df.index.max().date(),
    #                     initial_visible_month=df.index.min().date(),
    #                     start_date=df.index.min().date(),
    #                     end_date=df.index.max().date(),
    #                     clearable=True,
    #                 ),
    #                 html.Div(id='text_output_range'),
    #             ],
    #             className='two columns',
    #             style={'width': '48%'}
    #         ),
    #         html.Div(
    #         # Map

    #             [
    #                 dcc.Graph(
    #                     id='point-map',
    #                     style={'height': 580},
    #                     config={
    #                         'displayModeBar': False,
    #                     },
    #                 ),
    #             ],
    #             className='two columns',
    #             style={'width': '48%'}
    #         ),
    #     ],
    #     className='row'
    # ),
    # html.Div(
    #     # Graph node/edge
    #     cyto.Cytoscape(
    #         id='cytoscape',
    #         elements=metr_la_network,
    #         layout={"name": "grid"},
    #         style={"height": "95vh", "width": "100%"},
    #     )
    # ),
    # html.Div(
    #         # Graph Actions
    #         className="four columns",
    #         children=[
    #             dcc.Tabs(
    #                 id="tabs",
    #                 children=[
    #                     dcc.Tab(
    #                         label="Actions",
    #                         children=[
    #                             html.Button("Remove Selected Node", id="remove-button"),
    #                             html.Button("Select Nodes", id="select-button"),
    #                             html.Button("Reset", id="reset-button"),
    #                         ],
    #                     ),
    #                     dcc.Tab(
    #                         label="Tap Data",
    #                         children=[
    #                             html.Div(
    #                                 style=styles["tab"],
    #                                 children=[
    #                                     html.P("Node Data JSON:"),
    #                                     html.Pre(
    #                                         id="tap-node-data-json-output",
    #                                         style=styles["json-output"],
    #                                     ),
    #                                     html.P("Edge Data JSON:"),
    #                                     html.Pre(
    #                                         id="tap-edge-data-json-output",
    #                                         style=styles["json-output"],
    #                                     ),
    #                                 ],
    #                             )
    #                         ],
    #                     ),
    #                     dcc.Tab(
    #                         label="Selected Data",
    #                         children=[
    #                             html.Div(
    #                                 style=styles["tab"],
    #                                 children=[
    #                                     html.P("Node Data JSON:"),
    #                                     html.Pre(
    #                                         id="selected-node-data-json-output",
    #                                         style=styles["json-output"],
    #                                     ),
    #                                     html.P("Edge Data JSON:"),
    #                                     html.Pre(
    #                                         id="selected-edge-data-json-output",
    #                                         style=styles["json-output"],
    #                                     ),
    #                                 ],
    #                             )
    #                         ],
    #                     ),
    #                 ],
    #             ),
    #         ],
    # ),
])





# @app.callback(
#     dash.dependencies.Output('text_output_range', 'children'),
#     [dash.dependencies.Input('date-picker', 'start_date'), dash.dependencies.Input('date-picker', 'end_date')])
# def update_output_text(start_date, end_date):
#     """
#     Print selected time range
#     """
#     res = 'Selected range: {} - {}'.format(start_date, end_date)
#     return res


# @app.callback(
#     dash.dependencies.Output('point-map', 'figure'))
# def update_map_figure():
#     """
#     Provide data to map
#     """

#     # Select given time range and category
#     df_filtered = df

#     data = []
#     data.append(
#         go.Scattermapbox(
#             lon=df_filtered['lon'],
#             lat=df_filtered['lat'],
#             mode='markers',
#             marker=dict(
#                 size=8,
#                 # color='rgb(255, 0, 0)',
#                 color="rgba(255, 0, 0, 0.5)",
#                 opacity=0.7
#             ),
#             name='node',
#             hoverinfo='name'
#         )
#     )

#     return {
#         'data': data,
#         'layout': layout_map
#     }

# @app.callback(
#     dash.dependencies.Output("cytoscape", "elements"),
#     dash.dependencies.Input("remove-button", "n_clicks"),
#     dash.dependencies.Input("select-button", "n_clicks"),
#     dash.dependencies.Input("reset-button", "n_clicks"),
#     dash.dependencies.State("cytoscape", "elements"),
#     dash.dependencies.State("cytoscape", "selectedNodeData"),    
# )
# def network_graph_callback_dispatcher(remove, select, reset, elements, data):
#     elem = ctx.triggered_id
#     if elem == "remove-button":
#         return remove_selected_nodes(elements=elements, data=data)
#     elif elem == "select-button":
#         return select_nodes(elements=elements, data=data)
#     elif elem == "reset-button":
#         return reset_graph()
#     else:
#         raise ValueError("Invalid object")

# def reset_graph():
#     return metr_la_network 


# def remove_selected_nodes(elements, data):
#     if elements and data:
#         ids_to_remove = {ele_data["id"] for ele_data in data}
#         print("Before:", elements)
#         new_elements = [
#             ele for ele in elements if ele["data"]["id"] not in ids_to_remove
#         ]
#         print("After:", new_elements)
#         return new_elements

#     return elements

# def select_nodes(elements, data):
#     if elements and data:
#         ids_to_keep = {ele_data["id"] for ele_data in data}
#         print("Before:", elements)
#         new_elements = [
#             ele for ele in elements if (ele["data"]["id"] in ids_to_keep) or \
#             (ele["data"].get("source") and ele["data"]["source"] in ids_to_keep and ele["data"]["target"] in ids_to_keep) 
#         ]
#         print("After:", new_elements)
#         return new_elements

#     return elements


# @app.callback(
#     dash.dependencies.Output("tap-node-data-json-output", "children"), dash.dependencies.Input("cytoscape", "tapNodeData")
# )
# def displayTapNodeData(data):
#     return json.dumps(data, indent=2)


# @app.callback(
#     dash.dependencies.Output("tap-edge-data-json-output", "children"), dash.dependencies.Input("cytoscape", "tapEdgeData")
# )
# def displayTapEdgeData(data):
#     return json.dumps(data, indent=2)


# @app.callback(
#     dash.dependencies.Output("selected-node-data-json-output", "children"),
#     dash.dependencies.Input("cytoscape", "selectedNodeData"),
# )
# def displaySelectedNodeData(data):
#     return json.dumps(data, indent=2)


# @app.callback(
#     dash.dependencies.Output("selected-edge-data-json-output", "children"),
#     dash.dependencies.Input("cytoscape", "selectedEdgeData"),
# )
# def displaySelectedEdgeData(data):
#     return json.dumps(data, indent=2)

# df = pd.DataFrame(np.random.randn(100, 1), columns=['data'], index=pd.date_range('1/1/2020', periods=100))


# @app.callback(
#     dash.dependencies.Output('timeseries', 'figure'), 
#     [dash.dependencies.Input('date-picker', 'start_date'), dash.dependencies.Input('date-picker', 'end_date'), dash.dependencies.Input("aggregation", "value")])
# def update_chart(start, end, frequency):
#     dff = df.loc[start: end].resample(frequency).mean()
#     fig = px.line(dff, x=dff.index, y='data')
#     return fig



# def get_time_range_from_relayoutData(relayoutData):
#     """
#     Helper function to parse the selected time period from
#     the bar chart
#     """
#     time_range = [df_start, df_end]
#     if relayoutData is None:
#         pass
#     else:
#         if 'xaxis.range[0]' in relayoutData:
#             time_range = [pd.to_datetime(relayoutData['xaxis.range[0]']),
#                        pd.to_datetime(relayoutData['xaxis.range[1]'])]
#     return time_range


if __name__ == '__main__':
    app.run_server(debug=True)