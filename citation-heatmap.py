"""Plotting heatmap of citation per episode of Kaamelott.

"""
import re
import json
import urllib.request
import itertools
from collections import defaultdict
import data as data_module

import plotly.offline as py
import plotly.graph_objs as go

FILE_OUT = 'out/citation-count-heatmap.htm'


def citation_heatmap(data):
    """Return the pyplot html/js describing an heatmap over given data"""
    MAX_CITE_COUNT = max(len(cites) for ep in data.values() for cites in ep.values())
    number_of_citation_per_episode = [
        [len(data[season].get(episode, ())) for episode in range(1, 1+max(data[season]))]
        for season in data_module.LIVRE_ORDER_NUMERAL
    ]
    text_per_episode = [
        ['<br>'.join(c.text for c in data[season].get(episode, ())) for episode in range(1, 1+max(data[season]))]
        for season in data_module.LIVRE_ORDER_NUMERAL
    ]

    def keycolor_from_nbcit(nb:int) -> str:
        ratio = round(nb / MAX_CITE_COUNT, 2)
        val = (ratio) * 255
        red = 255-int(round(ratio * 255, 0))
        green = int(round(255, 0))
        blue = 255-int(round(ratio * 255, 0))
        return [ratio, f'rgb({red},{green},{blue})']

    colorscale = [keycolor_from_nbcit(nb) for nb in range(MAX_CITE_COUNT+1)]

    trace = go.Heatmap(
        z=number_of_citation_per_episode,
        y=[f'Livre {s}' for s in data_module.LIVRE_ORDER],
        text=text_per_episode,
        colorscale=colorscale,
    )
    return py.plot([trace], output_type='div')


if __name__ == '__main__':
    data = data_module.extract()
    html = citation_heatmap(data)
    with open(FILE_OUT, 'w') as fd:
        fd.write(html)
