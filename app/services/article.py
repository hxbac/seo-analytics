from app.models import Article, Website
from tortoise.expressions import RawSQL
from tortoise.functions import Count


class ArticleService:
    @staticmethod
    async def get_article_by_url(url):
        return await Article.get_or_none(url=url)

    @staticmethod
    async def create_article(data: dict, website: Website):
        article = await Article.get_or_none(url=data["url"])
        if article:
            return article

        return await Article.create(
            url=data.get("url"),
            lastmod=data.get("lastmod"),
            changefreq=data.get("changefreq"),
            title=data.get("title"),
            description=data.get("description"),
            content=data.get("content"),
            headline=data.get("headline"),
            author=data.get("author"),
            datePublished=data.get("datePublished"),
            dateModified=data.get("dateModified"),
            h1=data.get("h1"),
            h2=data.get("h2"),
            word_count=data.get("word_count"),
            image=data.get("image"),
            website=website,
        )

    @staticmethod
    async def create_many(articles: list[dict]):
        objs = [Article(**data) for data in articles]
        return await Article.bulk_create(objs)

    @staticmethod
    async def get_articles_keywords_empty(website_id):
        return await Article.filter(keywords=None, website_id=website_id).all()

    @staticmethod
    async def get_month_has_articles(website_id):
        return await (
            Article.filter(website_id=website_id)
                .annotate(month=RawSQL('TO_CHAR("datePublished", \'YYYY-MM\')'))
                .distinct()
                .order_by('month')
                .values_list('month', flat=True)
        )
