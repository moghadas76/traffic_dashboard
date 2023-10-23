import os
import json
import dash
import pandas as pd
import plotly.graph_objs as go
import dash_cytoscape as cyto


from dotenv import load_dotenv
from dash import dcc, ctx
from dash import html

from dashboard.assets import metr_la_network
from dashboard.styles import styles

load_dotenv()

# External recources
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
mapbox_access_token = os.getenv("mapbox_access_token")

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Read sample data
df = pd.read_csv('./assets/data_sample.csv')
df['dtg'] = pd.to_datetime(df['dtg'])

# Get start and end of sample data set
df_start = pd.to_datetime(df.sort_values('dtg')['dtg'].values[0])
df_end = pd.to_datetime(df.sort_values('dtg')['dtg'].values[-1])

# Get categories of sampel data set
causes_all = sorted(list(df.cause.unique()))
cause_options = [{'label': x, 'value': x} for x in ['All'] + causes_all]
cause_options_map = {x: [x] for x in causes_all}
cause_options_map['All'] = causes_all

colors = ['red', 'green', 'black']
cause_colors_map = dict(zip(causes_all, colors))

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
    html.Div(
        [
            html.Div(
                [
                    html.Div(children="Select categories:"),
                    dcc.Dropdown(
                        id='dropdown',
                        options=cause_options,
                        value=['ALL'],
                        clearable=False,
                        multi=True
                    ),
                ],
                className='three columns',
                style={'width': '30%'}
            ),
            html.Div(
                [
                    html.Div(children="Enter temporal aggregation window (eg 3H/1D/2W/3M/...):"),
                    dcc.Input(
                        id='aggregation',
                        placeholder='Enter a value...',
                        type='text',
                        value='1M'
                    ),
                ],
                className='three columns',
                style={'width': '30%'}
            ),
            html.Div(
                [
                    html.Div(children="Enter Node Id (eg,. 1, 2,3,4, ...). -1 means All nodes"),
                    dcc.Input(
                        id='node_id',
                        placeholder='Enter a value...',
                        type='number',
                        value='-1'
                    ),
                ],
                className='three columns',
                style={'width': '30%'}
            ),
        ],
        className='row'
    ),
    html.Hr(),
    html.Div(
        [
            html.Div(
                [
                    dcc.Graph(
                        id='bar-ts',
                        style={'height': 580},
                        config={
                            'displayModeBar': False
                        },
                    ),
                ],
                className='two columns',
                style={'width': '48%'}
            ),
            html.Div(
                [
                    dcc.Graph(
                        id='point-map',
                        style={'height': 580},
                        config={
                            'displayModeBar': False,
                        },
                    ),
                ],
                className='two columns',
                style={'width': '48%'}
            ),
        ],
        className='row'
    ),
    html.Div(
        cyto.Cytoscape(
            id='cytoscape',
            elements=metr_la_network,
            layout={"name": "grid"},
            style={"height": "95vh", "width": "100%"},
        )
    ),
    html.Div(
            className="four columns",
            children=[
                dcc.Tabs(
                    id="tabs",
                    children=[
                        dcc.Tab(
                            label="Actions",
                            children=[
                                html.Button("Remove Selected Node", id="remove-button"),
                                html.Button("Select Nodes", id="select-button"),
                                html.Button("Reset", id="reset-button"),
                            ],
                        ),
                        dcc.Tab(
                            label="Tap Data",
                            children=[
                                html.Div(
                                    style=styles["tab"],
                                    children=[
                                        html.P("Node Data JSON:"),
                                        html.Pre(
                                            id="tap-node-data-json-output",
                                            style=styles["json-output"],
                                        ),
                                        html.P("Edge Data JSON:"),
                                        html.Pre(
                                            id="tap-edge-data-json-output",
                                            style=styles["json-output"],
                                        ),
                                    ],
                                )
                            ],
                        ),
                        dcc.Tab(
                            label="Selected Data",
                            children=[
                                html.Div(
                                    style=styles["tab"],
                                    children=[
                                        html.P("Node Data JSON:"),
                                        html.Pre(
                                            id="selected-node-data-json-output",
                                            style=styles["json-output"],
                                        ),
                                        html.P("Edge Data JSON:"),
                                        html.Pre(
                                            id="selected-edge-data-json-output",
                                            style=styles["json-output"],
                                        ),
                                    ],
                                )
                            ],
                        ),
                    ],
                ),
            ],
    ),
    html.Div(id='text_output_range'),
])


@app.callback(
    dash.dependencies.Output('bar-ts', 'figure'),
    [dash.dependencies.Input('dropdown', 'value'),
     dash.dependencies.Input('aggregation', 'value')])
def update_bar_figure(selected_cause, aggregation):
    """
    Provide data to bar chart
    """

    # Select category
    selected_cause_list = cause_options_map[selected_cause]
    df_filtered = df[df.cause.isin(selected_cause_list)]

    # Aggregate to given time bins
    df_rs = df_filtered.set_index('dtg').groupby('cause')
    try:
        df_rs = df_rs.resample(aggregation).count()['lat'].rename('counts')
    except:
        df_rs = df_rs.resample('3M').count()['lat'].rename('counts')

    data_bar = []
    for cause in sorted(selected_cause_list):
        data_bar.append(
            go.Bar(
                x=[str(x) for x in list(df_rs[cause].index)],
                y=df_rs[cause].values,
                marker=dict(
                    color=cause_colors_map[cause]),
                name=cause,
            ))

    return {
        'data': data_bar,
        'layout': layout_bar
    }


@app.callback(
    dash.dependencies.Output('text_output_range', 'children'),
    [dash.dependencies.Input('bar-ts', 'relayoutData')])
def update_output_text(relayoutData):
    """
    Print selected time range
    """
    time_range = get_time_range_from_relayoutData(relayoutData)
    res = 'Selected range: {} - {}'.format(time_range[0], time_range[1])
    return res


@app.callback(
    dash.dependencies.Output('point-map', 'figure'),
    [dash.dependencies.Input('bar-ts', 'relayoutData'),
     dash.dependencies.Input('dropdown', 'value')])
def update_map_figure(relayoutData, selected_cause):
    """
    Provide data to map
    """

    # Select given time range and category
    time_range = get_time_range_from_relayoutData(relayoutData)
    selected_cause_list = cause_options_map[selected_cause]
    df_filtered = df[(df.dtg >= time_range[0]) &
                     (df.dtg <= time_range[1]) &
                     df.cause.isin(selected_cause_list)]

    data = []
    for cause in sorted(selected_cause_list):
        data.append(
            go.Scattermapbox(
                lon=df_filtered[df_filtered.cause == cause]['lon'],
                lat=df_filtered[df_filtered.cause == cause]['lat'],
                mode='markers',
                marker=dict(
                    size=8,
                    # color='rgb(255, 0, 0)',
                    color=cause_colors_map[cause],
                    opacity=0.7
                ),
                name=cause,
                hoverinfo='name'
            )
        )

    return {
        'data': data,
        'layout': layout_map
    }

@app.callback(
    dash.dependencies.Output("cytoscape", "elements"),
    dash.dependencies.Input("remove-button", "n_clicks"),
    dash.dependencies.Input("select-button", "n_clicks"),
    dash.dependencies.Input("reset-button", "n_clicks"),
    dash.dependencies.State("cytoscape", "elements"),
    dash.dependencies.State("cytoscape", "selectedNodeData"),    
)
def network_graph_callback_dispatcher(remove, select, reset, elements, data):
    elem = ctx.triggered_id
    if elem == "remove-button":
        return remove_selected_nodes(elements=elements, data=data)
    elif elem == "select-button":
        return select_nodes(elements=elements, data=data)
    elif elem == "reset-button":
        return reset_graph()
    else:
        raise ValueError("Invalid object")

def reset_graph():
    return metr_la_network 


def remove_selected_nodes(elements, data):
    if elements and data:
        ids_to_remove = {ele_data["id"] for ele_data in data}
        print("Before:", elements)
        new_elements = [
            ele for ele in elements if ele["data"]["id"] not in ids_to_remove
        ]
        print("After:", new_elements)
        return new_elements

    return elements

def select_nodes(elements, data):
    if elements and data:
        ids_to_keep = {ele_data["id"] for ele_data in data}
        print("Before:", elements)
        new_elements = [
            ele for ele in elements if (ele["data"]["id"] in ids_to_keep) or \
            (ele["data"].get("source") and ele["data"]["source"] in ids_to_keep and ele["data"]["target"] in ids_to_keep) 
        ]
        print("After:", new_elements)
        return new_elements

    return elements


@app.callback(
    dash.dependencies.Output("tap-node-data-json-output", "children"), dash.dependencies.Input("cytoscape", "tapNodeData")
)
def displayTapNodeData(data):
    return json.dumps(data, indent=2)


@app.callback(
    dash.dependencies.Output("tap-edge-data-json-output", "children"), dash.dependencies.Input("cytoscape", "tapEdgeData")
)
def displayTapEdgeData(data):
    return json.dumps(data, indent=2)


@app.callback(
    dash.dependencies.Output("selected-node-data-json-output", "children"),
    dash.dependencies.Input("cytoscape", "selectedNodeData"),
)
def displaySelectedNodeData(data):
    return json.dumps(data, indent=2)


@app.callback(
    dash.dependencies.Output("selected-edge-data-json-output", "children"),
    dash.dependencies.Input("cytoscape", "selectedEdgeData"),
)
def displaySelectedEdgeData(data):
    return json.dumps(data, indent=2)



def get_time_range_from_relayoutData(relayoutData):
    """
    Helper function to parse the selected time period from
    the bar chart
    """
    time_range = [df_start, df_end]
    if relayoutData is None:
        pass
    else:
        if 'xaxis.range[0]' in relayoutData:
            time_range = [pd.to_datetime(relayoutData['xaxis.range[0]']),
                       pd.to_datetime(relayoutData['xaxis.range[1]'])]
    return time_range


if __name__ == '__main__':
    app.run_server(debug=True)