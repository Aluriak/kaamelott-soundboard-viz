"""Generation of an interaction graph over the characters.

Two characters interacts when appearing in the same episode.

TODO someday: generate interactive visualization with networkx
and a javascript lib such as cytoscape.js.

"""

import biseau as bs
import itertools
import data as data_module
from collections import defaultdict

FILE_OUT_DOT = 'out/interaction-graph.dot'
FILE_OUT = 'out/interaction-graph.png'


def yield_characters_per_episode() -> [set]:
    "Yield set of characters belonging to the same episode"
    data = data_module.extract()
    for season, episodes in data.items():
        for episode, citations in episodes.items():
            yield set(itertools.chain.from_iterable(characters for _, characters in citations))

def get_characters_interactions() -> {(str, str): int}:
    "Return mapping {(char1, char2): number of episodes in common}"
    links = defaultdict(int)
    for characters in yield_characters_per_episode():
        for chars in itertools.combinations(characters, r=2):
            assert len(set(chars)) == len(chars) == 2, chars
            one, two = min(chars), max(chars)
            links[one, two] += 1
    return dict(links)


def get_nx_interaction_graph():
    "Return nx.Graph that encodes the interaction graph"
    import networkx as nx
    graph = nx.Graph()
    for (one, two), nb_interaction in get_characters_interactions().items():
        graph.add_edge(one, two, penwidth=nb_interaction)  # penwidth is for dot
    return graph


def biseau_encoding_of_interactions():
    "Return ASP that encodes the interaction graph for biseau"
    asp_code = """
    link(C,D) :- share(C,D,_).
    dot_property(C,D,penwidth,N) :- share(C,D,N).
    obj_property(graph,bgcolor,black).
    obj_property(edge,(fontcolor;color),white).
    obj_property(node,(fontcolor;color),white).
    obj_property(edge,arrowhead,none).
    """
    def gen_data():
        for (one, two), nb_interaction in get_characters_interactions().items():
            yield f'share("{one}","{two}",{nb_interaction}).'
    return asp_code + ' '.join(gen_data())


use_nx = False
if use_nx:
    from networkx.drawing.nx_agraph import write_dot
    graph = get_nx_interaction_graph()
    write_dot(graph, FILE_OUT_DOT)
else:
    asp = biseau_encoding_of_interactions()
    bs.compile_to_single_image(asp, outfile=FILE_OUT, dotfile=FILE_OUT_DOT)
