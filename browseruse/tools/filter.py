import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

WORDS_FILE = os.getenv("ALL_BLOCKS_PATH")
JSON_FILE = os.getenv("ELEMENT_FILE_PATH")

def filter_json():
    # Step 1: Load words
    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        words = [line.strip() for line in f if line.strip()]
        

    # Step 2: Load JSON data
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Step 3: Filter data
    filtered = []
    for obj in data.values():
        text = obj.get("text_content","")
        if text is None or not obj.get("tag_name") == "text":
            continue
        if any(text.startswith(w) for w in words):
            filtered.append({
                "tag_name": obj["tag_name"],
                "text_content": obj["text_content"],
                "x": round(obj["bounding_box"]["x"]),
                "y": round(obj["bounding_box"]["y"])
            })

    # Step 4: Print result
    #print(json.dumps(filtered, indent=2, ensure_ascii=False))
    filtered = sorted(filtered, key=lambda item: item["y"])
    return filtered

def find_used_blocks():
    find_used_blocks = []
    filtered = filter_json()
    for json_obj in filtered:
        if json_obj["x"] > 310:
            find_used_blocks.append(json_obj)
    return find_used_blocks


    # Step 4: Print result
print(filter_json())

def grt_list_of_used_blocks():
    used_blocks = find_used_blocks()
    string = ""
    count = 1
    for block in used_blocks:
        string = f"{string} {count}. {block['text_content']} Block \n"
        count += 1
    return string

# print(grt_list_of_used_blocks())