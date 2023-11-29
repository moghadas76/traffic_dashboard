import os

import dash
import numpy as np
import plotly.graph_objs as go
import plotly.express as px

from datetime import datetime as dt


from dotenv import load_dotenv
from dash import dcc, ctx
from dash import html
from dash import dash_table
from omegaconf import OmegaConf

# from dashboard.assets import metr_la_network
from dashboard.utils.data_loader import load_dataframes, get_plotly_figure
from dashboard.defaults import ChartDefaults
load_dotenv()
# External recources
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
mapbox_access_token = os.getenv("mapbox_access_token")

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Read sample data
np.random.seed(1)
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
    html.Div(
        [
            html.Div(children="Select Sensor:"),
            dcc.Dropdown(
                id='dropdown',
                options=[{"label": value, "value": value} for value in df["source.id"].unique().tolist()],
                clearable=False,
                multi=False
            ),
            html.Br(),
            html.Div([
                html.Div(id='date-picker', children="Select Date Range:"),
                dcc.DatePickerRange(
                    id='date-picker-range',
                    min_date_allowed=dt(2022, 8, 5),
                    max_date_allowed=dt(2024, 9, 19),
                    initial_visible_month=dt(2023, 11, 1),
                    end_date=dt(2023, 11, 30),
                    start_date=dt(2023, 1, 30),
                ),
            ]),
            html.Br(),
            html.Button(id="filter-btn", children="Filter", n_clicks=0),
            html.Button("Refresh", id="refresh-button", n_clicks=0),
        ],
        style={"margin":
               {'r': 20,
                't': 20,
                'b': 5,
                'l': 5,
                'pad': 0}}
    ),
    html.Br(),
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
])



if __name__ == '__main__':
    app.run_server(debug=True)