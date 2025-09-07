from rake_nltk import Rake
from stop_words import get_stop_words
# from elasticsearch import Elasticsearch, helpers
import json
import re

from keybert import KeyBERT
from underthesea import word_tokenize

# import nltk
# nltk.download("popular")
# nltk.download('punkt_tab')

vietnamese_stopwords = get_stop_words("vietnamese")


with open("articles.json", "r", encoding="utf-8") as f:
    articles = json.load(f)


def extract_keywords(content: str, n: int = 5):
    # content_tokens = word_tokenize(content, format="text")

    kw_model = KeyBERT("sentence-transformers/all-MiniLM-L6-v2")

    keywords = kw_model.extract_keywords(
        content,
        keyphrase_ngram_range=(1, 3),
        stop_words=vietnamese_stopwords,
        top_n=n,
        use_mmr=True,   # đa dạng hóa
        diversity=0.7
    )

    return [kw[0] for kw in keywords]

article = articles[0]

# print(article["content"])
keywords = extract_keywords(article["content"], n=5)
print("Từ khóa chính:", keywords)
