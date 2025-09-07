from app.models import Website

class WebsiteService:

    @staticmethod
    async def create_website(name: str, url: str):
        website = await Website.get_or_none(url=url)
        if website:
            return website
        return await Website.create(name=name, url=url)
