# import json
# from keybert import KeyBERT
# from transformers import AutoModel, AutoTokenizer
# from stop_words import get_stop_words
# from underthesea import word_tokenize

# with open("articles.json", "r", encoding="utf-8") as f:
#     articles = json.load(f)

# vietnamese_stopwords = set(get_stop_words("vietnamese"))

# phobert_model = AutoModel.from_pretrained("vinai/phobert-base")
# phobert_tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base")

# kw_model = KeyBERT(model=phobert_model)

# def remove_stopwords(text: str) -> str:
#     tokens = word_tokenize(text, format="text").split()
#     filtered = [t for t in tokens if t.lower() not in vietnamese_stopwords]
#     return " ".join(filtered)

# def extract_keywords(content: str, n: int = 5):
#     cleaned_content = remove_stopwords(content)
#     keywords = kw_model.extract_keywords(
#         cleaned_content,
#         keyphrase_ngram_range=(2, 5),
#         top_n=n,
#         use_maxsum=True,
#         diversity=0.7
#     )
#     return [kw[0].replace("_", " ") for kw in keywords], cleaned_content

# articles_with_keywords = []
# for article in articles:
#     try:
#         kws, content_stop_words = extract_keywords(article.get("content", ""), n=5)
#     except Exception as e:
#         kws = []
#         print(f"Lỗi khi xử lý article: {e}")
#     article["keywords"] = kws
#     articles_with_keywords.append(article)

# with open("articles_with_keywords.json", "w", encoding="utf-8") as f:
#     json.dump(articles_with_keywords, f, ensure_ascii=False, indent=2)

# print("✅ Đã tạo file articles_with_keywords.json")





import json
from keybert import KeyBERT
from transformers import AutoModel, AutoTokenizer
from stop_words import get_stop_words
from underthesea import word_tokenize
import re

with open("articles.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

def load_stopwords(filepath=r"utils/vietnamese-stopwords.txt"):
    with open(filepath, "r", encoding="utf-8") as f:
        return set(line.strip().lower() for line in f if line.strip())

custom_stopwords = load_stopwords()

phobert_model = AutoModel.from_pretrained("vinai/phobert-base")
phobert_tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base")
kw_model = KeyBERT(model=phobert_model)

def remove_stopwords(text: str) -> str:
    tokens = word_tokenize(text, format="text").split()

    filtered = [t for t in tokens if t.lower() not in custom_stopwords and t.isalpha()]
    cleaned = " ".join(filtered)

    for sw in sorted(custom_stopwords, key=lambda x: len(x.split()), reverse=True):
        pattern = r"\b" + re.escape(sw) + r"\b"
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned

def extract_keywords(content: str, n: int = 10, ngram=(1,3)):
    cleaned_content = remove_stopwords(content)
    print(cleaned_content)
    keywords = kw_model.extract_keywords(
        cleaned_content,
        keyphrase_ngram_range=ngram,
        top_n=n,
        use_maxsum=True,
        diversity=0.7
    )
    return [(kw[0].replace("_", " "), kw[1]) for kw in keywords], cleaned_content

# article = articles[0]
# content = article.get("content") or article.get("headline", "")
# kws, cleaned = extract_keywords(content)

articles_with_keywords = []
for idx, article in enumerate(articles, start=1):
    try:
        content = article.get("content") or article.get("headline", "")
        kws, cleaned = extract_keywords(content)
        article["keywords"] = kws
        article["cleaned_content"] = cleaned
    except Exception as e:
        article["keywords"] = []
        article["cleaned_content"] = ""
        print(f"Lỗi khi xử lý article {article.get('url')}: {e}")

    articles_with_keywords.append(article)
    print(f"[{idx}] ✅ Xử lý thành công: {article.get('url')}")

with open("articles_with_keywords.json", "w", encoding="utf-8") as f:
    json.dump(articles_with_keywords, f, ensure_ascii=False, indent=2)

print("✅ Đã tạo file articles_with_keywords.json")
