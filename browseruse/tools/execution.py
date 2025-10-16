import os
import sys
import json
import time
import pychrome
from difflib import SequenceMatcher
from dotenv import load_dotenv
from pathlib import Path

_file_ = os.path.abspath(__file__)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(_file_), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(_file_), '../..')))

from browseruse.tools.dragTool import Toolbox
from browseruse.tools.browserUseClient import send_task



drag_tool = Toolbox()
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
ELEMENTS = BASE_DIR / "element_data" / "enhanced_description.json"
# ELEMENTS = os.getenv("ELEMENTS_ENHANCED_DESCRIPTION_JSON_PATH")




class AdvancedExecutor:
    """
    Advanced executor with support for nested blocks and condition slots
    """
    
    def __init__(self, debug_port=9222, tab_index=0):
        self.debug_port = debug_port
        self.browser = pychrome.Browser(url=f"http://127.0.0.1:{self.debug_port}")
        self.tab = self.browser.list_tab()[tab_index]
        self.tab.start()
        self.nesting_stack = []  # Track current nesting context
        self.block_positions = {}  # Store positions of placed blocks
        self.current_nesting_level = 0
        
    @staticmethod
    def load_enhanced_descriptions():
        """Load enhanced description file with nesting metadata"""
        description_path = BASE_DIR / "element_data" / "description.json"
        # print(f"Loading enhanced descriptions from: {description_path}")
        try:
            with open(description_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading descriptions: {e}")
            return {}
    
    def get_block_metadata(self, category, block_name, descriptions):
        """
        Find block metadata from descriptions
        
        Returns:
            dict: Block metadata including nesting info
        """
        if category not in descriptions:
            return {}
            
        for block in descriptions[category].get("blocks", []):
            ratio = SequenceMatcher(
                None, block["name"].lower(), block_name.lower()
            ).ratio()
            if ratio > 0.6:
                return block
        return {}
    
    def calculate_position(self, step_data, descriptions):
        """
        Calculate X,Y coordinates based on placement type and nesting
        
        Args:
            step_data: Step with placement and parent info
            descriptions: Enhanced descriptions
            
        Returns:
            tuple: (x_end, y_end)
        """
        placement = step_data.get("placement", "below")
        parent_step = step_data.get("parent_step")
        category = step_data["category"]
        block_name = step_data["block"]
        step_num = step_data["step"]
        
        # Get metadata for this block
        block_meta = self.get_block_metadata(category, block_name, descriptions)
        
        # Base workspace coordinates
        base_x = 350
        base_y = 140
        standard_spacing = 37  # Vertical spacing between blocks
        
        print(f"  Calculating position for: {block_name}")
        print(f"  Placement: {placement}, Parent: {parent_step}")
        
        if placement == "root":
            # Root level - first block
            x_end = base_x
            y_end = base_y
            self.nesting_stack = [(step_num, x_end, y_end, 0)]
            self.current_nesting_level = 0
            
        elif placement == "below":
            # Directly below previous block
            if self.nesting_stack:
                last_step, last_x, last_y, last_level = self.nesting_stack[-1]
                x_end = last_x
                y_end = last_y + standard_spacing
                self.nesting_stack.append((step_num, x_end, y_end, last_level))
            else:
                x_end = base_x
                y_end = base_y
                self.nesting_stack = [(step_num, x_end, y_end, 0)]
                
        elif placement == "inside":
            # Inside a container block
            if parent_step and parent_step in self.block_positions:
                parent_pos = self.block_positions[parent_step]
                parent_meta = parent_pos.get("metadata", {})
                
                # Get nesting offsets from parent
                x_offset = parent_meta.get("nesting_offset_x", 11)
                y_offset = parent_meta.get("nesting_offset_y", 35)
                
                # Check if there are already blocks inside this container
                siblings_inside = [
                    pos for pos in self.block_positions.values()
                    if pos.get("parent_step") == parent_step 
                    and pos.get("placement") == "inside"
                    and pos.get("step") != step_num
                ]
                
                if siblings_inside:
                    # Stack below existing blocks inside container
                    last_sibling = max(siblings_inside, key=lambda b: b["y"])
                    x_end = last_sibling["x"]
                    y_end = last_sibling["y"] + standard_spacing
                else:
                    # First block inside container
                    x_end = parent_pos["x"] + x_offset
                    y_end = parent_pos["y"] + y_offset
                
                self.current_nesting_level = parent_pos.get("nesting_level", 0) + 1
                self.nesting_stack.append((step_num, x_end, y_end, self.current_nesting_level))
                
            else:
                # Fallback if parent not found
                x_end = base_x + 11
                y_end = base_y + 35
                self.nesting_stack.append((step_num, x_end, y_end, 1))
                
        elif placement == "condition":
            # In a condition slot (diamond/hexagon)
            if parent_step and parent_step in self.block_positions:
                parent_pos = self.block_positions[parent_step]
                parent_meta = parent_pos.get("metadata", {})
                
                # Get condition slot offsets
                cond_x_offset = parent_meta.get("condition_offset_x", 60)
                cond_y_offset = parent_meta.get("condition_offset_y", 5)
                
                x_end = parent_pos["x"] + cond_x_offset
                y_end = parent_pos["y"] + cond_y_offset
                
                # Condition blocks don't change nesting stack
            else:
                x_end = base_x + 60
                y_end = base_y + 5
                
        elif placement == "outside":
            # Exit container, return to parent's level
            if parent_step and parent_step in self.block_positions:
                parent_pos = self.block_positions[parent_step]
                parent_level = parent_pos.get("nesting_level", 0)
                
                # Find last block at parent level
                parent_level_blocks = [
                    pos for pos in self.block_positions.values()
                    if pos.get("nesting_level") == parent_level
                ]
                
                if parent_level_blocks:
                    last_at_level = max(parent_level_blocks, key=lambda b: b["y"])
                    x_end = last_at_level["x"]
                    y_end = last_at_level["y"] + standard_spacing + 35  # Extra space for container bottom
                else:
                    x_end = parent_pos["x"]
                    y_end = parent_pos["y"] + 70
                
                self.current_nesting_level = parent_level
                self.nesting_stack.append((step_num, x_end, y_end, parent_level))
            else:
                # Fallback
                if self.nesting_stack:
                    self.nesting_stack.pop()
                if self.nesting_stack:
                    last_step, last_x, last_y, last_level = self.nesting_stack[-1]
                    x_end = last_x
                    y_end = last_y + 70
                else:
                    x_end = base_x
                    y_end = base_y + 70
        else:
            # Default: treat as below
            x_end = base_x
            y_end = base_y
        
        print(f"  Position calculated: ({x_end}, {y_end})")
        return x_end, y_end
    
    @staticmethod
    def find_closest_block(category, block_query, descriptions):
        """Find block using fuzzy matching"""
        if category not in descriptions:
            return None
            
        best_match = None
        highest_ratio = 0
        
        for block in descriptions[category].get("blocks", []):
            ratio = SequenceMatcher(
                None, block["name"].lower(), block_query.lower()
            ).ratio()
            
            if ratio > highest_ratio and ratio > 0.6:
                highest_ratio = ratio
                best_match = block
        
        if best_match:
            coords = best_match["coordinates"]
            x = float(coords.split("x: ")[1].split(",")[0])
            y = float(coords.split("y: ")[1])
            
            return {
                "name": best_match["name"],
                "description": best_match["description"],
                "coordinates": {"x": x, "y": y},
                "metadata": best_match
            }
        return None
    def load_categories(self):
        """Load category data from elements file"""
        try:
            with open(ELEMENTS, 'r') as f:
                # print(f"Loading category data from: {ELEMENTS}")
                return json.load(f)
            
        except Exception as e:
            print(f"Error loading category data: {e}")
            return {}
    
    def execute_with_nesting(self, json_plan, delay=0.5):
        """
        Execute blocks with full nesting support
        
        Args:
            json_plan: JSON string with enhanced step format
            delay: Delay between operations
            
        Returns:
            str: Success message
        """
        try:
            plan = json.loads(json_plan)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
            return "❌ Invalid JSON plan."
        
        steps = plan.get("steps", [])
        descriptions = self.load_enhanced_descriptions()
        category_data = self.load_categories()

        # print(f"Loaded category data: {category_data}")
        # print(f"Loaded {descriptions} categories from descriptions.")
        print(f"\n{'='*60}")
        print(f"ADVANCED EXECUTOR - Processing {len(steps)} steps")
        print(f"{'='*60}\n")
        
        for step in steps:
            step_num = step["step"]
            category = step["category"]
            block_name = step["block"]
            placement = step.get("placement", "below")
            
            print(f"\n[Step {step_num}] {block_name}")
            
            # Find block in palette
            match = self.find_closest_block(category, block_name, descriptions)
            if not match:
                print(f"❌ Could not find block '{block_name}' in category '{category}'")
                continue
            
            start = match["coordinates"]
            x_start, y_start = start["x"], start["y"]
            
            # Calculate end position with nesting
            x_end, y_end = self.calculate_position(step, descriptions)
            
            # Store block position for reference
            block_meta = self.get_block_metadata(category, block_name, descriptions)
            self.block_positions[step_num] = {
                "step": step_num,
                "x": x_end,
                "y": y_end,
                "placement": placement,
                "parent_step": step.get("parent_step"),
                "nesting_level": self.current_nesting_level,
                "metadata": block_meta
            }

            
            # Click category tab
            category_position = category_data.get(category, {}).get("coordinates", "x: 0, y: 0")
            print(f"path {ELEMENTS}  Clicking category '{category}' at {category_position}")
            category_x, category_y = map(int, category_position.replace("x: ", "").replace("y: ", "").split(", "))
            drag_tool.click(category_x, category_y + 5)
            
            time.sleep(delay)
            
            # Drag and drop
            print(f"  Dragging from ({x_start}, {y_start}) to ({x_end}, {y_end})")
            drag_tool.drag_and_drop(
                x_start=x_start,
                y_start=y_start,
                x_end=x_end,
                y_end=y_end
            )
            
            time.sleep(delay)
        
        print(f"\n{'='*60}")
        print("✅ ADVANCED EXECUTION COMPLETED")
        print(f"{'='*60}\n")
        
        return "✅ Execution completed."
    
    @staticmethod
    def clean_workspace():
        """Clean workspace before execution"""
        from browseruse.tools.filter import find_used_blocks
        
        print("🧹 Cleaning workspace...")
        used_blocks = find_used_blocks()
        
        if not used_blocks or len(used_blocks) == 0:
            print("✓ Workspace is already empty")
            return True
        
        print(f"Found {len(used_blocks)} blocks to remove")
        
        for i, block in enumerate(used_blocks, 1):
            try:
                x_current = block["x"]
                y_current = block["y"]
                x_target = 100
                y_target = 300
                
                print(f"  Removing block {i}/{len(used_blocks)}: '{block['text_content']}'")
                
                drag_tool.drag_and_drop(
                    x_start=x_current,
                    y_start=y_current,
                    x_end=x_target,
                    y_end=y_target
                )
                
                time.sleep(0.3)
            except Exception as e:
                print(f"  ⚠ Error removing block: {e}")
                continue
        
        print("✓ Workspace cleaned successfully")
        return True
    
    def clean_and_execute(self, json_plan, delay=0.5):
        """Clean workspace then execute with nesting"""
        print("\n" + "="*60)
        print("🔧 CLEAN & EXECUTE WITH NESTING")
        print("="*60)
        
        # Clean
        print("\n[STEP 1] Cleaning workspace...")
        try:
            self.clean_workspace()
            time.sleep(1)
        except Exception as e:
            print(f"⚠ Error during cleanup: {e}")
        
        # Refresh
        print("\n[STEP 2] Refreshing...")
        try:
            send_task("refresh")
            time.sleep(2)
        except Exception as e:
            print(f"⚠ Error refreshing: {e}")
        
        # Execute
        print("\n[STEP 3] Executing with nesting...")
        result = self.execute_with_nesting(json_plan, delay)
        
        return result