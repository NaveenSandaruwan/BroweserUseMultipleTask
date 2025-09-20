import os
import json
from dotenv import load_dotenv

load_dotenv()

# Simple agent class
class BasicScratchAgent:
    def __init__(self):
        # Load data files
        self.elements_file = os.getenv("ELEMENT_FILE_PATH")
        self.description_file = os.getenv("ELEMENTS_DESCRIPTION_JSON_PATH")
        self.load_data()
        
    def load_data(self):
        """Load Scratch blocks and categories data"""
        try:
            # Load element positions
            with open(self.elements_file, 'r') as f:
                self.elements = json.load(f)
            
            # Load category descriptions
            with open(self.description_file, 'r') as f:
                self.categories = json.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")
            self.elements = {}
            self.categories = {}
    
    def find_block(self, block_name):
        """Find a block's position by name"""
        block_name_lower = block_name.lower()
        
        # Search in elements
        for elem_id, elem_data in self.elements.items():
            text = elem_data.get('text_content', '')
            if text and block_name_lower in text.lower():
                bbox = elem_data.get('bounding_box', {})
                return {
                    'found': True,
                    'text': text,
                    'x': bbox.get('x', 0),
                    'y': bbox.get('y', 0)
                }
        
        return {'found': False, 'message': f"Can't find '{block_name}'"}
    
    def get_category_position(self, category_name):
        """Get category position"""
        for cat, info in self.categories.items():
            if category_name.lower() in cat.lower():
                coords = info.get('coordinates', 'unknown')
                return {
                    'found': True,
                    'category': cat,
                    'position': coords,
                    'blocks': len(info.get('blocks', []))
                }
        
        return {'found': False, 'message': f"Category '{category_name}' not found"}
    
    def get_workspace_blocks(self):
        """Get blocks in workspace (x > 310)"""
        workspace_blocks = []
        
        for elem_id, elem_data in self.elements.items():
            text = elem_data.get('text_content', '')
            bbox = elem_data.get('bounding_box', {})
            x = bbox.get('x', 0)
            
            # Workspace blocks are on the right side
            if text and x > 310:
                workspace_blocks.append({
                    'text': text,
                    'x': x,
                    'y': bbox.get('y', 0)
                })
        
        return workspace_blocks
    
    def answer(self, question):
        """Simple question answering"""
        question_lower = question.lower()
        
        # Check workspace code
        if 'my code' in question_lower or 'correct' in question_lower:
            blocks = self.get_workspace_blocks()
            if blocks:
                response = "Your code has these blocks:\n"
                for i, block in enumerate(blocks, 1):
                    response += f"{i}. {block['text']} at ({block['x']}, {block['y']})\n"
                response += "\nLooks good! Add more blocks to do more things!"
            else:
                response = "You don't have any blocks yet! Try dragging some from the left side."
            return response
        
        # Find specific blocks
        if 'where' in question_lower or 'find' in question_lower:
            # Extract block name (simple approach)
            words = question.split()
            for word in words:
                if len(word) > 3:  # Skip small words
                    result = self.find_block(word)
                    if result['found']:
                        return f"Found '{result['text']}' at position ({result['x']}, {result['y']})"
            return "Tell me which block you're looking for!"
        
        # Category questions
        if 'motion' in question_lower:
            result = self.get_category_position('Motion')
            if result['found']:
                return f"Motion blocks are at {result['position']}. Click there to see {result['blocks']} movement blocks!"
        
        if 'sound' in question_lower:
            result = self.get_category_position('Sound')
            if result['found']:
                return f"Sound blocks are at {result['position']}. Click there to see {result['blocks']} sound blocks!"
        
        if 'looks' in question_lower:
            result = self.get_category_position('Looks')
            if result['found']:
                return f"Looks blocks are at {result['position']}. Click there to see {result['blocks']} appearance blocks!"
        
        # How to make something
        if 'how' in question_lower or 'make' in question_lower:
            if 'move' in question_lower:
                return "To make things move: Click Motion at (x: 1, y: 93), then drag 'move steps' to the workspace!"
            if 'sound' in question_lower:
                return "To add sounds: Click Sound at (x: 1, y: 185), then drag 'play sound' to the workspace!"
            if 'loop' in question_lower or 'repeat' in question_lower:
                return "To repeat things: Click Control at (x: 1, y: 277), then drag 'repeat' or 'forever' blocks!"
            
            return "What do you want to make? I can help with movement, sounds, loops, and more!"
        
        # Navigation
        if 'click' in question_lower or 'go to' in question_lower:
            return f"I'll help you navigate! Tell me what to click: Motion, Looks, Sound, Events, Control, Sensing, Operators, or Variables?"
        
        # Default response
        return "I can help you find blocks, check your code, or learn to make things! What do you need?"

# Simple usage
if __name__ == "__main__":
    agent = BasicScratchAgent()
    
    print("Hi! I'm your Scratch helper! Ask me anything!\n")
    
    while True:
        question = input("You: ")
        
        if question.lower() in ['exit', 'quit', 'bye']:
            print("Bye! Happy coding!")
            break
        
        answer = agent.answer(question)
        print(f"Helper: {answer}\n")