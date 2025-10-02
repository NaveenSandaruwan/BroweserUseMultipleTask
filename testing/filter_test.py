import pytest
from unittest.mock import patch, mock_open, MagicMock
import os
import sys
import json

# --- 1. SETUP PATH TO IMPORT filter.py (USING ABSOLUTE PATH) ---

# CRITICAL FIX: Use a RAW STRING (r"...") for the Windows path to the 'tools' directory.
# This ensures the 'filter.py' module can be found and imported.
target_dir = r"C:\Users\malit\OneDrive\Desktop\OBO\BroweserUseMultipleTask\browseruse\tools"

# Add the target directory to Python's search path
try:
    if target_dir not in sys.path:
        sys.path.insert(0, target_dir)
        print(f"Added filter.py directory to sys.path: {target_dir}")

    # Now attempt the import
    from filter import (
        filter_json, 
        find_used_blocks, 
        get_list_of_used_blocks, 
        get_category_coordinates, 
        generate_category_summary, 
        generate_detailed_blocks_summary
    )
except ImportError as e:
    # This block handles the case where the import fails (e.g., if the path is wrong)
    print(f"ERROR: Could not import functions from filter.py. Ensure the path '{target_dir}' is correct. Error: {e}")
    # In a real test environment, this would typically cause the session to fail or skip tests.
    pass


# --- 2. MOCK DATA DEFINITIONS ---

# These variables simulate the contents of your external files (words.txt, elements.json, description.json)
MOCK_WORDS_CONTENT = "move\nturn\nsay\nset"

MOCK_ELEMENTS_JSON = {
    "e1": {"tag_name": "text", "text_content": "move 10 steps", "bounding_box": {"x": 100.5, "y": 200.1}},
    "e2": {"tag_name": "text", "text_content": "say hello", "bounding_box": {"x": 400.3, "y": 100.9}}, # Expected block
    "e3": {"tag_name": "button", "text_content": "Save", "bounding_box": {"x": 50, "y": 50}}, # Excluded (wrong tag)
    "e4": {"tag_name": "text", "text_content": "if on edge, bounce", "bounding_box": {"x": 100, "y": 300}}, # Excluded (wrong starting word)
    "e5": {"tag_name": "text", "text_content": "turn 15 degrees", "bounding_box": {"x": 400, "y": 250}}, # Expected block
    "e6": {"tag_name": "text", "text_content": "set size to 100", "bounding_box": {"x": 100, "y": 150}}, # Expected block
    "e7": {"tag_name": "div", "text_content": "turn 90", "bounding_box": {"x": 100, "y": 400}}, # Excluded (wrong tag)
    "e8": {"tag_name": "text", "text_content": None, "bounding_box": {"x": 100, "y": 450}} # Excluded (None text content)
}

MOCK_DESCRIPTION_JSON = {
    "Motion": {
        "coordinates": "(X: 50, Y: 100)",
        "blocks": [
            {"name": "move steps", "description": "Moves the sprite"},
            {"name": "turn right", "description": "Turns the sprite clockwise"}
        ]
    },
    "Looks": {
        "coordinates": "(X: 50, Y: 150)",
        "blocks": [
            {"name": "say for secs", "description": "Says text"}
        ]
    },
    "Events": {
        "coordinates": "(X: 50, Y: 200)",
        "blocks": []
    }
}

# --- 3. PYTEST FIXTURES FOR MOCKING ---

@pytest.fixture
def mock_env_vars():
    """Mocks the environment variables used for file paths."""
    # We mock the ENVs because filter.py uses them to look up paths. 
    # The actual path values here don't matter since 'open' is also mocked.
    with patch.dict(os.environ, {
        "ALL_BLOCKS_PATH": "/mock/words.txt",
        "ELEMENT_FILE_PATH": "/mock/elements.json",
        "ELEMENTS_DESCRIPTION_JSON_PATH": "/mock/description.json"
    }):
        yield

@pytest.fixture
def mock_file_reads(mock_env_vars):
    """
    Mocks the built-in 'open' function to simulate reading different files 
    based on the file path requested by the filter functions.
    
    The file_path argument received by mock_file_open may be a pathlib.Path object.
    We convert it to a string to ensure consistent comparison and usage.
    """
    def mock_file_open(file_path, *args, **kwargs):
        # FIX: Ensure file_path is treated as a string for robust matching, 
        # especially if filter.py uses pathlib.Path objects.
        file_path = str(file_path)
        
        # Text/Word file mocking
        if 'words.txt' in file_path or 'browser_block.txt' in file_path:
            return mock_open(read_data=MOCK_WORDS_CONTENT).return_value
        
        # JSON file mocking (now unified with mock_open)
        elif 'elements.json' in file_path:
            return mock_open(read_data=json.dumps(MOCK_ELEMENTS_JSON)).return_value
        
        elif 'description.json' in file_path:
            return mock_open(read_data=json.dumps(MOCK_DESCRIPTION_JSON)).return_value
        
        else:
            # This will catch any other files the function tries to open that haven't been mocked
            raise FileNotFoundError(f"Mocked file not found: {file_path}")

    # Patch the global 'open' function
    with patch('builtins.open', side_effect=mock_file_open):
        yield

# --- 4. TEST CASES ---

def test_filter_json_filters_and_formats_correctly(mock_file_reads):
    """Tests the core filtering, rounding, and sorting logic of filter_json."""
    
    expected_output = [
        # Blocks that pass filtering (tag_name='text' and starts with a word in WORDS_FILE)
        # Sorted by rounded Y coordinate (101, 150, 200, 250)
        {"tag_name": "text", "text_content": "say hello", "x": 400, "y": 101},
        {"tag_name": "text", "text_content": "set size to 100", "x": 100, "y": 150},
        # FIX: Corrected expected X coordinate for 'move 10 steps' from 101 to 100 
        # to align with Python's banker's rounding (round(100.5) is 100).
        {"tag_name": "text", "text_content": "move 10 steps", "x": 100, "y": 200}, 
        {"tag_name": "text", "text_content": "turn 15 degrees", "x": 400, "y": 250},
    ]

    result = filter_json()
    
    assert len(result) == 4
    assert result == expected_output


def test_find_used_blocks_filters_by_x_coordinate(mock_file_reads):
    """Tests that find_used_blocks correctly filters objects where x > 310 (the workspace)."""

    # Blocks with X > 310: "say hello" (x=400) and "turn 15 degrees" (x=400)
    expected_output = [
        {"tag_name": "text", "text_content": "say hello", "x": 400, "y": 101},
        {"tag_name": "text", "text_content": "turn 15 degrees", "x": 400, "y": 250},
    ]

    result = find_used_blocks()
    
    assert len(result) == 2
    assert result == expected_output


def test_get_list_of_used_blocks_formats_string_correctly(mock_file_reads):
    """Tests that get_list_of_used_blocks generates the expected descriptive string."""
    
    expected_string = (
        " Code space start from coordinates (X: 310, Y: 160). List of used blocks in the code space:\n"
        " 1. say hello Code block. Block Coordinates: (X: 400, Y: 101 ) \n"
        " 2. turn 15 degrees Code block. Block Coordinates: (X: 400, Y: 250 ) \n"
    )
    
    # We patch 'print' because the function prints and returns the string
    with patch('builtins.print'):
        result = get_list_of_used_blocks()
        
    assert result == expected_string


def test_get_category_coordinates_formats_string_correctly(mock_file_reads):
    """Tests extraction of category titles and coordinates."""
    
    expected_result = (
        "Category Positions:\n"
        "Motion: (X: 50, Y: 100)\n"
        "Looks: (X: 50, Y: 150)\n"
        "Events: (X: 50, Y: 200)\n"
    )
    
    result = get_category_coordinates()
    assert result == expected_result


def test_generate_category_summary_formats_string_correctly(mock_file_reads):
    """Tests the generation of a concise category summary, including block counts."""
    
    expected_result = (
        "PAGE ELEMENT SUMMARY:\n\n"
        "This is the Scratch programming interface with the following categories:\n\n"
        "- Motion (at (X: 50, Y: 100), contains 2 blocks)\n"
        "- Looks (at (X: 50, Y: 150), contains 1 blocks)\n"
        "- Events (at (X: 50, Y: 200), contains 0 blocks)\n"
        "\nYou can interact with these categories by clicking on them to access their blocks."
    )
    
    result = generate_category_summary()
    assert result == expected_result


def test_generate_detailed_blocks_summary_formats_concise_correctly(mock_file_reads):
    """Tests the detailed summary in the default (concise, sample blocks) mode."""
    
    expected_result = (
        "SCRATCH PROGRAMMING INTERFACE ELEMENTS:\n\n"
        "The page displays a Scratch programming environment with the following categories and blocks:\n\n"
        "## Motion (located at (X: 50, Y: 100))\n"
        " Contains 2 blocks including: move steps, turn right...\n\n"
        "## Looks (located at (X: 50, Y: 150))\n"
        " Contains 1 blocks including: say for secs...\n\n"
        "## Events (located at (X: 50, Y: 200))\n"
        " No blocks defined for this category.\n\n"
        "\nYou can interact with this interface by clicking on categories to access their blocks, " 
        "then dragging blocks to the workspace to build programs."
    )
    
    result = generate_detailed_blocks_summary(include_all_blocks=False)
    assert result == expected_result


def test_generate_detailed_blocks_summary_formats_detailed_correctly(mock_file_reads):
    """Tests the detailed summary when include_all_blocks is True (full block listing)."""
    
    expected_result = (
        "SCRATCH PROGRAMMING INTERFACE ELEMENTS:\n\n"
        "The page displays a Scratch programming environment with the following categories and blocks:\n\n"
        "## Motion (located at (X: 50, Y: 100))\n"
        "  - move steps: Moves the sprite\n"
        "  - turn right: Turns the sprite clockwise\n\n"
        "## Looks (located at (X: 50, Y: 150))\n"
        "  - say for secs: Says text\n\n"
        "## Events (located at (X: 50, Y: 200))\n"
        "  No blocks defined for this category.\n\n"
        "\nYou can interact with this interface by clicking on categories to access their blocks, " 
        "then dragging blocks to the workspace to build programs."
    )
    
    result = generate_detailed_blocks_summary(include_all_blocks=True)
    assert result == expected_result
