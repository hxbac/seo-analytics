import asyncio
from tortoise import Tortoise, run_async
from app.config import TORTOISE_ORM
import argparse
from app.state import GlobalState
from app.services.website import WebsiteService
from app.export import *

from app.services.crawls.stavi import StaviService


def get_crawl_service():
    match GlobalState.website.id:
        case 1:
            return StaviService
        case _:
            raise Exception("Crawler not found")

async def run(args):
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    if args.export:
        await export_to_json()
        await Tortoise.close_connections()
        return

    website = None
    if args.url:
        website = await WebsiteService.create_website(args.name, args.url)

    if not website:
        await Tortoise.close_connections()
        raise Exception("Website not found")

    GlobalState.website = website

    crawl_service = get_crawl_service()
    if args.crawl_articles:
        await crawl_service.crawl_articles()

    if args.process_keywords:
        await crawl_service.process_keywords()

    if args.extract_top_keywords:
        await crawl_service.extract_top_keywords()

    await Tortoise.close_connections()

    print("✅ Exit")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--add", action="store_true", help="Add new website")
    parser.add_argument("--name", type=str, help="Website name")
    parser.add_argument("--url", type=str, help="Website url")
    parser.add_argument("--crawl_articles", action="store_true")
    parser.add_argument("--process_keywords", action="store_true")
    parser.add_argument("--extract_top_keywords", action="store_true")
    parser.add_argument("--export", action="store_true")
    args = parser.parse_args()

    run_async(run(args))
