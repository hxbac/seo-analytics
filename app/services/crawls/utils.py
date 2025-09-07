from bs4 import BeautifulSoup
import re
import requests
import json

def extract_title(soup: BeautifulSoup):
    tag = soup.find("title")
    return tag.text.strip() if tag else None


def extract_meta_description(soup: BeautifulSoup):
    tag = soup.find("meta", attrs={"name": "description"})
    return tag["content"].strip() if tag and tag.get("content") else None

def extract_keywords(soup: BeautifulSoup):
    tag = soup.find("meta", attrs={"name": "keywords"})
    if tag and tag.get("content"):
        content = tag["content"]
        return [kw.strip() for kw in content.split(",") if kw.strip()]
    return []

def extract_word_count(text: str):
    if not text:
        return 0
    words = re.findall(r'\w+', text)
    return len(words)

def extract_h1(soup: BeautifulSoup):
    h1_tag = soup.find("h1")
    return h1_tag.get_text(strip=True) if h1_tag else None

def extract_keywords_by_ai(prompt, model="qwen2:7b-instruct-q4_0", keywords=None):
    url = "http://localhost:11434/api/generate"

    resp = requests.post(url, json={
        "model": model,
        "prompt": prompt,
        "stream": False
    })

    data = resp.json()
    text = data["response"]

    try:
        start = text.find("[")
        end = text.rfind("]")

        extracted = text[start:end+1]
        keywords = json.loads(extracted)
    except:
        keywords = None

    return keywords
