
import sys

def search_in_file(filepath, keywords):
    try:
        print(f"Reading file: {filepath}")
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        print(f"File read. Size: {len(content)} chars.")
        
        for keyword in keywords:
            print(f"--- Searching for: {keyword} ---")
            count = 0
            index = content.find(keyword)
            while index != -1:
                count += 1
                if count <= 5: # Limit matches to avoid truncation
                    start = max(0, index - 100)
                    end = min(len(content), index + 100)
                    print(f"Match {count} at {index}:")
                    snippet = content[start:end].replace('\n', ' ')
                    print(f"...{snippet}...")
                    print("-" * 20)
                
                index = content.find(keyword, index + 1)
            
            if count == 0:
                print("No matches found.")
            else:
                print(f"Total matches for {keyword}: {count}")
            print(f"--- End search for {keyword} ---")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 search_large_js.py <filepath>")
        sys.exit(1)
        
    target_file = sys.argv[1]
    search_in_file(target_file, ['ClientMetadata', 'google.internal.cloud.code.v1internal.ClientMetadata'])
