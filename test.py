import requests
import json

def extract_keywords(text, model="qwen2:7b-instruct-q4_0"):
    url = "http://localhost:11434/api/generate"
    prompt = f"Hãy trích xuất tối đa 10 từ khóa sắp xếp theo thứ tự quan trọng từ đoạn văn sau và trả về dưới dạng array json string của các từ khóa. Lưu ý, không giải thích gì thêm, các từ khóa không nên quá dài. Nội dung:\n\n{text}"

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
        keywords = data["response"]

    return keywords


with open("articles.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

output_file = "articles_with_keywords.jsonl"

with open(output_file, "w", encoding="utf-8") as f_out:
    for idx, article in enumerate(articles, start=1):
        content = article.get("content") or article.get("headline", "")
        if content:
            try:
                kws = extract_keywords(content)
                article["keywords"] = kws
                print(f"[{idx}] ✅ {len(kws)} keywords")
            except Exception as e:
                article["keywords"] = []
                print(f"[{idx}] ❌ Lỗi: {e}")
        else:
            article["keywords"] = []

        f_out.write(json.dumps(article, ensure_ascii=False) + "\n")
        f_out.flush()
