import json
import re

def extract_steps_json(text):
    """
    Extracts JSON objects containing a "steps" array from text.
    
    Args:
        text (str): The text to search for JSON objects
        
    Returns:
        list: List of extracted JSON objects as Python dictionaries
    """
    # Look for JSON-like patterns starting with { and ending with }
    # Using non-greedy approach to handle multiple JSON objects in text
    potential_json_matches = re.finditer(r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{(?:[^{}])*\}))*\}))*\}', text)
    
    results = []
    
    for match in potential_json_matches:
        json_str = match.group(0)
        try:
            # Try to parse as JSON
            parsed_json = json.loads(json_str)
            
            # Check if it has the "steps" key and it's a list/array
            if isinstance(parsed_json, dict) and "steps" in parsed_json and isinstance(parsed_json["steps"], list):
                results.append(parsed_json)
        except json.JSONDecodeError:
            # Not valid JSON, skip it
            continue
    
    return results


def extract_first_steps_json(text):
    """
    Extracts the first JSON object containing a "steps" array from text.
    
    Args:
        text (str): The text to search for JSON objects
        
    Returns:
        dict: The first extracted JSON object as a Python dictionary, or None if not found
    """
    results = extract_steps_json(text)
    return results[0] if results else None


def format_json_with_double_quotes(json_dict, indent=2):
    """
    Converts a Python dictionary to a properly formatted JSON string with double quotes.
    
    Args:
        json_dict (dict): The Python dictionary to format
        indent (int): Number of spaces for indentation
        
    Returns:
        str: A properly formatted JSON string with double quotes
    """
    return json.dumps(json_dict, indent=indent)

# Add this to your existing extract functions to return formatted strings
def extract_and_format_first_json(text, indent=2):
    """
    Extracts the first JSON object and returns it as a properly formatted string.
    
    Args:
        text (str): The text to search for JSON objects
        indent (int): Number of spaces for indentation
        
    Returns:
        str: Formatted JSON string with double quotes, or None if not found
    """
    result = extract_first_steps_json(text)
    if result:
        return format_json_with_double_quotes(result, indent)
    return None
string = """
Once the JSON is generated, send it to the `executor_tool` for execution.
Once the JSON is generated, send it to the `executor_tool` for execution.
{
  "steps": [
    {"step": 1, "category": "Events", "block": "when green flag clicked"},
    {"step": 2, "category": "Events", "block": "when key pressed"},
    {"step": 3, "category": "Events", "block": "when this sprite clicked"}
  ]
}""" 

# print(extract_first_steps_json(string))
# Example usage:
# extracted_dict = extract_first_steps_json(string)
# formatted_json = format_json_with_double_quotes(extracted_dict)
# print(formatted_json)

# # Or use the combined function:
# print(extract_and_format_first_json(string))