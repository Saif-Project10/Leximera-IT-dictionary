import json
import os
import shutil
from collections import defaultdict
from datetime import datetime

def analyze_and_move_multiform_words():
    # Create folder for multi-form words
    forms_folder = "Multiple_Forms_Words"
    if not os.path.exists(forms_folder):
        os.makedirs(forms_folder)
    
    duplicates_folder = "Duplicates"
    
    # Check if Duplicates folder exists
    if not os.path.exists(duplicates_folder):
        print(f"❌ Error: '{duplicates_folder}' folder not found!")
        return
    
    # Get all JSON files
    json_files = [f for f in os.listdir(duplicates_folder) if f.endswith('.json')]
    
    if not json_files:
        print(f"❌ No JSON files found in '{duplicates_folder}'!")
        return
    
    print(f"📁 Found {len(json_files)} files in Duplicates folder")
    print("="*60)
    
    form_words = []
    remaining_files = []
    
    for filename in json_files:
        file_path = os.path.join(duplicates_folder, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                entries = json.load(f)
        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")
            continue
        
        if not entries:
            continue
        
        word = entries[0].get('word', 'unknown')
        
        # Collect all partOfSpeech values from all entries
        pos_list = set()
        for entry in entries:
            pos = entry.get('partOfSpeech', '').lower()
            if pos and pos not in ['n/a', '']:
                # Handle cases where POS might have multiple values
                # e.g., "noun / verb" or "noun, verb"
                for p in pos.replace('/', ' ').replace(',', ' ').split():
                    p = p.strip()
                    if p and p not in ['n/a', '']:
                        pos_list.add(p)
        
        # Clean POS list
        pos_list = {p for p in pos_list if p not in ['n/a', '']}
        
        # Check if this word has multiple parts of speech
        if len(pos_list) > 1:
            # This word has multiple forms (noun, verb, etc.)
            form_info = {
                'word': word,
                'file': filename,
                'forms': sorted(pos_list),
                'entries': entries
            }
            form_words.append(form_info)
            
            # Move the file
            source = os.path.join(duplicates_folder, filename)
            
            # Create a clean filename
            clean_word = word.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_').replace(' ', '_')
            forms_str = '_'.join(sorted(pos_list))
            new_filename = f"{clean_word}_{forms_str}.json"
            destination = os.path.join(forms_folder, new_filename)
            
            shutil.copy2(source, destination)
            os.remove(source)
            
            print(f"✅ MOVED: '{word}'")
            print(f"   Parts of Speech found: {sorted(pos_list)}")
            print(f"   To: {forms_folder}/{new_filename}")
            print(f"   Removed from: {duplicates_folder}/{filename}")
            print("-" * 50)
        else:
            # Only one part of speech - keep in Duplicates
            remaining_files.append(filename)
    
    print("="*60)
    print(f"\n📊 FINAL SUMMARY:")
    print(f"   Total files processed: {len(json_files)}")
    print(f"   Words with multiple forms moved: {len(form_words)}")
    print(f"   Files remaining in Duplicates: {len(remaining_files)}")
    
    # Show sample of moved words
    if form_words:
        print("\n📝 Words with multiple parts of speech:")
        for info in form_words[:10]:
            print(f"   '{info['word']}' → {info['forms']}")
        if len(form_words) > 10:
            print(f"   ... and {len(form_words) - 10} more")
    
    # Also create a report file
    report_file = f"multiform_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_files_processed': len(json_files),
            'files_moved': len(form_words),
            'files_remaining': len(remaining_files),
            'moved_words': [{'word': w['word'], 'forms': w['forms']} for w in form_words]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Detailed report saved: {report_file}")

# Run the function
if __name__ == "__main__":
    analyze_and_move_multiform_words()