import json
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("keepitreal/vietnamese-sbert")

def semantic_deduplicate_embeddings(keywords, threshold=0.8):
    result = []
    seen_embeddings = []

    for kw, score in keywords:
        emb = model.encode(kw, convert_to_tensor=True)
        is_duplicate = False
        for seen_kw, seen_emb in seen_embeddings:
            sim = util.cos_sim(emb, seen_emb).item()
            if sim >= threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            result.append((kw, score))
            seen_embeddings.append((kw, emb))
    return result


def clean_articles_keywords(articles, threshold=0.8):
    cleaned_articles = []
    for idx, article in enumerate(articles, start=1):
        try:
            raw_keywords = article.get("keywords", [])
            if raw_keywords:
                cleaned_keywords = semantic_deduplicate_embeddings(raw_keywords, threshold=threshold)
                article["keywords_cleaned"] = cleaned_keywords
            else:
                article["keywords_cleaned"] = []
            cleaned_articles.append(article)
            print(f"[{idx}] ✅ Cleaned {len(raw_keywords)} → {len(article['keywords_cleaned'])} keywords")
        except Exception as e:
            article["keywords_cleaned"] = []
            cleaned_articles.append(article)
            print(f"[{idx}] ❌ Lỗi khi xử lý article {article.get('url')}: {e}")
    return cleaned_articles


if __name__ == "__main__":
    with open("articles_with_keywords_v2.json", "r", encoding="utf-8") as f:
        articles = json.load(f)

    cleaned = clean_articles_keywords(articles, threshold=0.8)

    with open("articles_with_keywords_cleaned.json", "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    print("✅ Đã tạo file articles_with_keywords_cleaned.json")
