import os
import pandas as pd

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.express as px
from dash.dependencies import State, Input, Output
from dash.exceptions import PreventUpdate

# Run this app with `python app.py` and
# visit http://{host}:8050/ in your web browser.

host='10.10.100.218'

app = dash.Dash(
    __name__,
    meta_tags=[
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1, maximum-scale=1.0, user-scalable=no",
        }
    ],
)
app.title = "CMS Hospital Data"
app.config["suppress_callback_exceptions"] = True
server = app.server

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

data_path = '/shared/matt/CMS/Data/CMS_HOSP_data'

data = dict()
for f in os.listdir(data_path):
    data_name = f[:-13]
    data[data_name] = pd.read_csv((data_path + '/' + f))

"""df = data['Timely_and_Effective_Care-Hospital']
    df = df[df['Measure Name'] == value]
    df = df[df['Score'] != 'Not Available']
    df['Score'] = df['Score'].astype(float)
    fig1 = px.histogram(df, x="Score")"""


app.layout = html.Div(
    [
        html.Div([
        dcc.Dropdown(
            id='dataset-dropdown',
            options=[{'label':name, 'value':name} for name in list(data.keys())],
            value = list(data.keys())[0]
            ),
            ],style={'width': '30%', 'display': 'inline-block'}),
        html.Div([
        dcc.Dropdown(
            id='measure-dropdown',
            ),
            ],style={'width': '69%', 'display': 'inline-block'}
        ),
        html.Hr(),
        dcc.Graph(id='histogram', figure={})
    ]
)

@app.callback(
    dash.dependencies.Output('measure-dropdown', 'options'),
    [dash.dependencies.Input('dataset-dropdown', 'value')]
)
def update_measure_dropdown(dataset_name):
    df = data[dataset_name]
    return [{'label': i, 'value': i} for i in list(data[dataset_name]['Measure Name'].unique())]



@app.callback(
    dash.dependencies.Output('histogram', 'figure'),
    dash.dependencies.Input('measure-dropdown', 'value'),
    dash.dependencies.Input('dataset-dropdown', 'value')
)
def update_graph(selected_measure, selected_dataset):
    df = data[selected_dataset]
    df = df[df['Measure Name'] == selected_measure]
    df = df[df['Score'] != 'Not Available']
    df['Score'] = df['Score'].astype(float)
    fig1 = px.histogram(df, x="Score", 
        title = selected_measure
    )
    return fig1
    #return 'You have selected "{}"'.format(value)



    

if __name__ == '__main__':
    app.run_server(host, port=8050, debug=True)