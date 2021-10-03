import praw
import json
import pandas as pd
import plotly.express as px
from itertools import combinations


def flatten_list(multi_list):
    return [item for sublist in multi_list for item in sublist]


def format_node(node_type, name):
    return {'data': {'id': str(name), 'classes': node_type, 'tooltip': '<a href="https://github.com/QuantStack/ipycytoscape/issues/82">My 5</a>'}}


def build_nodes(df, node_type):
    return [format_node(node_type, name) for name in df[node_type].unique()]


def build_edges(df, source, target):
    records = df[[source, target]].to_records(index=False)
    format_records = [
        {'data': {'source': str(i[0]), 'target': str(i[1])}} for i in records]
    return format_records


def load_json(path):
    with open(path) as f:
        return json.load(f)


def df_to_cytoscape(df, node_types, relationships=None):
    """
    relationships = [('source', 'target'), ...]
    """
    if relationships is None:
        relationships = combinations(node_types, 2)
    nodes = flatten_list([build_nodes(df, node_type)
                          for node_type in node_types])
    edges = flatten_list([build_edges(df, i[0], i[1])
                          for i in relationships])
    elements = flatten_list([nodes, edges])
    return elements


class reddit():
    def __init__(self, sub, query):
        config = load_json('./config.json')
        self.client = praw.Reddit(
            client_id=config['client_id'],
            client_secret=config['secret'],
            user_agent=f"<platform>:{config['client_id']}:0.1 (by u/edgewize_)",
        )
        self.node_types = ['author', 'title',
                           'subreddit']
        self.subreddit = sub
        self.query = query
        self.df = None

    def format_df(self, df):
        df['subreddit'] = df['subreddit'].apply(lambda x: str(x))
        df['created'] = pd.to_datetime(df['created'], unit='ms')
        df['year-month'] = df['created'].apply(lambda x: f'{x.year}-{x.month}')
        df['month-day'] = df['created'].apply(lambda x: f'{x.month}-{x.day}')
        return df

    def search(self):
        search = self.client.subreddit(
            self.subreddit).search(self.query, limit=None)
        df = pd.DataFrame([i.__dict__ for i in search])
        df['author'] = df['author'].apply(lambda x: x.name)
        df['created'] = pd.to_datetime(
            df['created'], unit='s')
        self.df = self.format_df(df)
        return self.df

    def set_df(self, df):
        self.df = df
        return True

    def get_df(self):
        if self.df is None:
            self.search()
        df = self.df
        return df

    def timeline(self):
        df = self.get_df()
        daily_counts_by_sub = df.set_index('created').groupby([pd.Grouper(freq='d'), 'subreddit']).count()[
            'id'].fillna(0).reset_index()
        fig = px.bar(daily_counts_by_sub, x='created',
                     y='id', color='subreddit')
        return fig

    def cytoscape(self):
        df = self.get_df()
        return df_to_cytoscape(df, self.node_types)


if __name__ == "__main__":
    r = reddit('all', 'yolo')

    # elements = r.cytoscape()
