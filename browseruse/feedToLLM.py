import os
import glob
import json
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime

# 1️⃣ Load API key from .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
PATH = os.getenv("ELEMENT_FILE_PATH")

if not API_KEY:
    raise ValueError("❌ Gemini API key not found in .env file")
if not PATH:
    raise ValueError("❌ ELEMENT_FILE_PATH not found in .env file")

# 2️⃣ Configure Gemini
genai.configure(api_key=API_KEY)

# 3️⃣ Path to JSON folder
json_dir = PATH

# 4️⃣ Get latest JSON file automatically
list_of_files = glob.glob(os.path.join(json_dir, "*.json"))
if not list_of_files:
    print("⚠️ No JSON files found in the element_data folder.")
    exit()

latest_file = max(list_of_files, key=os.path.getctime)
print(f"\n📂 Latest JSON file: {latest_file}")


# 5️⃣ Load latest JSON content
with open(latest_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# 6️⃣ Extract only needed fields
def extract_simplified_elements(data):
    elements = []
    for key in sorted(data.keys(), key=lambda k: int(k)):
        el = data[key]
        elements.append({
            "id": key,
            "tag_name": el.get("tag_name"),
            "text_content": el.get("text_content"),
            "is_visible": el.get("is_visible")
        })
    return elements

elements = extract_simplified_elements(data)

# 7️⃣ Print first 5 elements before sending to LLM
print("\n🔍 First 5 elements preview:")
for e in elements[:5]:
    print(e)

# 8️⃣ Format for Gemini prompt
element_text = "\n".join(
    [f"{e['id']}: tag={e['tag_name']}, text={e['text_content']}, visible={e['is_visible']}"
     for e in elements]
)

# 9️⃣ Create Gemini model
model = genai.GenerativeModel("gemini-2.0-flash")

# 🔟 Prompt to LLM
prompt = f"""
You are an AI tutor for Scratch programming.

Here is a simplified list of elements extracted from a Scratch JSON file:
{element_text}

Rules:
- Each block starts with tag_name = "path".
- The following "g" or "text" elements belong to that block until the next "path".
- Combine multiple text parts into a single label (e.g., "move", "10", "steps" → "move 10 steps").
- If a block has only "path" and no text, call it "Unknown block".

For each block, explain clearly:
1. Block label
2. What the block does in Scratch
3. Usage (when a student might use it)
4. Example (short context)
"""

# 1️⃣1️⃣ Generate response
response = model.generate_content(prompt)

# 1️⃣2️⃣ Save output to file
output_dir = os.path.join(os.getcwd(), "scratch_block_descriptions")
os.makedirs(output_dir, exist_ok=True)

output_file = os.path.join(
    output_dir, f"scratch_block_descriptions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
)
with open(output_file, "w", encoding="utf-8") as f:
    f.write(response.text)

print(f"\n✅ Block descriptions saved to: {output_file}")
