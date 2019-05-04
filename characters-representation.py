"""Create pie chart showing characters presence in the dataset"""

import data as data_module
from collections import Counter

import plotly.offline as py
import plotly.graph_objs as go

FILE_OUT_PIE = 'out/characters-pie.htm'
FILE_OUT_BAR = 'out/characters-bar.htm'


def counts_and_citations(data, livres=0, episodes=0) -> (dict, tuple):
    # decides episodes to keep, keep them ordered in memory
    citations = (
        (char, citation.text)
        for livre in data
        for episode in data[livre]
        for citation in data[livre][episode]
        for char in citation.characters
        if data_module.belongs(data, livre, episode, livres, episodes)
    )
    counts = Counter(c for c, _ in citations)
    char_citations = {}
    for char, text in citations:
        char_citations.setdefault(char, []).append(text)
    counts = tuple(sorted(tuple(counts.items())))
    return char_citations, counts


def make_chart(data, livres=0, episodes=0):
    char_citations, counts = counts_and_citations(data, livres, episodes)
    labels, values = zip(*counts)
    trace = go.Pie(labels=labels, values=values)
    return py.plot([trace], output_type='div')


def make_stacked_bar(data, livres=0, episodes=0):
    # for each livre, make a trace (they will be stacked later)
    traces = []
    for livre in data_module.LIVRE_ORDER_NUMERAL:
        if livres and livre != livres and livre not in livres:  continue  # unwanted livre
        char_citations, counts = counts_and_citations(data, livre, episodes)
        labels, values = zip(*counts)
        name = 'Livre ' + data_module.LIVRE_ROMAN[livre]
        traces.append(go.Bar(x=labels, y=values, name=name))
    # stack and generate
    fig = go.Figure(traces, layout=go.Layout(barmode='stack'))
    return py.plot(fig, output_type='div')


if __name__ == '__main__':
    data = data_module.extract()
    html = make_chart(data)
    with open(FILE_OUT_PIE, 'w') as fd:
        fd.write(html)
    html = make_stacked_bar(data)
    with open(FILE_OUT_BAR, 'w') as fd:
        fd.write(html)
