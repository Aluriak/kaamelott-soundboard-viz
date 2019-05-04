"""Associate for each sound file (sounds/*.mp3) a human & shortened
version garantueed unique accross all sound files.

"""

import os
import glob
import clyngor
from collections import defaultdict

MAX_SEARCH_TIME = 30  # (seconds)  avoid < 10
SHOW_CHOICES = True  # set to False to prevent useless lines

def get_words_per_file():
    for idx, fname in enumerate(glob.glob("sounds/*.mp3"), start=1):
        fname = os.path.basename(os.path.splitext(fname)[0])
        words = fname.replace('-', '_').split("_")
        yield fname, tuple(words)
    print(f'{idx} files found in sounds/*.mp3')


def atoms_from_words(words: tuple) -> [str]:
    "Yield ASP atoms describing given words"
    sep = '";"'
    for idx, (_, words) in enumerate(words):
        yield from f'word({idx},("{sep.join(words)}")).'


def get_selected_words(words: tuple) -> tuple:
    "Return tuple fname, words, shortened words"
    atoms = "".join(atoms_from_words(words))
    models = clyngor.solve("shortener.lp", inline=atoms, options=f'--parallel-mode=4 --time-limit={MAX_SEARCH_TIME}').by_predicate
    model = None
    for model in models:
        pass  # just get the last (which is the optimal) model
    shortened_words = defaultdict(set)  # idx: words
    for idx, word in model["selword"]:
        shortened_words[idx].add(word.strip('"'))
    for idx, assoc_words in shortened_words.items():
        fname, initial_words = words[idx]
        yield fname, initial_words, tuple(w for w in initial_words if w in assoc_words)


def words_with_specific(words: tuple) -> dict:
    "Yield pairs (fname, specific)"
    word_to_fnames = defaultdict(set)  # word: set of fname
    for fname, assoc_words in words:
        for word in assoc_words:
            word_to_fnames[word].add(fname)
    specifics = defaultdict(set)  # fname -> specific words
    for word, fnames in word_to_fnames.items():
        if len(fnames) == 1:
            specifics[next(iter(fnames))].add(word)
    for fname, assoc_words in specifics.items():
        # TODO: allow to choose depending of other metrics (min, letter surreprensation,…)
        many_choices = len(assoc_words) > 1
        if SHOW_CHOICES and many_choices:
            print(f"file {fname} associated with {len(assoc_words)} words: {', '.join(assoc_words)}. ", end='')
        if any('z' in w for w in assoc_words):  # prefer words with a 'z' inside
            assoc_words = (w for w in assoc_words if 'z' in w)
        chosen = max(assoc_words, key=len)
        if SHOW_CHOICES and many_choices:
            print(f"{chosen} was chosen.")
        yield fname, chosen


def precompute_shortened_words(words: tuple) -> tuple:
    """Wrapper around get_selected_words(), yielding (fname, shortened words).

    Improves efficiency by pre-shorten filenames with specific words in it.

    """
    specifics = dict(words_with_specific(words))
    for fname, assoc_words in words:
        if fname in specifics:
            yield fname, assoc_words, (specifics[fname],)
    to_select_fnames = tuple((f, w) for f, w in words if f not in specifics)
    for fname, assoc_words, shortened_words in get_selected_words(to_select_fnames):
        yield fname, assoc_words, shortened_words


def validate_words(words: tuple) -> None or ValueError:
    # verify doublons
    all_words = {}
    for fname, assoc_words in words:
        if assoc_words in all_words:
            raise ValueError(
                f"DOUBLON: {assoc_words} from {fname} is already associated with {all_words[assoc_words]}"
            )
        all_words[assoc_words] = fname


if __name__ == "__main__":
    words = tuple(get_words_per_file())
    validate_words(words)
    for fname, initial_words, words in precompute_shortened_words(words):
        new_fname = '_'.join(words) + '.mp3'
        print(f'    {fname.rjust(50)}.mp3    ->    {new_fname}')
        # print(f"{initial_words}".rjust(40), "->", f"{words}")
