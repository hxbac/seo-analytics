import json

input_file = "articles_with_keywords.jsonl"
output_file = "articles_with_keywords.json"

data = []
with open(input_file, "r", encoding="utf-8") as f_in:
    for line in f_in:
        if line.strip():
            data.append(json.loads(line))

with open(output_file, "w", encoding="utf-8") as f_out:
    json.dump(data, f_out, ensure_ascii=False, indent=2)

print(f"Đã convert {input_file} -> {output_file}, total: {len(data)} articles")
