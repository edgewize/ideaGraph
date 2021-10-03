import ideaGraph
import dash
import json
import pandas as pd
from dash_cytoscape.Cytoscape import Cytoscape
from dash import html
from dash import dcc
import dash_cytoscape as cyto
from dash.dependencies import Input, Output

app = dash.Dash(__name__)


cyto_style = [
    {
        'selector': '.author',
        'style': {
                    'background-color': 'red',
                    'line-color': 'red'
        }
    }
]
layout_dropdown = dcc.Dropdown(
    id='dropdown-callbacks-1',
    value='circle',
    clearable=False,
    options=[
        {'label': name.capitalize(), 'value': name}
        for name in ['concentric', 'grid', 'random', 'circle', 'cose']
    ]
)
search_input = html.Div([
    "Input: ",
    dcc.Input(id='search', value='yolo', type='text')
])
submit_button = html.Button('Submit', id='submit', n_clicks=0)
network_viz = cyto.Cytoscape(
    id='cytoscape',
    style={'width': '[100%', 'height': '800px'},
    stylesheet=cyto_style
)
timeline_viz = dcc.Graph(id='timeline')
node_info = html.P(id='node-info')

row_1 = html.Div([search_input, submit_button])
col_2 = html.Div([layout_dropdown, node_info, network_viz])
row_2 = html.Div([timeline_viz, col_2], style={
                 'columnCount': 2})
row_3 = html.Div([dcc.Store(id='project-data')])
app_layout = html.Div([row_1, row_2, row_3])
app.layout = html.Div(app_layout)


@ app.callback(
    dash.dependencies.Output('project-data', 'data'),
    [dash.dependencies.Input('submit', 'n_clicks')],
    [dash.dependencies.State('search', 'value')])
def get_data(n_clicks, value):
    reddit_search = ideaGraph.reddit('all', value)
    test = True
    if value == 'yolo':
        with open('yolo.json', 'r') as file:
            data = json.load(file)
    else:
        data = reddit_search.search().to_json()
    return data


@ app.callback(Output('timeline', 'figure'), Input('project-data', 'data'))
def update_timeline(data):
    reddit_search = ideaGraph.reddit(None, None)
    df = reddit_search.format_df(pd.DataFrame(json.loads(data)))
    reddit_search.set_df(df)
    fig = reddit_search.timeline()
    return fig


@ app.callback(Output('cytoscape', 'elements'), Input('project-data', 'data'))
def update_cytoscape(data):
    reddit_search = ideaGraph.reddit(None, None)
    reddit_search.set_df(pd.DataFrame(json.loads(data)))
    elements = reddit_search.cytoscape()
    return elements


@ app.callback(Output('node-info', 'children'),
               Input('cytoscape', 'mouseoverNodeData'))
def displayTapNodeData(data):
    if data:
        return f"{data['classes']}: {data['id']}"


@ app.callback(Output('cytoscape', 'layout'),
               Input('dropdown-callbacks-1', 'value'))
def update_layout(layout):
    return {'name': layout}


if __name__ == '__main__':
    app.run_server(debug=True)
