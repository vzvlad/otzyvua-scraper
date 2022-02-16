import re
import nltk

from ukrainian_pos_tagger.tagger import Tagger


def tokenize(text):
    text = re.sub(r"""['’"`�]""", '', text)
    text = re.sub(r"""([0-9])([\u0400-\u04FF]|[A-z])""", r"\1 \2", text)
    text = re.sub(r"""([\u0400-\u04FF]|[A-z])([0-9])""", r"\1 \2", text)
    text = re.sub(r"""[\-.,:+*/_]""", ' ', text)
    return [word.lower() if word.isalpha() else word for word in nltk.word_tokenize(text)]


def pos_tags(text):
    tagger = Tagger(tokenize(text))
    tagger.label_data()
    return [tags[0] for tags in tagger.predicted_tags]
