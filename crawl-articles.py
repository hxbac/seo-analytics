import requests
from bs4 import BeautifulSoup
import json
import time
import re
from fake_useragent import UserAgent


def extract_h1(soup: BeautifulSoup):
    h1_tag = soup.find("h1")
    return h1_tag.get_text(strip=True) if h1_tag else None


def extract_h2(soup: BeautifulSoup):
    return [h2.get_text(strip=True) for h2 in soup.find_all("h2")]


def extract_word_count(text: str):
    if not text:
        return 0
    words = re.findall(r'\w+', text)
    return len(words)


def extract_title(soup: BeautifulSoup):
    tag = soup.find("title")
    return tag.text.strip() if tag else None


def extract_meta_description(soup: BeautifulSoup):
    tag = soup.find("meta", attrs={"name": "description"})
    return tag["content"].strip() if tag and tag.get("content") else None


def extract_json_ld(soup: BeautifulSoup):
    headline, publish_date, modified_date, author_name, image_url = None, None, None, None, None

    ld_json_list = soup.find_all("script", type="application/ld+json")
    for ld_json in ld_json_list:
        try:
            ld_data = json.loads(ld_json.string)

            if isinstance(ld_data, list):
                for item in ld_data:
                    if isinstance(item, dict) and item.get("@type") == "Article":
                        headline = item.get("headline")
                        publish_date = item.get("datePublished")
                        modified_date = item.get("dateModified")
                        if "author" in item and isinstance(item["author"], dict):
                            author_name = item["author"].get("name")
                        image_url = item.get("image")
            elif isinstance(ld_data, dict) and ld_data.get("@type") == "Article":
                headline = ld_data.get("headline")
                publish_date = ld_data.get("datePublished")
                modified_date = ld_data.get("dateModified")
                if "author" in ld_data and isinstance(ld_data["author"], dict):
                    author_name = ld_data["author"].get("name")
                image_url = ld_data.get("image")

        except Exception as e:
            print(f"⚠️ Lỗi parse JSON-LD: {e}")

    return headline, publish_date, modified_date, author_name, image_url


def crawl_sitemap_and_articles(sitemap_url, limit=100, output_file="articles.json"):
    ua = UserAgent()

    headers = {"User-Agent": ua.random}
    r = requests.get(sitemap_url, headers=headers)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "xml")
    urls = soup.find_all("url")

    data = []
    for i, url in enumerate(urls[:limit]):
        loc = url.find("loc").text if url.find("loc") else None
        lastmod = url.find("lastmod").text if url.find("lastmod") else None
        changefreq = url.find("changefreq").text if url.find("changefreq") else None

        headers = {"User-Agent": ua.random}
        try:
            res = requests.get(loc, headers=headers, timeout=10)
            res.raise_for_status()
            page = BeautifulSoup(res.text, "html.parser")

            title = extract_title(page)
            meta_desc = extract_meta_description(page)

            body_text = None
            rte_tag = page.find("div", class_="article-body")
            if rte_tag:
                body_text = rte_tag.get_text(" ", strip=True)

            headline, publish_date, modified_date, author_name, image_url = extract_json_ld(page)

        except Exception as e:
            print(f"[{i+1}] ❌ Lỗi crawl {loc}: {e}")
            title, meta_desc, body_text = None, None, None
            headline, publish_date, modified_date, author_name, image_url = None, None, None, None, None

        data.append({
            "url": loc,
            "lastmod": lastmod,
            "changefreq": changefreq,
            "title": title,
            "description": meta_desc,
            "content": body_text,
            "headline": headline,
            "author": author_name,
            "datePublished": publish_date,
            "dateModified": modified_date,
            "h1": extract_h1(page),
            "h2": extract_h2(page),
            "word_count": extract_word_count(body_text),
            "image": image_url,
        })

        print(f"[{i+1}] ✅ Collected: {loc}")

        time.sleep(0.5)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"\n✅ Đã lưu {len(data)} article vào {output_file}")


sitemap_url = "https://goya.vn/sitemap_blogs_1.xml"
crawl_sitemap_and_articles(sitemap_url, 500)
