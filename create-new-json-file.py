import json

with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)  # data is a LIST of objects

first_20 = data[:20]  # First 20 objects from list

with open('blank.json', 'w', encoding='utf-8') as f:
    json.dump(first_20, f, indent=2, ensure_ascii=False)