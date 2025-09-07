from app.state import GlobalState
from fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup
from .utils import *
from datetime import datetime
from tqdm import tqdm
import time

from ..article import ArticleService

ua = UserAgent()

class StaviService:
    @staticmethod
    def crawl_articles_link():
        article_page_url = 'https://stavi.com.vn/vi/tin-tuc'
        all_links = []
        page = 1

        while True:
            headers = {"User-Agent": ua.random}
            r = requests.get(article_page_url, headers=headers, params={"page": page})
            r.raise_for_status()

            soup = BeautifulSoup(r.text, "html.parser")
            section = soup.select_one(".section-body.news")

            if not section:
                print("❌ Không tìm thấy section-body.news -> dừng")
                break

            links = []
            for li in section.select("ul:not(.pagination) li.item"):
                a = li.select_one("h3 a")
                if not a:
                    continue

                href = a.get("href")
                if href and href.startswith("https://stavi.com.vn/vi/tin-tuc"):
                    date_tag = li.select_one("._date")
                    date_published = None
                    if date_tag:
                        raw_date = date_tag.get_text(strip=True)
                        try:
                            # parse dd/MM/YYYY
                            date_published = datetime.strptime(raw_date, "%d/%m/%Y").date()
                        except ValueError:
                            print(f"⚠️ Không parse được ngày: {raw_date}")

                    links.append({"href": href, "date_published": date_published})

            if not links:
                print("❌ Không tìm thấy link nào -> dừng")
                break

            if len(links) < 12:
                print(f"⚠️ Page {page} chỉ có {len(links)} links (<12)")

            all_links.extend(links)
            page += 1

        print(f"✅ Tổng số link thu thập được: {len(all_links)}")
        return all_links

    @staticmethod
    async def process_article(link):
        article = await ArticleService.get_article_by_url(link)
        if article:
            return None

        headers = {"User-Agent": ua.random}
        try:
            res = requests.get(link, headers=headers, timeout=10)
            res.raise_for_status()
            page = BeautifulSoup(res.text, "html.parser")

            title = extract_title(page)
            meta_desc = extract_meta_description(page)
            keywords = extract_keywords(page)
            h1 = extract_h1(page)

            body_text = None
            rte_tag = page.find("section", class_="news-view")
            if rte_tag:
                body_text = rte_tag.get_text(" ", strip=True)

        except Exception as e:
            print(f"[] ❌ Lỗi crawl:", link, e)
            return None

        return {
            "url": link,
            "title": title,
            "description": meta_desc,
            "content": body_text,
            "h1": h1,
            "word_count": extract_word_count(body_text),
            "additional_attributes": {
                "keywords": keywords,
            }
        }

    @staticmethod
    async def crawl_articles():
        all_links = StaviService.crawl_articles_link()

        articles = []
        for link in tqdm(all_links, desc="📥 Crawling articles"):
            article = await StaviService.process_article(link["href"])

            if article is None:
                continue

            time.sleep(0.3)
            article["website_id"] = GlobalState.website.id
            article["datePublished"] = link["date_published"]
            articles.append(article)

        if articles:
            await ArticleService.create_many(articles)
            print(f"Created {len(articles)} articles")

    @staticmethod
    async def process_keywords():
        articles = await ArticleService.get_articles_keywords_empty(GlobalState.website.id)
        for article in tqdm(articles, desc="📥 Extract keywords"):

            keywords = article.additional_attributes.get("keywords")
            content = article.content or article.description or article.title

            prompt = f"""
            Hãy trích xuất tối đa 10 từ khóa quan trọng nhất, sắp xếp theo mức độ liên quan đến nội dung.
            - Mỗi từ khóa nên khác nhau, không trùng lặp, không quá dài.
            - Ưu tiên những từ khóa có ý nghĩa SEO.
            - Đầu vào gồm có nội dung bài viết và danh sách keywords SEO gợi ý.

            Kết quả chỉ trả về JSON array (danh sách string từ khóa), không thêm bất kỳ văn bản nào khác.

            keywords: {keywords}

            Content: {content}
            """

            keywords_extracted = extract_keywords_by_ai(prompt)

            if not keywords_extracted:
                continue

            article.keywords = keywords_extracted
            await article.save()

    @staticmethod
    async def extract_top_keywords():
        months = await ArticleService.get_month_has_articles(GlobalState.website.id)

        print((months))

        # for r in months:
        #     month_str = r.month.strftime("%Y-%m")
        #     print(month_str, r.total_articles)
