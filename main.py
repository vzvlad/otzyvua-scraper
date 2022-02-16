"""
For every bigram and trigram of PoS, retrieves its occurence frequency. Splitting into n-grams and calculating
distribution - via nltk.corpus and nltk.probability
"""

import nltk
from tqdm import tqdm

from pos_tagger import pos_tags

with open('reviews/uk.txt', 'r', encoding='utf-8') as inp:
    reviews_raw = [line.rstrip() for line in inp]

ngrams = {2: [], 3: []}
failures_counter = 0

for review in tqdm(reviews_raw, position=0, leave=True):
    try:
        review_tags = pos_tags(review)
        for N in [2, 3]:
            ngrams[N].extend(nltk.ngrams(pos_tags(review), N))
    except UnicodeEncodeError:
        failures_counter += 1
    except Exception:
        pass

print(f"Warning: {failures_counter} reviews were not tagged due to encoding problems")

for N in [2, 3]:
    fdist = nltk.FreqDist(ngrams[N])
    total = fdist.N()
    print(f"{N}-grams")
    for ngram, n_occurrences in fdist.most_common(20):
        print(f"{(n_occurrences / total * 100): .2f}% {ngram}")
    print()
