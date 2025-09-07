import json
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from datetime import datetime


model = SentenceTransformer("keepitreal/vietnamese-sbert")


def group_semantic_keywords(keywords, distance_threshold=0.6):
    if not keywords:
        return {}, None

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

    return clusters, embeddings


def get_cluster_representative(kws, embeddings, scores):
    idxs = [i for i, _ in enumerate(kws)]
    cluster_emb = embeddings[idxs]
    centroid = cluster_emb.mean(axis=0)

    sims = np.dot(cluster_emb, centroid) / (
        np.linalg.norm(cluster_emb, axis=1) * np.linalg.norm(centroid)
    )
    best_idx = int(np.argmax(sims))
    return kws[best_idx], scores[best_idx]


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
        for kw, score in art.get("keywords_cleaned", []):
            rows.append({"month": month, "keyword": kw, "score": score})

    df = pd.DataFrame(rows)

    monthly_clusters = {}
    for month, group in df.groupby("month"):
        keywords = group["keyword"].tolist()
        scores = group["score"].tolist()

        clusters, embeddings = group_semantic_keywords(keywords)
        if embeddings is None:
            continue

        cluster_summary = []
        for cid, kws in clusters.items():
            sub_df = group[group["keyword"].isin(kws)]
            sub_scores = sub_df["score"].tolist()

            rep_kw, rep_score = get_cluster_representative(kws, embeddings, sub_scores)

            cluster_summary.append({
                "cluster_id": int(cid),
                "keywords": kws,
                "representative": rep_kw,
                "score": float(rep_score),
                "keyword_count": len(kws),
            })

        cluster_summary = sorted(cluster_summary, key=lambda x: x["score"], reverse=True)[:top_n]
        monthly_clusters[month] = cluster_summary

    return monthly_clusters


if __name__ == "__main__":
    with open("articles_with_keywords_cleaned.json", "r", encoding="utf-8") as f:
        articles = json.load(f)

    clusters_by_month = process_articles(articles, top_n=20)

    with open("clustered_keywords_top_month_v3.json", "w", encoding="utf-8") as f:
        json.dump(clusters_by_month, f, ensure_ascii=False, indent=2)

    print("✅ Exported clustered_keywords_top_month_v3.json")
