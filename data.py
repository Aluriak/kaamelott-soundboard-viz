"""Extraction of citation data"""
import re
import json
from collections import defaultdict, namedtuple


DATAFILE_URL = 'https://raw.githubusercontent.com/2ec0b4/kaamelott-soundboard/master/sounds/sounds.json'
REGEX_INFO = re.compile(r'Livre ([IV]+), ([0-9]+) - (.*)')
LIVRE_NUMBER = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7}
LIVRE_ROMAN = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 'VII': 7}
LIVRE_ORDER = 'I', 'II', 'III', 'IV', 'V', 'VI', 'VI'
LIVRE_ORDER_NUMERAL = tuple(LIVRE_NUMBER[l] for l in LIVRE_ORDER)
Citation = namedtuple('Citation', 'text, characters')


def extract_jsondata_from_web(url=DATAFILE_URL):
    with urllib.request.urlopen(DATAFILE_URL) as fd:
        return json.load(fd)

def extract_jsondata_from_file(fname='resources/sounds.json'):
    with open(fname) as fd:
        return json.load(fd)


def extract_data_from_json(rawjson:list):
    "Return dict mapping season -> episode -> [citations]"
    data = defaultdict(lambda: defaultdict(list))
    for citation in rawjson:
        match = REGEX_INFO.fullmatch(citation['episode'])
        if not match:  continue
        season, number, title = match.groups(0)
        season = LIVRE_NUMBER[season]
        characters = set(citation['character'].split(' - '))
        # if len(characters) > 1 or any(',' in c for c in characters):
            # print(citation, characters)
        data[season][int(number)].append(Citation(citation['title'], characters))
    return {season: {ep: tuple(cits) for ep, cits in sub.items()}
            for season, sub in data.items()}


def extract():
    return extract_data_from_json(extract_jsondata_from_file())

def extract_from_web():
    return extract_data_from_json(extract_jsondata_from_web())


def belongs(data, livre, episode, livres, episodes) -> bool:
    "True if given episode in given livre is expected to be in (livres, episodes) ranges"
    def verify(obj, container) -> bool:
        if container is None or container == 0:
            return True
        elif isinstance(container, int):
            return obj == container
        else:
            assert isinstance(container, (list, tuple, set, range)), (type(container), container)
            return obj in container
        return False
    exists = livre in data and episode in data[livre]
    return verify(livre, livres) and verify(episode, episodes) and exists


if __name__ == '__main__':
    from pprint import pprint
    pprint(extract())
