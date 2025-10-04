import os
import sys
import json
from dotenv import load_dotenv
from pathlib import Path

# load_dotenv()

# # Base directory - root of your project
# BASE_DIR = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# # Get paths from environment variables and make them absolute by joining with BASE_DIR
# WORDS_FILE = BASE_DIR / os.getenv("ALL_BLOCKS_PATH")
# JSON_FILE = BASE_DIR / os.getenv("ELEMENT_FILE_PATH")
# DESCRIPTION_FILE = BASE_DIR / os.getenv("ELEMENTS_DESCRIPTION_JSON_PATH")

def get_base_path():
    """Return folder where exe/script is located (for reading/writing files)."""
    try:
        if getattr(sys, "frozen", False):
            # Running as PyInstaller exe
            return Path(sys.executable).parent
        else:
            # Running as Python script
            return Path(__file__).parent.parent.parent
    except Exception as e:
        print(f"Error determining base path: {e}")
        # Fallback to current directory
        return Path.cwd()
    
BASE_DIR = get_base_path()
WORDS_FILE = BASE_DIR / "element_data" / "browser_block.txt"
JSON_FILE = BASE_DIR / "element_data" / "elements.json"
DESCRIPTION_FILE = BASE_DIR / "element_data" / "description.json"

def filter_json():
    """
    Filter JSON objects based on starting words from a text file.
    Returns a list of web elements current context.
    """
    try:
        # Step 1: Load words
        try:
            with open(WORDS_FILE, "r", encoding="utf-8") as f:
                words = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Error: Words file not found at {WORDS_FILE}")
            return []
        except Exception as e:
            print(f"Error reading words file: {type(e).__name__}: {e}")
            return []

        # Step 2: Load JSON data
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: JSON file not found at {JSON_FILE}")
            return []
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in {JSON_FILE}")
            return []
        except Exception as e:
            print(f"Error reading JSON file: {type(e).__name__}: {e}")
            return []

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

        filtered = sorted(filtered, key=lambda item: item["y"])
        return filtered
        
    except Exception as e:
        print(f"Unexpected error in filter_json: {type(e).__name__}: {e}")
        return []

# print("Filtered JSON:", filter_json())

def find_used_blocks():
    find_used_blocks = []
    filtered = filter_json()
    for json_obj in filtered:
        if json_obj["x"] > 310:
            find_used_blocks.append(json_obj)
    return find_used_blocks


    # Step 4: Print result
# print("Found used blocks:", find_used_blocks())

def get_list_of_used_blocks():
    '''
    Get Scratch working space used blocks with coordinates. It's out put like 
    List of used blocks:  Code space start from coordinates (X: 310, Y: 160). List of used blocks in the code space:
        1. turn Code block. Block Coordinates: (X: 367, Y: 215 )
        2. turn Code block. Block Coordinates: (X: 367, Y: 247 )
    '''

    used_blocks = find_used_blocks()
    string = " Code space start from coordinates (X: 310, Y: 160). List of used blocks in the code space:\n"
    count = 1
    for block in used_blocks:
        string = f"{string} {count}. {block['text_content']} Code block. Block Coordinates: (X: {block['x']}, Y: {block['y']} ) \n"
        count += 1
    
    print("List of used blocks:", string)
    print(f"Found used blocks: {used_blocks}")
    return string

# print("List of used blocks:", get_list_of_used_blocks())


def get_category_coordinates(json_file_path=None):
    """Read the description.json file and extract category titles and coordinates."""
    try:
        # Use default path if none provided
        if json_file_path is None:
            json_file_path = Path(DESCRIPTION_FILE)
        
        # Check if file exists
        if not json_file_path.exists():
            return f"Error: File not found at {json_file_path}"
        
        # Read and parse the JSON file
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            return f"Error: Invalid JSON format in {json_file_path}"
        except Exception as e:
            return f"Error reading JSON file: {type(e).__name__}: {e}"
        
        # Format the output string
        result = "Category Positions:\n"
        for category, info in data.items():
            result += f"{category}: {info['coordinates']}\n"
        
        return result
    except Exception as e:
        return f"Unexpected error in get_category_coordinates: {type(e).__name__}: {e}"

# print("Category coordinates:", get_category_coordinates())


def generate_category_summary(json_file_path=None):
    """
    Generate a concise summary of Scratch programming categories and their positions.
    
    Args:
        json_file_path (str, optional): Path to description.json file
        
    Returns:
        str: Formatted summary of categories for LLM prompts
    """
    # Use default path if none provided
    if json_file_path is None:
        json_file_path = Path(DESCRIPTION_FILE)
    
    # Read and parse the JSON file
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return f"Error reading JSON file: {e}"
    
    # Generate summary text
    summary = "PAGE ELEMENT SUMMARY:\n\n"
    summary += "This is the Scratch programming interface with the following categories:\n\n"
    
    for category, info in data.items():
        blocks_count = len(info["blocks"]) if "blocks" in info else 0
        summary += f"- {category} (at {info['coordinates']}, contains {blocks_count} blocks)\n"
    
    summary += "\nYou can interact with these categories by clicking on them to access their blocks."
    return summary

# print("Category summary:", generate_category_summary())

def generate_detailed_blocks_summary(json_file_path=None, include_all_blocks=False):
    """
    Generate a comprehensive summary of Scratch programming blocks and categories.
    
    Args:
        json_file_path (str, optional): Path to description.json file
        include_all_blocks (bool): Whether to include all block details or just count them
        
    Returns:
        str: Formatted detailed summary for LLM prompts
    """
    # Use default path if none provided
    if json_file_path is None:
        json_file_path = Path(DESCRIPTION_FILE)
    print("Using JSON file path:", json_file_path)
    # Read and parse the JSON file
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return f"Error reading JSON file: {e}"
    
    # Generate detailed summary text
    summary = "SCRATCH PROGRAMMING INTERFACE ELEMENTS:\n\n"
    summary += "The page displays a Scratch programming environment with the following categories and blocks:\n\n"
    
    for category, info in data.items():
        summary += f"## {category} (located at {info['coordinates']})\n"
        
        if include_all_blocks and "blocks" in info and info["blocks"]:
            for block in info["blocks"]:
                summary += f"  - {block['name']}: {block['description']}\n"
        else:
            block_count = len(info.get("blocks", []))
            sample_blocks = ", ".join([block["name"] for block in info.get("blocks", [])[:3]])
            
            if block_count > 0:
                summary += f"  Contains {block_count} blocks including: {sample_blocks}...\n"
            else:
                summary += "  No blocks defined for this category.\n"
        
        summary += "\n"
    
    summary += "You can interact with this interface by clicking on categories to access their blocks, " 
    summary += "then dragging blocks to the workspace to build programs."
    
    return summary
# print("Detailed blocks summary:", generate_detailed_blocks_summary(include_all_blocks=True))

# if __name__ == "__main__":
#     # print(get_list_of_used_blocks())
#     print(generate_category_summary())
#     print(generate_detailed_blocks_summary(include_all_blocks=True))