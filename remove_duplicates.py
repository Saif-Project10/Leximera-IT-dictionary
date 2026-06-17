import json
from collections import defaultdict

# Load data.json
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("="*60)
print("🔍 DUPLICATE REMOVER - Keep Only First Copy")
print("="*60)
print(f"📊 Original entries: {len(data)}")

# Group by word
word_groups = defaultdict(list)
for entry in data:
    word_groups[entry['word']].append(entry)

# Keep only first copy of each word
cleaned_data = []
removed_count = 0
duplicate_words = []

for word, entries in word_groups.items():
    if len(entries) == 1:
        # Unique word - keep as is
        cleaned_data.append(entries[0])
    else:
        # Keep first copy only
        cleaned_data.append(entries[0])
        removed_count += len(entries) - 1
        duplicate_words.append({
            'word': word,
            'total_copies': len(entries),
            'kept': 1,
            'removed': len(entries) - 1
        })

# Update data.json with cleaned data
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

print("="*60)
print("✅ SUCCESS!")
print("="*60)
print(f"✅ Original entries: {len(data)}")
print(f"✅ Cleaned entries: {len(cleaned_data)}")
print(f"✅ Removed duplicates: {removed_count}")
print(f"✅ data.json has been updated!")
print("="*60)

# Show sample of what was removed
if duplicate_words:
    print("\n📝 Sample of duplicate words removed (first 20):")
    for item in duplicate_words[:20]:
        print(f"   '{item['word']}' → {item['total_copies']} copies, removed {item['removed']}")
    if len(duplicate_words) > 20:
        print(f"   ... and {len(duplicate_words) - 20} more words")
else:
    print("\n✅ No duplicates found!")

# Save a backup of the report (optional)
with open('duplicate_removal_report.json', 'w', encoding='utf-8') as f:
    json.dump({
        'original_entries': len(data),
        'cleaned_entries': len(cleaned_data),
        'removed_entries': removed_count,
        'duplicate_words_processed': len(duplicate_words),
        'details': duplicate_words
    }, f, indent=2, ensure_ascii=False)

print(f"\n📄 Detailed report saved: duplicate_removal_report.json")