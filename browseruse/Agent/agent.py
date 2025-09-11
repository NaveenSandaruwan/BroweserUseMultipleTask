from google import genai
from utils.file_loader import load_and_extract_elements, load_element_descriptions
from utils.prompt_rules import RULES
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.dragTool import Toolbox
from tools.browserUseClient import send_task
from langgraph.graph import StateGraph, END

# Add the parent directory of `tools` to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from dotenv import load_dotenv
from dataclasses import dataclass

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

dragTool = Toolbox()

from typing import TypedDict, List

class AgentState(TypedDict, total=False):
    rules: str
    labeled_blocks: List[dict]
    element_description: str
    question: str
    answer: str
    task_type: str
    result: str

class AgentGraph:
    def __init__(self):
        # Use dict state, easier with LangGraph
        self.graph = StateGraph(AgentState)

        # Define the workflow steps (nodes)
        self.graph.add_node("refresh_data", self.refresh_data)
        self.graph.add_node("load_files", self.load_files)
        self.graph.add_node("process_rules", self.process_rules)
        self.graph.add_node("analyze_question", self.analyze_question)
        self.graph.add_node("assist_user", self.assist_user)
        self.graph.add_node("generate_answer", self.generate_answer)
        self.graph.add_node("get_result", self.get_result)

        # Define the workflow edges
        self.graph.set_entry_point("refresh_data")
        self.graph.add_edge("refresh_data", "load_files")
        self.graph.add_edge("load_files", "process_rules")
        self.graph.add_edge("process_rules", "analyze_question")

        self.graph.add_conditional_edges(
            "analyze_question",
            lambda state: state["task_type"],  # decision key
            {
                "drag_and_drop": "assist_user",
                "generate_answer": "generate_answer",
            },
        )
        self.graph.add_edge("assist_user", "get_result")
        self.graph.add_edge("generate_answer", "get_result")
        self.graph.add_edge("get_result", END)

        # Compile the graph
        self.app = self.graph.compile()

    # === Nodes ===
    def refresh_data(self, state: AgentState):
        """Refresh the element data files."""
        send_task("refresh")
        return state  # Return the updated state

    def load_files(self, state: AgentState):
        """Load labeled blocks and element descriptions."""
        print(f"DEBUG: State before load_files: {state} (type: {type(state)})")
        
        # Load labeled blocks
        labeled_blocks = load_and_extract_elements()
        state["labeled_blocks"] = labeled_blocks
        print(f"🔍 Found {len(labeled_blocks)} labeled blocks.")
        
        # Load element descriptions
        element_description = load_element_descriptions()
        state["element_description"] = element_description
        print(f"📝 Loaded element descriptions.")
        
        return state  # Return the updated state

    def process_rules(self, state: AgentState):
        """Load rules for the agent."""
        state["rules"] = RULES
        return state  # Return the updated state

    def analyze_question(self, state: AgentState):
        """Analyze the user's question to determine the task type."""
        question = state.get("question", "")
        if "drag" in question.lower() or "drop" in question.lower():
            state["task_type"] = "drag_and_drop"
        else:
            state["task_type"] = "generate_answer"
        return state  # Return the updated state

    def assist_user(self, state: AgentState):
        """Assist the user by dragging and dropping blocks."""
        print("Hubaaaaa")
        for block in state.get("labeled_blocks", []):
            x_start, y_start, x_end, y_end = block["x_start"], block["y_start"], block["x_end"], block["y_end"]
            dragTool.drag_and_drop(x_start, y_start, x_end, y_end)
        state["result"] = "Drag-and-drop assistance completed."
        return state  # Return the updated state

    def generate_answer(self, state: AgentState):
        """Generate an answer to the user's question."""
        # Convert labeled_blocks to a string (e.g., JSON format) for inclusion in the prompt
        labeled_blocks_str = "\n".join([str(block) for block in state.get("labeled_blocks", [])])
    
        # Construct the prompt with labeled_blocks included
        prompt = (
            f"Rules: {state['rules']}\n"
            f"Description: {state['element_description']}\n"
            f"Labeled Blocks:\n{labeled_blocks_str}\n"
            f"Question: {state['question']}"
        )
    
        # Call the LLM with the constructed prompt
        state["answer"] = llm_call(prompt)
        state["result"] = f"Answer: {state['answer']}"
        return state  # Return the updated state

    def get_result(self, state: AgentState):
        """Return the agent's result."""
        return state  # Return the final state
    

if __name__ == "__main__":
    agent = AgentGraph()
    while True:
        question = input("Enter your question (or type 'exit' to quit): ")
        if question.strip().lower() == "exit":
            break

        # Initialize the state as a dictionary
        initial_state = {"question": question}
        result = agent.app.invoke(initial_state)
        print("Result:", result.get("result"))
    # print(agent.app.get_graph().draw_mermaid())