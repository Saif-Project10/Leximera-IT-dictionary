import json

# Load data.json
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Count total words
total_words = len(data)

# Create word_count.txt
with open('word_count.txt', 'w', encoding='utf-8') as f:
    f.write(f"Total unique words in data.json: {total_words}")

print(f"✅ Total unique words: {total_words}")
print(f"✅ Created: word_count.txt")