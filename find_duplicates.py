import json
import os
from collections import defaultdict

# Create Duplicates folder if it doesn't exist
folder_name = "Duplicates"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)
    print(f"📁 Created folder: {folder_name}")

# Load data.json
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Group entries by 'word' (exact match, including all special characters)
word_groups = defaultdict(list)
for entry in data:
    word_groups[entry['word']].append(entry)

# Filter only duplicate words (more than 1 entry)
duplicate_words = {word: entries for word, entries in word_groups.items() if len(entries) > 1}

# Create separate files for each duplicate word inside Duplicates folder
file_counter = 1
for word, entries in duplicate_words.items():
    # Clean filename (remove special characters for safe file naming)
    # But keep the original word intact in the JSON content
    safe_filename = word.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    
    # If filename is too long or has problematic characters, use counter only
    if len(safe_filename) > 50 or not safe_filename.strip():
        filename = os.path.join(folder_name, f"duplicate{file_counter}.json")
    else:
        filename = os.path.join(folder_name, f"duplicate{file_counter}_{safe_filename}.json")
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created: {filename} → contains {len(entries)} copies of '{word}'")
    file_counter += 1

# Summary
print("\n" + "="*60)
print(f"📊 SUMMARY:")
print(f"   Total entries in data.json: {len(data)}")
print(f"   Total unique words: {len(word_groups)}")
print(f"   Duplicate words found: {len(duplicate_words)}")
print(f"   Files created in '{folder_name}/': {file_counter - 1}")
print("="*60)

# Show which words were duplicated
if duplicate_words:
    print("\n📝 Duplicate words found:")
    for idx, (word, entries) in enumerate(duplicate_words.items(), 1):
        print(f"   {idx}. '{word}' → {len(entries)} copies")
else:
    print("\n✅ No duplicate words found! All entries are unique.")