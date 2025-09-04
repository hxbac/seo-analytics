import json
from keybert import KeyBERT
from transformers import AutoModel, AutoTokenizer
from stop_words import get_stop_words
from underthesea import word_tokenize, pos_tag
import re
import yake
from rapidfuzz import fuzz

vietnamese_stopwords = set(get_stop_words("vietnamese"))

with open("articles.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

def deduplicate_keywords(keywords, threshold=80):
    result = []
    for kw, score in sorted(keywords, key=lambda x: (-len(x[0]), x[1])):
        is_duplicate = False
        for existing_kw, _ in result:
            if kw in existing_kw or existing_kw in kw:
                is_duplicate = True
                break
            if fuzz.ratio(kw, existing_kw) > threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            result.append((kw, score))
    return result

def remove_stopwords(text: str) -> str:
    words = re.findall(r'\w+', text.lower(), flags=re.UNICODE)

    filtered_words = [w for w in words if w not in vietnamese_stopwords]

    return " ".join(filtered_words)

def filter_noun_phrases(keywords):
    result = []
    for kw, score in keywords:
        tags = pos_tag(kw)
        if any(tag[1] in ["N", "Np", "Nc"] for tag in tags):
            result.append((kw, score))
    return result

def semantic_deduplicate(keywords, threshold=80):
    result = []
    for kw, score in keywords:
        is_duplicate = False
        for existing_kw, _ in result:
            if fuzz.partial_ratio(kw, existing_kw) > threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            result.append((kw, score))
    return result



    # kw_extractor = yake.KeywordExtractor(
    #     lan="vi",
    #     n=ngram[1],
    #     top=n*5,
    #     features=None
    # )

    # raw_keywords = kw_extractor.extract_keywords(content)
    # keywords = [(kw, score) for kw, score in raw_keywords]

def extract_keywords(content: str, n: int = 10, ngram=(1,3)):
    cleaned_content = remove_stopwords(content)

    all_keywords = []

    for size in range(ngram[0], ngram[1] + 1):
        kw_extractor = yake.KeywordExtractor(
            lan="vi",
            n=size,
            top=n*5,
            features=None
        )
        raw_keywords = kw_extractor.extract_keywords(content)
        all_keywords.extend([(kw, score) for kw, score in raw_keywords])


    keywords = filter_noun_phrases(all_keywords)
    keywords = deduplicate_keywords(keywords)
    keywords = semantic_deduplicate(keywords)

    keywords = sorted(keywords, key=lambda x: x[1])

    return keywords[:n], cleaned_content

articles_with_keywords = []
for idx, article in enumerate(articles, start=1):
    try:
        content = article.get("content") or article.get("headline", "")
        kws, cleaned = extract_keywords(content, n=20)
        article["keywords"] = kws
        article["cleaned_content"] = cleaned
    except Exception as e:
        article["keywords"] = []
        article["cleaned_content"] = ""
        print(f"Lỗi khi xử lý article {article.get('url')}: {e}")

    articles_with_keywords.append(article)
    print(f"[{idx}] ✅ Xử lý thành công: {article.get('url')}")

with open("articles_with_keywords_v2.json", "w", encoding="utf-8") as f:
    json.dump(articles_with_keywords, f, ensure_ascii=False, indent=2)

print("✅ Đã tạo file articles_with_keywords.json")
