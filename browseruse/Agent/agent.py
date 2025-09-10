from google import genai
from utils.file_loader import load_latest_json
from utils.element_parser import extract_simplified_elements, convert_elements_to_text
from utils.tools import build_block_labeling_prompt, build_qa_prompt
from langgraph.graph import StateGraph, END
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
PATH = os.getenv("ELEMENT_FILE_PATH")

# Define API call function
def llm_call(prompt: str, model="gemini-2.0-flash"):
    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )
    return response.text.strip()

# State for LangGraph
class AgentState(dict):
    pass

# Labeling step
def labeling_step(state: AgentState):
    json_data, _ = load_latest_json(os.getenv("ELEMENT_FILE_PATH"))
    print(len(json_data))
    elements = extract_simplified_elements(json_data)
    element_text = convert_elements_to_text(elements)

    with open(PATH, "r") as f:
        block_list = f.read()

    print("Element text length:", len(element_text))
    prompt = build_block_labeling_prompt(element_text, block_list)
    result = llm_call(prompt)
    state["labeled_blocks"] = result
    return state

# QA step
def qa_step(state: AgentState):
    question = state["question"]
    with open(r"E:\VS CODE\Agentic AI\BrowserUse\browseruse\allElement.txt", "r") as f:
        block_list = f.read()
    print("Block list length:", len(block_list))
    prompt = build_qa_prompt(state["labeled_blocks"], block_list, question)
    result = llm_call(prompt)
    state["answer"] = result
    return state

# LangGraph workflow
workflow = StateGraph(AgentState)
workflow.add_node("label_blocks", labeling_step)
workflow.add_node("qa", qa_step)
workflow.add_edge("label_blocks", "qa")
workflow.set_entry_point("label_blocks")
workflow.set_finish_point("qa")

agent = workflow.compile()
