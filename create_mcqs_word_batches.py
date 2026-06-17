import json
import os
import math

def create_mcqs_word_batches():
    # Load data.json to get words
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract all words
    all_words = [entry['word'] for entry in data]
    total_words = len(all_words)
    
    print("="*70)
    print("📁 MCQS WORDS BATCHES CREATOR")
    print("="*70)
    print(f"✅ Total words available in data.json: {total_words}")
    print("="*70)
    
    # Configuration
    WORDS_PER_FILE = 10
    FILES_PER_SUBFOLDER = 10
    WORDS_PER_SUBFOLDER = WORDS_PER_FILE * FILES_PER_SUBFOLDER  # 10 * 10 = 100
    SUBFOLDERS_PER_BATCH = 25
    WORDS_PER_BATCH = WORDS_PER_SUBFOLDER * SUBFOLDERS_PER_BATCH  # 100 * 25 = 2500
    TOTAL_BATCHES = 12
    TOTAL_WORDS_NEEDED = TOTAL_BATCHES * WORDS_PER_BATCH  # 12 * 2500 = 30000
    
    # Main folder
    main_folder = "Mcqs_Words_Batches"
    if not os.path.exists(main_folder):
        os.makedirs(main_folder)
    
    print(f"\n📁 Main folder created: {main_folder}/")
    print("\n📋 Configuration:")
    print(f"   Words per file: {WORDS_PER_FILE}")
    print(f"   Files per sub-folder: {FILES_PER_SUBFOLDER}")
    print(f"   Words per sub-folder: {WORDS_PER_SUBFOLDER}")
    print(f"   Sub-folders per batch: {SUBFOLDERS_PER_BATCH}")
    print(f"   Words per batch: {WORDS_PER_BATCH}")
    print(f"   Total batches planned: {TOTAL_BATCHES}")
    print(f"   Total words needed: {TOTAL_WORDS_NEEDED}")
    print(f"   Actual words available: {total_words}")
    print("="*70)
    
    # Check if we have enough words
    if total_words < TOTAL_WORDS_NEEDED:
        print(f"\n⚠️ Only {total_words} words available. Will use all words and stop when they run out.")
        print(f"   This will create approximately {math.ceil(total_words / WORDS_PER_BATCH)} batches.")
        print("="*70)
    
    # Create batches
    word_index = 0
    global_file_counter = 1
    total_files_created = 0
    total_subfolders_created = 0
    words_used = 0
    batches_created = 0
    
    for batch_num in range(1, TOTAL_BATCHES + 1):
        # Check if we still have words
        if word_index >= total_words:
            print(f"\n⚠️ No more words available! Stopped at Batch {batch_num - 1}")
            break
        
        # Create batch folder
        batch_folder = os.path.join(main_folder, f"Mcqs-Words-Batch-{batch_num}")
        os.makedirs(batch_folder, exist_ok=True)
        
        print(f"\n📁 Creating: {batch_folder}")
        print(f"   Starting file number: {global_file_counter}")
        
        files_in_batch = 0
        subfolders_in_batch = 0
        words_in_batch = 0
        
        # Create 25 sub-folders per batch
        for subfolder_num in range(1, SUBFOLDERS_PER_BATCH + 1):
            # Check if we still have words
            if word_index >= total_words:
                break
            
            # Create sub-folder
            subfolder_name = f"Mcqs-words-batch-{subfolder_num}"
            subfolder_path = os.path.join(batch_folder, subfolder_name)
            os.makedirs(subfolder_path, exist_ok=True)
            
            files_in_subfolder = 0
            words_in_subfolder = 0
            
            # Create 10 files in each sub-folder
            for file_num in range(1, FILES_PER_SUBFOLDER + 1):
                # Check if we still have words
                if word_index >= total_words:
                    break
                
                # Get next 10 words
                batch_words = all_words[word_index:word_index + WORDS_PER_FILE]
                word_index += WORDS_PER_FILE
                words_used += len(batch_words)
                words_in_batch += len(batch_words)
                words_in_subfolder += len(batch_words)
                
                # Create file with continuous numbering
                filename = f"mcqs-words-batch-{global_file_counter}.txt"
                filepath = os.path.join(subfolder_path, filename)
                
                # Write words in comma-separated format
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(','.join(batch_words))
                
                files_in_subfolder += 1
                files_in_batch += 1
                total_files_created += 1
                global_file_counter += 1
                
                # If no more words, break
                if word_index >= total_words:
                    break
            
            subfolders_in_batch += 1
            total_subfolders_created += 1
            
            print(f"   ✅ {subfolder_name}/ → {files_in_subfolder} files ({words_in_subfolder} words)")
            
            # If no more words, break
            if word_index >= total_words:
                break
        
        batches_created += 1
        print(f"   ✅ Batch {batch_num} complete! {files_in_batch} files, {words_in_batch} words")
        print(f"   Last file number: {global_file_counter - 1}")
        
        # If no more words, break
        if word_index >= total_words:
            print(f"\n⚠️ All {words_used} words have been used!")
            break
    
    # Save summary
    summary = {
        'total_words_available': total_words,
        'words_used': words_used,
        'words_per_file': WORDS_PER_FILE,
        'files_per_subfolder': FILES_PER_SUBFOLDER,
        'words_per_subfolder': WORDS_PER_SUBFOLDER,
        'subfolders_per_batch': SUBFOLDERS_PER_BATCH,
        'words_per_batch': WORDS_PER_BATCH,
        'total_batches_planned': TOTAL_BATCHES,
        'total_batches_created': batches_created,
        'total_subfolders_created': total_subfolders_created,
        'total_files_created': total_files_created,
        'file_numbering': 'Continuous (1 to {})'.format(total_files_created),
        'file_type': 'TXT (comma-separated words)',
        'notes': f'Only {words_used} words were available out of {TOTAL_WORDS_NEEDED} planned',
        'folder_structure': {
            'main_folder': main_folder
        }
    }
    
    summary_file = os.path.join(main_folder, 'batch_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Create word_count.txt
    with open('word_count.txt', 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("MCQS WORDS BATCHES - SUMMARY\n")
        f.write("="*60 + "\n\n")
        f.write(f"Total words available in data.json: {total_words}\n")
        f.write(f"Words used in batches: {words_used}\n")
        f.write(f"Total batches created: {batches_created}\n")
        f.write(f"Total sub-folders created: {total_subfolders_created}\n")
        f.write(f"Total files created: {total_files_created}\n")
        f.write(f"File numbering: Continuous (1 to {total_files_created})\n\n")
        f.write("-"*60 + "\n")
        f.write("Configuration:\n")
        f.write("-"*60 + "\n")
        f.write(f"  Words per file: {WORDS_PER_FILE}\n")
        f.write(f"  Files per sub-folder: {FILES_PER_SUBFOLDER}\n")
        f.write(f"  Words per sub-folder: {WORDS_PER_SUBFOLDER}\n")
        f.write(f"  Sub-folders per batch: {SUBFOLDERS_PER_BATCH}\n")
        f.write(f"  Words per batch: {WORDS_PER_BATCH}\n")
        f.write(f"  Total batches planned: {TOTAL_BATCHES}\n")
        f.write(f"  Total words planned: {TOTAL_WORDS_NEEDED}\n\n")
        f.write("-"*60 + "\n")
        f.write("Batch-wise Details:\n")
        f.write("-"*60 + "\n")
        
        # Calculate files per batch
        total_files_so_far = 0
        for i in range(1, batches_created + 1):
            if i < batches_created:
                files_in_batch = SUBFOLDERS_PER_BATCH * FILES_PER_SUBFOLDER
                words_in_batch = WORDS_PER_BATCH
            else:
                files_in_batch = total_files_created - total_files_so_far
                words_in_batch = words_used - ((i - 1) * WORDS_PER_BATCH)
            
            total_files_so_far += files_in_batch
            f.write(f"  Batch {i}: {words_in_batch} words in {files_in_batch} files\n")
    
    print("\n" + "="*70)
    print("✅ COMPLETED!")
    print("="*70)
    print(f"📊 Words available: {total_words}")
    print(f"📊 Words used: {words_used}")
    print(f"📁 Total batches created: {batches_created}")
    print(f"📁 Total sub-folders created: {total_subfolders_created}")
    print(f"📄 Total files created: {total_files_created}")
    print(f"📁 Main folder: {main_folder}/")
    print(f"📄 Summary report: {summary_file}")
    print(f"📄 Word count: word_count.txt")
    print(f"📌 Each file contains {WORDS_PER_FILE} words")
    print("="*70)

if __name__ == "__main__":
    create_mcqs_word_batches()