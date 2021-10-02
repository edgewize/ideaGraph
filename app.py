import dash
from dash_cytoscape.Cytoscape import Cytoscape
import reddit
from dash import html
from dash import dcc
import dash_cytoscape as cyto
from dash.dependencies import Input, Output

app = dash.Dash(__name__)


app.layout = html.Div([
    html.Div([
        "Input: ",
        dcc.Input(id='search', value='yolo', type='text')
    ]),
    html.Button('Submit', id='submit', n_clicks=0),
    cyto.Cytoscape(
        id='cytoscape',
        style={'width': '[100%', 'height': '800px'},
        layout={'name': 'cose'},
        stylesheet=[
            {
                'selector': '.subreddit',
                'style': {
                    'background-color': 'red',
                    'line-color': 'red',
                }
            }
        ]
    ),
    html.P(id='node-info'),
])


@app.callback(
    dash.dependencies.Output('cytoscape', 'elements'),
    [dash.dependencies.Input('submit', 'n_clicks')],
    [dash.dependencies.State('search', 'value')])
def update_output(n_clicks, value):
    elements = reddit.redditGraph('all', value).cyto_data()
    return elements

@app.callback(Output('node-info', 'children'),
              Input('cytoscape', 'mouseoverNodeData'))
def displayTapNodeData(data):
    if data:
        return f"{data['classes']}: {data['id']}"


if __name__ == '__main__':
    app.run_server(debug=True)
