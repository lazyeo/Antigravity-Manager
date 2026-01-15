
import sys

def get_proto_def(filepath, keyword):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        index = content.find(keyword)
        if index == -1:
            print("Keyword not found.")
            return

        print(f"--- Context for {keyword} at {index} ---")
        start = max(0, index - 50)
        end = min(len(content), index + 3000) # Read 3000 chars to cover full definition
        print(content[start:end])
        print("-" * 20)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    file = '/Users/lbjlaq/Desktop/new/analysis/antigravity_extension.js'
    target = 'typeName="google.internal.cloud.code.v1internal.ClientMetadata";static fields=r.proto3.util.newFieldList(()=>['
    get_proto_def(file, target)
