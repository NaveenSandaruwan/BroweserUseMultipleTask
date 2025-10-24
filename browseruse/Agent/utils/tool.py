import json
from typing import List, Dict, Any
from langchain_core.tools import tool
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tools.execution import AdvancedExecutor

executor = AdvancedExecutor()

@tool
def make_blocks_advanced(json_string: str) -> str:
    '''
    Execute blocks with ADVANCED NESTING support.
    
    Handles:
    - Blocks inside containers (forever, repeat, if)
    - Condition blocks in diamond/hexagon slots
    - Multi-level nesting
    - Proper coordinate calculation
    
    JSON Format:
    {
      "steps": [
        {"step": 1, "category": "Events", "block": "when green flag clicked", 
         "placement": "root", "parent_step": null},
        {"step": 2, "category": "Control", "block": "forever", 
         "placement": "below", "parent_step": 1},
        {"step": 3, "category": "Control", "block": "if then", 
         "placement": "inside", "parent_step": 2},
        {"step": 4, "category": "Sensing", "block": "touching object", 
         "placement": "condition", "parent_step": 3},
        {"step": 5, "category": "Motion", "block": "move steps", 
         "placement": "inside", "parent_step": 3}
      ]
    }
    '''
    if len(json_string.strip()) == 0:
        print("Empty JSON string provided.")
        return "false"
    
    try:
        result = executor.execute_with_nesting(json_string)
        return "true" if "completed" in result.lower() else "false"
    except json.JSONDecodeError:
        print("Invalid JSON format")
        return "false"
    except Exception as e:
        print(f"Error in make_blocks_advanced: {e}")
        return "false"


@tool
def clean_and_make_blocks_advanced(json_string: str) -> str:
    '''
    Clean workspace then execute with ADVANCED NESTING.
    
    Use for CODE FIXING operations.
    
    Process:
    1. Remove all blocks from workspace
    2. Refresh DOM
    3. Execute new blocks with proper nesting
    '''
    if len(json_string.strip()) == 0:
        print("Empty JSON string provided.")
        return "false"
    
    try:
        result = executor.clean_and_execute(json_string)
        return "true" if "completed" in result.lower() else "false"
    except json.JSONDecodeError:
        print("Invalid JSON format")
        return "false"
    except Exception as e:
        print(f"Error in clean_and_make_blocks_advanced: {e}")
        return "false"