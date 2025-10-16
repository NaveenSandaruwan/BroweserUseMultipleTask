import sys
import os
_file_ = os.path.abspath(__file__)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(_file_), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(_file_), '../..')))

from browseruse.tools.browserUseClient import send_task
from browseruse.tools.filter import filter_json

import pychrome
import time

class Toolbox:
    def __init__(self, debug_port=9222, tab_index=0):
        self.debug_port = debug_port
        self.browser = pychrome.Browser(url=f"http://127.0.0.1:{self.debug_port}")
        self.tab = self.browser.list_tab()[tab_index]
        self.tab.start()

    def drag_and_drop(self, x_start, y_start, x_end, y_end, steps=10, delay=0.05):
        """
        Simulates a drag-and-drop mouse operation from a starting position to an ending position.
        Args:
            x_start (int or float): The starting x-coordinate of the drag.
            y_start (int or float): The starting y-coordinate of the drag.
            x_end (int or float): The ending x-coordinate of the drag.
            y_end (int or float): The ending y-coordinate of the drag.
            steps (int, optional): The number of intermediate steps between start and end positions. Defaults to 10.
            delay (float, optional): The delay in seconds between each mouse event. Defaults to 0.05.
        """
        # Move to starting position
        self.tab.Input.dispatchMouseEvent(type="mouseMoved", x=x_start, y=y_start)
        time.sleep(delay)
        
        # Press mouse down
        self.tab.Input.dispatchMouseEvent(type="mousePressed", x=x_start, y=y_start, button="left", clickCount=1)
        time.sleep(delay)
        
        # Move to destination
        for i in range(1, steps + 1):
            x = x_start + (x_end - x_start) * i / steps
            y = y_start + (y_end - y_start) * i / steps
            self.tab.Input.dispatchMouseEvent(type="mouseMoved", x=x, y=y, buttons=1)
            time.sleep(delay)
        
        # Release mouse
        self.tab.Input.dispatchMouseEvent(type="mouseReleased", x=x_end, y=y_end, button="left", clickCount=1)
        # time.sleep(delay)
        return "Drag and drop operation completed."
    
    def click(self, x, y, button="left", click_count=1, delay=0.05):
        """
        Simulates a mouse click at the specified coordinates.
        
        Args:
            x (int or float): The x-coordinate to click.
            y (int or float): The y-coordinate to click.
            button (str, optional): The mouse button to click ("left", "right", or "middle"). Defaults to "left".
            click_count (int, optional): Number of clicks (1 for single-click, 2 for double-click). Defaults to 1.
            delay (float, optional): The delay in seconds between mouse events. Defaults to 0.05.
            
        Returns:
            str: Confirmation message.
        """
        # Move to the position
        self.tab.Input.dispatchMouseEvent(type="mouseMoved", x=x, y=y)
        # time.sleep(delay)
        
        # Press mouse down
        self.tab.Input.dispatchMouseEvent(type="mousePressed", x=x, y=y, button=button, clickCount=click_count)
        # time.sleep(delay)
        
        # Release mouse up
        self.tab.Input.dispatchMouseEvent(type="mouseReleased", x=x, y=y, button=button, clickCount=click_count)
        # time.sleep(delay)
        # send_task('refresh')
        new_context = filter_json()

        return f"Click operation completed at coordinates ({x}, {y}). New context: {new_context}"
    def scroll(self, x=290, y=297, delta_x=0, delta_y=0):
        """
        Simulates a mouse wheel scroll at the specified coordinates.
        
        Args:
            x (int or float): The x-coordinate where the scroll occurs.
            y (int or float): The y-coordinate where the scroll occurs.
            delta_x (int, optional): The horizontal scroll amount. Defaults to 0.
            delta_y (int, optional): The vertical scroll amount. Defaults to -100 (scroll up).
            
        Returns:
            str: Confirmation message.
        """
        self.tab.Input.dispatchMouseEvent(type="mouseWheel", x=x, y=y, deltaX=delta_x, deltaY=delta_y)
        time.sleep(0.1)  # Small delay to ensure the scroll is registered
        return f"Scroll operation completed at coordinates ({x}, {y}) with delta ({delta_x}, {delta_y})."
# # Example usage:
# toolbox = Toolbox()
# toolbox.scroll(delta_y=405)