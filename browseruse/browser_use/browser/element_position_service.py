import json
import os
from pathlib import Path

class ElementPositionService:
    def __init__(self, base_directory: Path):
        self.base_directory = base_directory
        self.elements_dir = base_directory / "element_data"
        os.makedirs(self.elements_dir, exist_ok=True)
        
    def _get_text_content(self, element) -> str | None:
        """Extract text content from DOM nodes recursively"""
        if hasattr(element, 'innerText'):
            return element.innerText
        
        # Try to get text from node_value if it's a text node
        if hasattr(element, 'node_type') and element.node_type == 3:  # Text node
            return getattr(element, 'node_value', None)
            
        # Try to get text from children nodes
        text = []
        children = getattr(element, 'children', None) or getattr(element, 'children_nodes', [])
        if children:
            for child in children:
                child_text = self._get_text_content(child)
                if child_text:
                    text.append(child_text)
        
        return ' '.join(text) if text else None

    async def store_element_positions(self, dom_state, step_number: int) -> Path:
        """Store element positions in a JSON file"""
        filename = f"elements.json"
        file_path = self.elements_dir / filename

        element_data = {}
        if dom_state and hasattr(dom_state, 'selector_map'):
            for idx, element in dom_state.selector_map.items():
                if isinstance(element, dict):
                    bounding_box = element.get('bounding_box')
                    text_content = element.get('text_content')
                    tag_name = element.get('tag_name')
                    is_visible = element.get('is_visible')
                    element_hash = element.get('element_hash')
                else:
                    # Use absolute_position instead of bounding_box for EnhancedDOMTreeNode objects
                    bounding_box_obj = getattr(element, 'absolute_position', None)
                    # Convert DOMRect to a serializable dictionary
                    bounding_box = None
                    if bounding_box_obj:
                        bounding_box = {
                            "x": getattr(bounding_box_obj, 'x', None),
                            "y": getattr(bounding_box_obj, 'y', None),
                            "width": getattr(bounding_box_obj, 'width', None),
                            "height": getattr(bounding_box_obj, 'height', None),
                            "top": getattr(bounding_box_obj, 'top', getattr(bounding_box_obj, 'y', None)),
                            "left": getattr(bounding_box_obj, 'left', getattr(bounding_box_obj, 'x', None)),
                            "bottom": getattr(bounding_box_obj, 'bottom', None),
                            "right": getattr(bounding_box_obj, 'right', None),
                        }
                    text_content = getattr(element, 'node_value', None) or self._get_text_content(element)
                    tag_name = getattr(element, 'tag_name', None) or getattr(element, 'node_name', None)
                    is_visible = getattr(element, 'is_visible', None)
                    element_hash = getattr(element, 'element_hash', None)
                element_data[idx] = {
                    "tag_name": tag_name,
                    "text_content": text_content,
                    "bounding_box": bounding_box,
                    "is_visible": is_visible,
                    "element_hash": element_hash,
                }
        with open(file_path, 'w') as f:
            json.dump(element_data, f, indent=2)
        return file_path
