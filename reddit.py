import praw
import json
import pandas as pd
from itertools import combinations


def flatten_list(multi_list):
    return [item for sublist in multi_list for item in sublist]


def format_node(node_type, name):
    return {'data': {'id': str(name), 'classes': node_type, 'tooltip': '<a href="https://github.com/QuantStack/ipycytoscape/issues/82">My 5</a>'}}


def build_nodes(df, node_type):
    return [format_node(node_type, name) for name in df[node_type].unique()]


def build_edges(df, source, target):
    records = df[[source, target]].to_records(index=False)
    return [{'data': {'source': str(i[0]), 'target': str(i[1])}} for i in records]

def load_json(path):
    with open(path) as f:
        return json.load(f)

class redditGraph():
    def __init__(self, sub, query):
        config = load_json('./config.json')
        self.client = praw.Reddit(
            client_id=config['client_id'],
            client_secret=config['secret'],
            user_agent=f"<platform>:{config['client_id']}:0.1 (by u/edgewize_)",
        )
        self.node_types = ['author', 'title', 'subreddit', 'created']
        self.subreddit = sub
        self.query = query

    def search(self):
        return self.client.subreddit(self.subreddit).search(self.query)

    def cyto_data(self):
        search = self.search()
        df = pd.DataFrame([i.__dict__ for i in search])
        df['author'] = df['author'].apply(lambda x: x.name)
        nodes = flatten_list([build_nodes(df, node_type)
                             for node_type in self.node_types])
        relationships = combinations(self.node_types, 2)
        edges = flatten_list([build_edges(df, i[0], i[1])
                             for i in relationships])
        elements = flatten_list([nodes, edges])
        return elements


if __name__ == "__main__":
    client_id = "76zZBSNM5hKJ556gC2G6lA"
    secret = "mdly8KNyZIP6FXDlgpU9IyYiIxjkTQ"
    elements = redditGraph(client_id, secret, 'all', 'yolo').cyto_data()
