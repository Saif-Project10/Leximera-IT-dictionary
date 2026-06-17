import json
import os
import math

def create_mcqs_json_batches():
    # Load data.json to get word count (just for reference)
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total_words = len(data)
    
    print("="*70)
    print("📁 MCQs JSON BATCHES CREATOR")
    print("="*70)
    print(f"✅ Total words in data.json: {total_words}")
    print("="*70)
    
    # Configuration
    JSON_FILES_PER_BATCH = 25
    TOTAL_BATCHES = 12
    TOTAL_JSON_FILES = TOTAL_BATCHES * JSON_FILES_PER_BATCH  # 12 * 25 = 300
    
    # Main folder
    main_folder = "MCQs_JSON_Batches"
    if not os.path.exists(main_folder):
        os.makedirs(main_folder)
    
    print(f"\n📁 Main folder created: {main_folder}/")
    print("\n📋 Configuration:")
    print(f"   JSON files per batch: {JSON_FILES_PER_BATCH}")
    print(f"   Total batches: {TOTAL_BATCHES}")
    print(f"   Total JSON files: {TOTAL_JSON_FILES}")
    print(f"   File numbering: Continuous (1 to {TOTAL_JSON_FILES})")
    print(f"   File content: [ (line 1), blank (line 2), ] (line 3)")
    print("="*70)
    
    # Create batches
    global_file_counter = 1
    total_files_created = 0
    
    for batch_num in range(1, TOTAL_BATCHES + 1):
        # Create batch folder
        batch_folder = os.path.join(main_folder, f"MCQs-JSON-Batch-{batch_num}")
        os.makedirs(batch_folder, exist_ok=True)
        
        print(f"\n📁 Creating: {batch_folder}")
        print(f"   Starting file number: {global_file_counter}")
        
        files_in_batch = 0
        
        # Create 25 JSON files in each batch
        for file_num in range(1, JSON_FILES_PER_BATCH + 1):
            # Create JSON file with continuous numbering
            filename = f"mcqs-json-batch-{global_file_counter}.json"
            filepath = os.path.join(batch_folder, filename)
            
            # Write [ on line 1, blank line 2, ] on line 3
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('[\n\n]')
            
            files_in_batch += 1
            total_files_created += 1
            global_file_counter += 1
        
        print(f"   ✅ Created {files_in_batch} JSON files (file numbers: {global_file_counter - files_in_batch} to {global_file_counter - 1})")
        print(f"   ✅ Batch {batch_num} complete!")
    
    # Save summary
    summary = {
        'total_words_available': total_words,
        'json_files_per_batch': JSON_FILES_PER_BATCH,
        'total_batches': TOTAL_BATCHES,
        'total_json_files': TOTAL_JSON_FILES,
        'file_numbering': 'Continuous (1 to {})'.format(TOTAL_JSON_FILES),
        'file_type': 'JSON with [ ] brackets (empty array)',
        'file_content': '[\n\n]',
        'note': 'Line 1: [, Line 2: empty (paste data here), Line 3: ]',
        'folder_structure': {
            'main_folder': main_folder,
            'batches': [
                {
                    'batch_num': i,
                    'json_files': JSON_FILES_PER_BATCH,
                    'file_numbers': f"{((i-1) * JSON_FILES_PER_BATCH) + 1} to {i * JSON_FILES_PER_BATCH}"
                }
                for i in range(1, TOTAL_BATCHES + 1)
            ]
        }
    }
    
    summary_file = os.path.join(main_folder, 'batch_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Create word_count.txt
    with open('word_count.txt', 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("MCQs JSON BATCHES - SUMMARY\n")
        f.write("="*60 + "\n\n")
        f.write(f"Total words in data.json: {total_words}\n")
        f.write(f"Total JSON files created: {TOTAL_JSON_FILES}\n")
        f.write(f"Total batches created: {TOTAL_BATCHES}\n")
        f.write(f"JSON files per batch: {JSON_FILES_PER_BATCH}\n")
        f.write(f"File numbering: Continuous (1 to {TOTAL_JSON_FILES})\n\n")
        f.write("-"*60 + "\n")
        f.write("File Content Format:\n")
        f.write("-"*60 + "\n")
        f.write("Line 1: [\n")
        f.write("Line 2: (empty - paste your MCQs data here)\n")
        f.write("Line 3: ]\n\n")
        f.write("-"*60 + "\n")
        f.write("Batch-wise Details:\n")
        f.write("-"*60 + "\n")
        for i in range(1, TOTAL_BATCHES + 1):
            start_num = ((i - 1) * JSON_FILES_PER_BATCH) + 1
            end_num = i * JSON_FILES_PER_BATCH
            f.write(f"  Batch {i}: {JSON_FILES_PER_BATCH} files (mcqs-json-batch-{start_num}.json to mcqs-json-batch-{end_num}.json)\n")
    
    print("\n" + "="*70)
    print("✅ COMPLETED!")
    print("="*70)
    print(f"📊 Total words available: {total_words}")
    print(f"📁 Total batches created: {TOTAL_BATCHES}")
    print(f"📄 Total JSON files created: {TOTAL_JSON_FILES}")
    print(f"📁 Main folder: {main_folder}/")
    print(f"📄 Summary report: {summary_file}")
    print(f"📄 Word count: word_count.txt")
    print(f"📄 File type: JSON with [ ] brackets")
    print(f"📌 File format:")
    print(f"   Line 1: [")
    print(f"   Line 2: (paste your MCQs data here)")
    print(f"   Line 3: ]")
    print("="*70)

if __name__ == "__main__":
    create_mcqs_json_batches()