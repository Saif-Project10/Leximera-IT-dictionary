import json
import os
import math

def create_word_batches():
    # Load data.json
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract all words
    words = [entry['word'] for entry in data]
    total_words = len(words)
    
    print("="*70)
    print("📊 WORD BATCH CREATOR")
    print("="*70)
    print(f"✅ Total unique words: {total_words}")
    print("="*70)
    
    # Configuration
    WORDS_PER_FILE = 20
    FILES_PER_SUBFOLDER = 10
    WORDS_PER_SUBFOLDER = WORDS_PER_FILE * FILES_PER_SUBFOLDER  # 20 * 10 = 200
    WORDS_PER_BATCH = 5000  # 5000 words per batch (pehle 5 batches ke liye)
    
    # Main folder
    main_folder = "Main_Words_Folder"
    if not os.path.exists(main_folder):
        os.makedirs(main_folder)
    
    print(f"\n📁 Main folder created: {main_folder}/")
    print("\n📋 Configuration:")
    print(f"   Words per file: {WORDS_PER_FILE}")
    print(f"   Files per sub-folder: {FILES_PER_SUBFOLDER}")
    print(f"   Words per sub-folder: {WORDS_PER_SUBFOLDER}")
    print(f"   Words per batch: {WORDS_PER_BATCH}")
    print("="*70)
    
    # Define batch sizes
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
    
    # Remove empty batches
    batch_sizes = [size for size in batch_sizes if size > 0]
    
    print(f"\n📊 Batch sizes:")
    for i, size in enumerate(batch_sizes, 1):
        print(f"   Batch {i}: {size} words")
    print("="*70)
    
    # Create batches
    word_index = 0
    global_file_counter = 1  # Continuous file counter
    total_files_created = 0
    total_subfolders_created = 0
    
    for batch_num, batch_size in enumerate(batch_sizes, 1):
        if batch_size == 0:
            continue
        
        # Create batch folder
        batch_folder = os.path.join(main_folder, f"Word-Batch-{batch_num}")
        os.makedirs(batch_folder, exist_ok=True)
        print(f"\n📁 Creating: {batch_folder}")
        
        # Calculate number of sub-folders needed for this batch
        words_in_batch = batch_size
        subfolders_needed = math.ceil(words_in_batch / WORDS_PER_SUBFOLDER)
        
        print(f"   Words: {words_in_batch}")
        print(f"   Sub-folders: {subfolders_needed}")
        print(f"   Starting file number: {global_file_counter}")
        
        # Create sub-folders
        for subfolder_num in range(1, subfolders_needed + 1):
            # Create sub-folder
            subfolder_name = f"word-batch-{subfolder_num}"
            subfolder_path = os.path.join(batch_folder, subfolder_name)
            os.makedirs(subfolder_path, exist_ok=True)
            
            files_in_subfolder = 0
            
            # Create 10 files in each sub-folder
            for file_num in range(1, FILES_PER_SUBFOLDER + 1):
                # Check if we still have words
                if word_index >= total_words:
                    break
                
                # Get next 20 words
                batch_words = words[word_index:word_index + WORDS_PER_FILE]
                word_index += WORDS_PER_FILE
                
                # Create file with continuous numbering
                filename = f"word-batch-{global_file_counter}.txt"
                filepath = os.path.join(subfolder_path, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(','.join(batch_words))
                
                files_in_subfolder += 1
                total_files_created += 1
                global_file_counter += 1
                
                # If no more words, break
                if word_index >= total_words:
                    break
            
            total_subfolders_created += 1
            print(f"   ✅ {subfolder_name}/ → {files_in_subfolder} files created (file numbers: {global_file_counter - files_in_subfolder} to {global_file_counter - 1})")
            
            # If no more words, break
            if word_index >= total_words:
                break
        
        print(f"   ✅ Batch {batch_num} complete! Last file number: {global_file_counter - 1}")
    
    # Save summary report
    summary = {
        'total_words': total_words,
        'words_per_file': WORDS_PER_FILE,
        'files_per_subfolder': FILES_PER_SUBFOLDER,
        'words_per_subfolder': WORDS_PER_SUBFOLDER,
        'batch_sizes': batch_sizes,
        'total_batches': len(batch_sizes),
        'total_subfolders': total_subfolders_created,
        'total_files': total_files_created,
        'file_numbering': 'Continuous',
        'folder_structure': {
            'main_folder': main_folder,
            'batches': [
                {
                    'batch_num': i,
                    'words': size,
                    'subfolders': math.ceil(size / WORDS_PER_SUBFOLDER)
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
        f.write(f"Total sub-folders created: {total_subfolders_created}\n")
        f.write(f"Total files created: {total_files_created}\n")
        f.write(f"File numbering: Continuous (1 to {total_files_created})\n\n")
        f.write("Batch Details:\n")
        for i, size in enumerate(batch_sizes, 1):
            subfolders = math.ceil(size / WORDS_PER_SUBFOLDER)
            f.write(f"  Batch {i}: {size} words in {subfolders} sub-folders\n")
    
    print("\n" + "="*70)
    print("✅ COMPLETED!")
    print("="*70)
    print(f"📊 Total words processed: {total_words}")
    print(f"📁 Total batches created: {len(batch_sizes)}")
    print(f"📁 Total sub-folders created: {total_subfolders_created}")
    print(f"📄 Total files created: {total_files_created}")
    print(f"📁 Main folder: {main_folder}/")
    print(f"📄 Summary report: {summary_file}")
    print(f"📄 Word count: word_count.txt")
    print(f"📊 File numbering: 1 to {total_files_created}")
    print("="*70)

if __name__ == "__main__":
    create_word_batches()