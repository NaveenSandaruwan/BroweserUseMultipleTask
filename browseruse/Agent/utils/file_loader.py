import json
import os
from dotenv import load_dotenv
load_dotenv()

def load_and_extract_elements(json_path=os.getenv("ELEMENT_FILE_PATH")):
    """
    Reads a JSON file containing element data, extracts 'tag_name', 'text_content', 'x', and 'y' from each item,
    and returns a structured list suitable for feeding to an LLM.


    Returns:
        list[dict]: List of dictionaries with keys: 'tag_name', 'text_content', 'x', 'y'.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    elements = []
    print("xxxxx")
    for item in data.values():
        tag_name = item.get('tag_name', '')
        text_content = item.get('text_content', '')
        bounding_box = item.get('bounding_box', {})
        x = bounding_box.get('x', None)
        y = bounding_box.get('y', None)
        if x is not None:
            x = round(x)
        if y is not None:
            y = round(y)
        elements.append({
            'tag_name': tag_name,
            'text_content': text_content,
            'x': x,
            'y': y
        })
    return elements

# Example usage:
# elements = load_and_extract_elements(r"E:\VS CODE\Agentic AI\BrowserUse\element_data\elements.json")
# print(elements)

# def load_element_descriptions(txt_path=r"E:\VS CODE\Agentic AI\BrowserUse\browseruse\allElement.txt"):
#     """
#     Reads a text file containing element descriptions, one per line, and returns a list of descriptions.

#     Returns:
#         list[str]: List of element descriptions.
#     """
#     with open(txt_path, 'r', encoding='utf-8') as f:
#         descriptions = [line.strip() for line in f if line.strip()]
#     return descriptions

def load_scratch_descriptions(json_path=os.getenv("ELEMENTS_DESCRIPTION_JSON_PATH")):
    """
    Reads a JSON file containing Scratch block descriptions and formats it as a readable string.
    
    Args:
        json_path (str): Path to the description JSON file
        
    Returns:
        str: Formatted string containing all Scratch block descriptions by category
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Format the data as a readable string
        formatted_output = "SCRATCH BLOCKS DESCRIPTIONS:\n\n"
        
        # Iterate through each category
        for category, blocks in data.items():
            formatted_output += f"=== {category.upper()} ===\n"
            
            # Add each block in the category
            for block in blocks:
                name = block.get('name', 'Unknown')
                description = block.get('description', 'No description available')
                formatted_output += f"- {name}: {description}\n"
            
            formatted_output += "\n"
        
        return formatted_output
    
    except FileNotFoundError:
        return f"Error: File not found at {json_path}"
    except json.JSONDecodeError:
        return f"Error: Invalid JSON format in {json_path}"
    except Exception as e:
        return f"Error loading description file: {str(e)}"


# print(load_scratch_descriptions())