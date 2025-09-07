import json
import os
from app.models import Website, Article

async def export_to_json():
    os.makedirs("db", exist_ok=True)

    # Export Website
    websites = await Website.all()
    websites_list = []
    for w in websites:
        websites_list.append({
            "id": w.id,
            "name": w.name,
            "url": w.url,
        })

    with open("db/websites.json", "w", encoding="utf-8") as f:
        json.dump(websites_list, f, ensure_ascii=False, indent=4)

    for w in websites:
        articles = await Article.filter(website_id=w.id)
        articles_list = []
        for a in articles:
            articles_list.append({
                "id": a.id,
                "url": a.url,
                "lastmod": a.lastmod.isoformat() if a.lastmod else None,
                "changefreq": a.changefreq,
                "title": a.title,
                "description": a.description,
                "content": a.content,
                "headline": a.headline,
                "author": a.author,
                "datePublished": a.datePublished.isoformat() if a.datePublished else None,
                "dateModified": a.dateModified.isoformat() if a.dateModified else None,
                "h1": a.h1,
                "h2": a.h2,
                "word_count": a.word_count,
                "image": a.image,
                "keywords": a.keywords,
                "additional_attributes": a.additional_attributes,
                "website_id": a.website_id
            })

        file_path = os.path.join(f"db/articles_{w.id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(articles_list, f, ensure_ascii=False, indent=4)
