import os
import glob
import json
import google.generativeai as genai
from dotenv import load_dotenv

# 1️⃣ Load API key and path
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
PATH = os.getenv("ELEMENT_FILE_PATH")

if not API_KEY:
    raise ValueError("❌ Gemini API key not found in .env file")
if not PATH:
    raise ValueError("❌ ELEMENT_FILE_PATH not found in .env file")

# 2️⃣ Configure Gemini
genai.configure(api_key=API_KEY)

# 3️⃣ Get latest JSON file
list_of_files = glob.glob(os.path.join(PATH))
if not list_of_files:
    print("⚠️ No JSON files found.")
    exit()

latest_file = max(list_of_files, key=os.path.getctime)
print(f"\n📂 Latest JSON file: {latest_file}")

# 4️⃣ Load JSON
with open(latest_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# 5️⃣ Simplify JSON (only needed fields)
def extract_simplified_elements(data):
    elements = []
    for key in sorted(data.keys(), key=lambda k: int(k)):
        el = data[key]
        elements.append({
            "id": key,
            "tag": el.get("tag_name"),
            "text": el.get("text_content"),
            "visible": el.get("is_visible"),
            "x": el.get("bounding_box", {}).get("x"),
            "y": el.get("bounding_box", {}).get("y")
        })
    return elements

elements = extract_simplified_elements(data)

# 6️⃣ Convert to text for LLM
element_text = "\n".join(
    [f"{e['id']}: tag={e['tag']}, text={e['text']}, visible={e['visible']}, x={round(e['x']) if e['x'] is not None else e['x']}, y={round(e['y']) if e['y'] is not None else e['y']}"
     for e in elements]
)

# 7️⃣ Create model
model = genai.GenerativeModel("gemini-2.0-flash")

with open("browseruse\\allElement.txt", "r") as file:
    content = file.read()
    # print(content)


# 8️⃣ Intro rules
rules = """
You are an AI tutor for Scratch programming.

Here are the rules for interpreting JSON elements:
- Each block starts with tag = "path".
- The following "g" or "text" belong to that block until the next "path".
- Combine multiple text parts into one label (e.g., "move", "10", "steps" → "move 10 steps").
- Blocks with only "path" and no text = "Unknown block".
- If a block's x value is larger than 310, it is a part of child used block belonging to a "My Blocks" definition.
- Block name value is in text_content; compare and consider valid block names.
- Please mention "your blocks" when describing My Blocks.
- Always mention block name and its position (e.g., 1,2,3..).
- Positions must always be sequential like 1,2,3..
- Positions should be based on the order of appearance in the JSON data.
- Output the child used blocks and other blocks mane as blocks separately with x and y values.
Block list: {content}
IMPORTANT:
- Only label the blocks and create the position list:
  ex:1.go to X:50.155522255, Y:502.84544565.
- befor give the lables first check if the block is in above    
"""

# 9️⃣ Send initial context
context = f"{rules}\n\nHere is the extracted JSON data:\n{element_text}\n\nNow, label the blocks according to the rules."

response = model.generate_content(context)

print("\n===================== BLOCK LABELING =====================\n")
print(response.text)
print("\n==========================================================\n")


# ✅ Question-answering using the labeled blocks from initial LLM response
print("💬 Ask me questions about these blocks (type 'n' to stop)\n")

while True:
    question = input("❓ Your question: ")
    if question.lower().strip() == "n":
        print("👋 Exiting Q&A loop.")
        break

    # Create prompt for LLM using the labeled blocks
    qa_prompt = f"""
Based on the Scratch block labeling below :
list of blocks with positions:
    {response.text}
Block list: {content}
Question: {question}
when you give me block as anwser firt look if there is similar block in above list of blocks with positions and return block name and position only bellow format
if not suggest block whish is in Scratch and how to get that block use Block list for that.
Answer in this exact format:
Use a `<block name>` block from the page in `<position>` and change it to `<user's request>`.
give small explanation about that block also.

If no relevant block is found in list of blocks with positions respond exactly:
give me that block from Block list and how to get that block.
"""
    answer = model.generate_content(qa_prompt)
    print("\n📝 Answer:\n", answer.text, "\n")
