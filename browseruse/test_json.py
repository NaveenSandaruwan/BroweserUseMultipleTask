import json

# Path to your JSON file
json_file = r"C:\Users\malit\OneDrive\Desktop\OBO\BroweserUseMultipleTask\browseruse\element_data\elements_step_4.json"

# Load JSON content
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Pretty-print the JSON
print(json.dumps(data, indent=4, ensure_ascii=False))
