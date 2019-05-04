"""Create a wordcloud over the citations"""

import numpy as np
from PIL import Image
from wordcloud import WordCloud
import data as data_module

IMG_OUT = 'out/wordcloud.png'
IMG_MASK = 'resources/kaamelott-mask.png'
FILE_STOPWORDS = 'resources/stopwords'


def get_citation_texts(data):
    for episodes in data.values():
        for citations in episodes.values():
            yield from (c.text for c in citations)

def get_stop_words():
    with open(FILE_STOPWORDS) as fd:
        for line in fd:
            yield line.strip()


if __name__ == '__main__':
    data = data_module.extract()
    stopwords = set(get_stop_words())
    mask = np.array(Image.open(IMG_MASK))
    text = '\n'.join(get_citation_texts(data)).lower()
    wc = WordCloud(margin=10, stopwords=stopwords, mask=mask).generate(text)
    wc.to_image().save(IMG_OUT)
