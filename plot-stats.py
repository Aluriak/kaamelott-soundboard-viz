"""Plotting of Kaamelott data, using file sounds.json of
kaamelott-soundboard project.

"""
import re
import json
import itertools
from collections import defaultdict

import plotly.offline as py
import plotly.graph_objs as go


REGEX_INFO = re.compile(r'Livre ([IV]+), ([0-9]+) - (.*)')
LIVRE_ORDER = 'I', 'II', 'III', 'IV', 'V', 'VI', 'VI'
# ROMAN_TO_INT = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6}
# INT_TO_ROMAN = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI'}


def extract_data():
    "Return dict mapping season -> episode -> [citations]"
    data = defaultdict(lambda: defaultdict(list))
    with open('sounds.json') as fd:
        rawjson = json.load(fd)
    for citation in rawjson:
        match = REGEX_INFO.fullmatch(citation['episode'])
        if not match:
            print(f'WARNING citation {citation} is not properly formatted. Ignored.')
            continue
        season, number, title = match.groups(0)
        data[season][int(number)].append(citation['title'])
    return data


def citation_heatmap():
    data = extract_data()
    MAX_CITE_COUNT = max(len(cites) for ep in data.values() for cites in ep.values())
    for season in LIVRE_ORDER:
        print(season, max(data[season]))
    formated = [
        [len(data[season][episode]) for episode in range(max(data[season]))]
        for season in LIVRE_ORDER
    ]
    formated_text = [
        ['<br>'.join(data[season][episode]) for episode in range(max(data[season]))]
        for season in LIVRE_ORDER
    ]

    def keycolor_from_nbcit(nb:int) -> str:
        ratio = round(nb / MAX_CITE_COUNT, 2)
        val = (ratio) * 255
        red = 255-int(round(ratio * 255, 0))
        green = int(round(255, 0))
        blue = 255-int(round(ratio * 255, 0))
        print('C:', nb, red, blue)
        return [ratio, f'rgb({red},{green},{blue})']

    colorscale = [keycolor_from_nbcit(nb) for nb in range(MAX_CITE_COUNT+1)]
    print('COLORSCALE:', colorscale)

    trace = go.Heatmap(
        z=formated,
        y=[f'Livre {s}' for s in LIVRE_ORDER],
        text=formated_text,
        colorscale=colorscale,
    )
    with open('out.html', 'w') as fd:
        html = py.plot([trace], output_type='div')
        fd.write(html)
        print('done')


if __name__ == '__main__':
    citation_heatmap()
