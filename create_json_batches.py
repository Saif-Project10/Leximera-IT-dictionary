import json
import os
import math

def create_empty_json_files():
    # Load data just to get word count
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total_words = len(data)
    
    print("="*70)
    print("📁 EMPTY JSON FILES CREATOR (With [ ] brackets)")
    print("="*70)
    print(f"✅ Total words in data.json: {total_words}")
    print("="*70)
    
    # Configuration
    WORDS_PER_FILE = 20
    FILES_PER_SUBFOLDER = 10
    WORDS_PER_SUBFOLDER = WORDS_PER_FILE * FILES_PER_SUBFOLDER  # 20 * 10 = 200
    WORDS_PER_BATCH = 5000
    
    # Main folder
    main_folder = "Main_Words_Folder_JSON"
    if not os.path.exists(main_folder):
        os.makedirs(main_folder)
    
    print(f"\n📁 Main folder created: {main_folder}/")
    print("\n📋 Configuration:")
    print(f"   Words per file: {WORDS_PER_FILE}")
    print(f"   Files per sub-folder: {FILES_PER_SUBFOLDER}")
    print(f"   Words per sub-folder: {WORDS_PER_SUBFOLDER}")
    print(f"   Words per batch: {WORDS_PER_BATCH}")
    print("="*70)
    
    # Calculate batch sizes
    batch_sizes = []
    remaining_words = total_words
    
    for batch_num in range(1, 7):
        if batch_num <= 5:
            batch_size = 5000
        else:
            batch_size = remaining_words
        
        if remaining_words > 0:
            if batch_num <= 5:
                batch_sizes.append(5000)
                remaining_words -= 5000
            else:
                batch_sizes.append(remaining_words)
        else:
            batch_sizes.append(0)
    
    batch_sizes = [size for size in batch_sizes if size > 0]
    
    print(f"\n📊 Batch sizes:")
    for i, size in enumerate(batch_sizes, 1):
        files_needed = math.ceil(size / WORDS_PER_SUBFOLDER)
        print(f"   Batch {i}: {size} words → {files_needed} JSON files")
    print("="*70)
    
    # Create batches
    global_file_counter = 1
    total_files_created = 0
    
    for batch_num, batch_size in enumerate(batch_sizes, 1):
        if batch_size == 0:
            continue
        
        # Create batch folder
        batch_folder = os.path.join(main_folder, f"Word-Batch-{batch_num}")
        os.makedirs(batch_folder, exist_ok=True)
        
        # Calculate files needed for this batch (each file = 10 batches = 200 words)
        files_needed = math.ceil(batch_size / WORDS_PER_SUBFOLDER)
        
        print(f"\n📁 Creating: {batch_folder}")
        print(f"   Words: {batch_size}")
        print(f"   JSON files: {files_needed}")
        print(f"   Starting file number: {global_file_counter}")
        
        # Create JSON files directly in batch folder
        for file_num in range(1, files_needed + 1):
            filename = f"word-batch-{global_file_counter}.json"
            filepath = os.path.join(batch_folder, filename)
            
            # Write [ on line 1, empty line 2, ] on line 3
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('[\n\n]')
            
            total_files_created += 1
            global_file_counter += 1
        
        print(f"   ✅ Created {files_needed} JSON files (file numbers: {global_file_counter - files_needed} to {global_file_counter - 1})")
        print(f"   ✅ Batch {batch_num} complete!")
    
    # Save summary
    summary = {
        'total_words': total_words,
        'words_per_file': WORDS_PER_FILE,
        'files_per_subfolder': FILES_PER_SUBFOLDER,
        'words_per_subfolder': WORDS_PER_SUBFOLDER,
        'words_per_batch': WORDS_PER_BATCH,
        'batch_sizes': batch_sizes,
        'total_batches': len(batch_sizes),
        'total_files': total_files_created,
        'file_numbering': 'Continuous (1 to {})'.format(total_files_created),
        'file_type': 'JSON with [ ] brackets (empty array)',
        'file_content': '[\n\n]',
        'note': 'Line 1: [, Line 2: empty (paste here), Line 3: ]',
        'folder_structure': {
            'main_folder': main_folder,
            'batches': [
                {
                    'batch_num': i,
                    'words': size,
                    'files': math.ceil(size / WORDS_PER_SUBFOLDER),
                    'words_per_file': WORDS_PER_SUBFOLDER
                }
                for i, size in enumerate(batch_sizes, 1)
            ]
        }
    }
    
    summary_file = os.path.join(main_folder, 'batch_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Create word_count.txt
    with open('word_count.txt', 'w', encoding='utf-8') as f:
        f.write(f"Total unique words in data.json: {total_words}\n")
        f.write(f"Total batches created: {len(batch_sizes)}\n")
        f.write(f"Total JSON files created: {total_files_created}\n")
        f.write(f"File numbering: Continuous (1 to {total_files_created})\n")
        f.write(f"Each JSON file = 10 word batches = 200 words\n")
        f.write(f"Each JSON file contains:\n")
        f.write(f"  Line 1: [\n")
        f.write(f"  Line 2: (empty - paste data here)\n")
        f.write(f"  Line 3: ]\n\n")
        f.write("Batch Details:\n")
        for i, size in enumerate(batch_sizes, 1):
            files = math.ceil(size / WORDS_PER_SUBFOLDER)
            f.write(f"  Batch {i}: {size} words in {files} JSON files\n")
    
    print("\n" + "="*70)
    print("✅ COMPLETED!")
    print("="*70)
    print(f"📊 Total words processed: {total_words}")
    print(f"📁 Total batches created: {len(batch_sizes)}")
    print(f"📄 Total JSON files created: {total_files_created}")
    print(f"📁 Main folder: {main_folder}/")
    print(f"📄 Summary report: {summary_file}")
    print(f"📄 Word count: word_count.txt")
    print(f"📄 File type: JSON with [ ] brackets")
    print(f"📌 Each JSON file = 10 word batches = 200 words")
    print(f"📌 File format:")
    print(f"   Line 1: [")
    print(f"   Line 2: (paste your data here)")
    print(f"   Line 3: ]")
    print("="*70)

if __name__ == "__main__":
    create_empty_json_files()