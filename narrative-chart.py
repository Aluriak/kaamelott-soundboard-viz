"""Create a narrative chart using the characters cited in each episode"""

import itertools
import data as data_module
from collections import defaultdict

import plotly.offline as py
import plotly.graph_objs as go

DEFAULT_TITLE = 'Kaamelott Narrative Chart'


def make_sankey_chart(labels, sources, targets, values, descs,
                      title:str=DEFAULT_TITLE, black_theme:bool=False) -> str:
    "Return the HTML describing a sankey chart, according to given args"
    data = {
        'type': 'sankey',
        # 'width': 4000,
        # 'height': 1000,
        'orientation': 'h',
        'valuesuffix': " personnages",
        'valueformat': '.i',
        'node': {
            'pad': 15,
            'thickness': 3,
            'line': {'color': 'black'},
            'label': labels,
        },
        'link': {
            'source': sources,
            'target': targets,
            'value': values,
            'label': descs,
        }
    }
    layout = {'title': title, 'font': {'size': 12}}
    if black_theme:
        layout.update({
            'plot_bgcolor': 'black',
            'paper_bgcolor': 'black',
        })
        layout['font']['color'] = 'white'
    fig = {'data': [data], 'layout': layout}
    return py.offline.plot(fig, auto_open=False, output_type='div')


def make_chart(data, livres=0, episodes=0):
    # decides episodes to keep, keep them ordered in memory
    belonging_episodes = tuple(
        (livre, episode, characters)
        for livre, episode, characters in characters_from_data(data)
        if data_module.belongs(data, livre, episode, livres, episodes)
    )
    all_characters = frozenset(itertools.chain.from_iterable(c for l, e, c in belonging_episodes))
    print('ALL CHARACTERS:', ', '.join(sorted(tuple(all_characters))))
    belonging_episodes = ((0, 0, all_characters),) + belonging_episodes + ((0, 0, all_characters),)
    # decide which are followed by which
    # print(belonging_episodes)
    followers = find_followers(belonging_episodes)
    # print(followers)
    # create data for each link
    def links_from_followers(episodes:tuple, followers:dict) -> [(int, int, int, str)]:
        "Yield (source, target, nb character, character names)"
        for src, succs in followers.items():
            for succ, chars in succs.items():
                yield src, succ, len(chars), ', '.join(chars)
    sources, targets, values, descrs = zip(*links_from_followers(belonging_episodes, followers))
    labels = tuple(f'{livre}-{episode:02}' if livre != 0 else ''
                   for livre, episode, _ in belonging_episodes)
    return make_sankey_chart(labels, sources, targets, values, descrs)


def find_followers(episodes) -> dict:
    followers = defaultdict(dict)
    for idx, (pred_livre, pred_ed, pred_chars) in enumerate(episodes):
        unplaced_characters = set(pred_chars)
        for succ_idx, (succ_livre, succ_ep, succ_chars) in enumerate(episodes[idx+1:], start=idx+1):
            common = unplaced_characters & succ_chars
            # print(idx, succ_idx)
            # print('\t', unplaced_characters)
            # print('\t', set(succ_chars))
            # print('\t->', common)
            if common:
                unplaced_characters -= common
                followers[idx][succ_idx] = common
            if not unplaced_characters: break  # this episode found all its successors
        else:  # the unplaced characters are not reused later…
                    ...  # TODO: there is something to implement here
    return dict(followers)


def characters_from_data(data) -> [int, int, {str}]:
    "Yield (livre, episode, characters in that episode), ordered by standard episode order"
    for livre in data_module.LIVRE_ORDER_NUMERAL:
        first, last = min(data[livre]), max(data[livre])
        for episode in range(first, last+1):
            chars = set()
            for citation in data[livre].get(episode, ()):
                chars |= citation.characters
            # print('ATELTQ:', livre, episode, chars)
            yield livre, episode, frozenset(chars)




if __name__ == '__main__':
    LIVRES = 1
    EPISODES = 0  # 0 means all
    FILE_OUT_TEMPLATE = "out/narrative_chart_{uid}.htm"
    CASES = {
        # (1, range(1, 11)): '1_1-11',
        # (1, 0): '1-all',
        (0, 0): 'all',
    }
    for (livres, episodes), fuid in CASES.items():
        data = data_module.extract()
        html = make_chart(data, livres=livres, episodes=episodes)
        with open(FILE_OUT_TEMPLATE.format(uid=fuid), 'w') as fd:
            fd.write(html)
