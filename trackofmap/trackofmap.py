import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
import plotly.graph_objs as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash()
server = app.server
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

mapbox_access_token = 'pk.eyJ1IjoibW9vbmluZ3dpbmUiLCJhIjoiY2p3aTIxdWg0MDFyaTRhbHBoOTlhb2dwZCJ9.fnhC8DX58l5SX__iBqSotw'

df = pd.read_csv("./timestep-s.csv")
centerdf = pd.read_csv("./centerOfVenues.csv")
avgdf = pd.read_csv("./avgDistanceTravel.csv")
available_userid = np.sort(df['userId'].unique())


app.layout = html.Div([
    html.Div([
        html.Div([html.H1("Trace of Time & Space")],
             style={'textAlign': "center", "padding-bottom": "10", "padding-top": "10"}),
        # html.Label('userID'),
        html.Div([
            html.Label('userID'),
            dcc.Dropdown(
                id='userID',
                options=[{'label': i, 'value': i} for i in available_userid],
                value=943
            )
        ],
            style={"display": "block", "margin-left": "auto", "margin-right": "auto", "width": "20%"})

    ]),

    html.Div([
        dcc.Graph(
            id='indicator-graphic'
        )
    ],
        style={'display': 'inline-block', 'padding': '50','textAlign': "center"})

], className="page")

@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('userID', 'value')])
def update_graph(user_id):
    filtered_df = df[df.userId == user_id]
    lat_center=centerdf[centerdf.userId==user_id].iloc[0,0]
    lon_center = centerdf[centerdf.userId == user_id].iloc[0, 1]
    avgdistance=avgdf[avgdf.userId==user_id].iloc[0,0]
    #print(lat_center, lon_center)
    # available_time=filtered_df['time'].unique()

    data = list()
    data_lines=list()

    data_lines .append(go.Scattermapbox(
        lat=filtered_df['latitude'],
        lon=filtered_df['longitude'],
        text=[(a, b) for a, b in zip(filtered_df['venueCategory'], filtered_df['time'])],
        mode='lines',
        opacity=0.3,
        marker=go.scattermapbox.Marker(
            opacity=1.0,
            color='rgb(115,115,115)',
            # colorscale='Blues',
            # showscale=True,
            size=5),
        name='lines'
    ))
    for i in range(len(filtered_df)):
        data.append(go.Scattermapbox(
            lat=[filtered_df.iloc[i,4]],
            lon=[filtered_df.iloc[i,5]],
            #text=[(a, b) for a, b in zip(filtered_df['venueCategory'], filtered_df['time'])],
            mode='markers',
            opacity=0.9,
            marker=go.scattermapbox.Marker(
                opacity=0.9,
                size=12
             ),
            name=str(filtered_df.iloc[i,1])+' '+filtered_df.iloc[i,3]
        ))
    data.append(go.Scattermapbox(
        lat=[lat_center],
        lon=[lon_center],
        # text=[(a, b) for a, b in zip(filtered_df['venueCategory'], filtered_df['time'])],
        mode='markers',
        opacity=0.9,
        marker=go.scattermapbox.Marker(
            opacity=1,
            color='#FFD700',
            size=30
        ),
        name='center'
    ))


    return {
        'data': data_lines+data,
        'layout': go.Layout(
            height=700,
            width=1200,
            xaxis={
                'title': 'longitude'#,
                #'type': 'linear' if xaxis_type == 'Linear' else 'log'
            },
            yaxis={
                'title': 'latitude'#,
                #'type': 'linear' if yaxis_type == 'Linear' else 'log'
            },
            margin={'l': 100, 'b': 40, 't': 50, 'r': 50},
            hovermode='closest',
            mapbox=go.layout.Mapbox(
                accesstoken=mapbox_access_token,
                bearing=0,
                center=go.layout.mapbox.Center(
                    lat=35.65,
                    lon=139.7
                ),
                pitch=0,
                zoom=10,
                #style='mapbox://styles/mooningwine/cjwoikmng4w661cup5jombdqe'
                style='mapbox://styles/mapbox/light-v9'
            ),

        )
    }
'''
external_css = ["https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",
                "https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "https://codepen.io/ffzs/pen/mjjXGM.css",
                "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"]

for css in external_css:
    app.css.append_css({"external_url": css})
'''

if __name__ == '__main__':
    app.run_server(debug=True)