"""Plotting of Kaamelott data, using file sounds.json of
kaamelott-soundboard project.

"""
import re
import json
import urllib.request
import itertools
from collections import defaultdict

import plotly.offline as py
import plotly.graph_objs as go


DATAFILE_URL = 'https://raw.githubusercontent.com/2ec0b4/kaamelott-soundboard/master/sounds/sounds.json'
REGEX_INFO = re.compile(r'Livre ([IV]+), ([0-9]+) - (.*)')
LIVRE_ORDER = 'I', 'II', 'III', 'IV', 'V', 'VI', 'VI'


def extract_jsondata_from_web(url=DATAFILE_URL):
    with urllib.request.urlopen(DATAFILE_URL) as fd:
        return json.load(fd)

def extract_jsondata_from_file(fname='sounds.json'):
    with open(fname) as fd:
        return json.load(fd)


def extract_data_from_json(rawjson:list):
    "Return dict mapping season -> episode -> [citations]"
    data = defaultdict(lambda: defaultdict(list))
    for citation in rawjson:
        match = REGEX_INFO.fullmatch(citation['episode'])
        if not match:
            print(f'WARNING citation {citation} is not properly formatted. Ignored.')
            continue
        season, number, title = match.groups(0)
        data[season][int(number)].append(citation['title'])
    return data


def citation_heatmap(data):
    MAX_CITE_COUNT = max(len(cites) for ep in data.values() for cites in ep.values())
    formated = [
        [len(data[season][episode+1]) for episode in range(max(data[season]))]
        for season in LIVRE_ORDER
    ]
    formated_text = [
        ['<br>'.join(data[season][episode+1]) for episode in range(max(data[season]))]
        for season in LIVRE_ORDER
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
        z=formated,
        y=[f'Livre {s}' for s in LIVRE_ORDER],
        text=formated_text,
        colorscale=colorscale,
    )
    with open('out.html', 'w') as fd:
        html = py.plot([trace], output_type='div')
        fd.write(html)


if __name__ == '__main__':
    data = extract_data_from_json(extract_jsondata_from_file())
    citation_heatmap(data)
