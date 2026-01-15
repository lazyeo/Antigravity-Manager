
import sys

def read_context(filepath, offset, length=2000):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            f.seek(offset)
            content = f.read(length)
            print(f"--- Content at {offset} (len {length}) ---")
            print(content)
            print("-" * 20)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    offsets = [1331378, 1332683, 1333454, 1333984]
    file = '/Users/lbjlaq/Desktop/new/analysis/antigravity_extension.js'
    for off in offsets:
        read_context(file, off)
