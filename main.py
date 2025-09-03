from stop_words import get_stop_words
from elasticsearch import Elasticsearch, helpers
import json
import re

vietnamese_stopwords = set(get_stop_words("vietnamese"))
es = Elasticsearch(["http://localhost:9200"])

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9à-ỹ\s]", " ", text)
    tokens = text.split()
    tokens = [t for t in tokens if t not in vietnamese_stopwords and len(t) > 2]
    return " ".join(tokens)

def extract_keywords(*texts) -> list:
    """Trích từ khóa từ title + h1 + content"""
    combined = " ".join([t for t in texts if t])
    if not combined:
        return []
    combined = combined.lower()
    combined = re.sub(r"[^a-zA-Z0-9à-ỹ\s]", " ", combined)
    tokens = combined.split()
    return [t for t in tokens if t not in vietnamese_stopwords and len(t) > 2]



INDEX_NAME = "articles"

es.indices.delete(index=INDEX_NAME, ignore=[400, 404])
mapping = {
    "mappings": {
        "properties": {
            "url": {"type": "keyword"},
            "title": {"type": "text"},
            "description": {"type": "text"},
            "content": {"type": "text"},
            "h1": {"type": "text"},
            "author": {"type": "keyword"},
            "datePublished": {"type": "date"},
            "dateModified": {"type": "date"},
            "lastmod": {"type": "date"},
            "word_count": {"type": "integer"},
            "image": {"type": "keyword"},
            "keywords": {"type": "keyword"}
        }
    }
}
es.indices.create(index=INDEX_NAME, body=mapping)


with open("articles.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

actions = []
for art in articles:
    title = art.get("title", "")
    h1 = " ".join(art.get("h1", [])) if isinstance(art.get("h1"), list) else art.get("h1", "")
    content = art.get("content", "")

    doc = {
        "_index": INDEX_NAME,
        "_source": {
            "url": art.get("url"),
            "title": clean_text(title),
            "description": clean_text(art.get("description", "")),
            "content": clean_text(content),
            "h1": clean_text(h1),
            "author": art.get("author"),
            "datePublished": art.get("datePublished"),
            "dateModified": art.get("dateModified"),
            "lastmod": art.get("lastmod"),
            "word_count": art.get("word_count"),
            "image": art.get("image"),
            "keywords": extract_keywords(title, h1, content)
        }
    }
    actions.append(doc)

helpers.bulk(es, actions)
print(f"Indexed {len(actions)} articles into {INDEX_NAME}")
