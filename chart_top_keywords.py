import json
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from datetime import datetime


def group_semantic_keywords(keywords, distance_threshold=1.3):
    if not keywords:
        return {}

    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    embeddings = model.encode(keywords)

    clustering = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=distance_threshold,
        metric="cosine",
        linkage="average"
    )
    labels = clustering.fit_predict(embeddings)

    clusters = {}
    for kw, label in zip(keywords, labels):
        clusters.setdefault(label, []).append(kw)

    return clusters

def parse_date_safe(date_str):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(str(date_str))
    except ValueError:
        try:
            return datetime.strptime(str(date_str), "%Y-%m-%d")
        except Exception:
            return None

def process_articles(articles, top_n=10):
    rows = []

    for art in articles:
        date = parse_date_safe(art.get("datePublished"))
        if not date:
            continue

        month = date.strftime("%Y-%m")
        for kw, score in art.get("keywords", []):
            rows.append({"month": month, "keyword": kw, "score": score})

    df = pd.DataFrame(rows)

    monthly_clusters = {}
    for month, group in df.groupby("month"):
        keywords = group["keyword"].tolist()

        clusters = group_semantic_keywords(keywords)

        cluster_summary = []
        for cid, kws in clusters.items():
            rep_kw = (
                group[group["keyword"].isin(kws)]
                .sort_values("score", ascending=True)
                .iloc[0]["keyword"]
            )
            cluster_summary.append({
                "cluster_id": int(cid),
                "keywords": kws,
                "representative": rep_kw
            })

        cluster_summary = sorted(cluster_summary, key=lambda x: -len(x["keywords"]))[:top_n]
        monthly_clusters[month] = cluster_summary

    return monthly_clusters


if __name__ == "__main__":
    with open("articles_with_keywords_v2.json", "r", encoding="utf-8") as f:
        articles = json.load(f)

    clusters_by_month = process_articles(articles)

    with open("clustered_keywords.json", "w", encoding="utf-8") as f:
        json.dump(clusters_by_month, f, ensure_ascii=False, indent=2)

    print("✅ Exported clustered_keywords.json")
