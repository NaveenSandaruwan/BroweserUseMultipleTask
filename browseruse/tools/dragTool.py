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
        time.sleep(delay)

# Example usage:
# toolbox = Toolbox()
# toolbox.drag_and_drop(74, 149, 400, 179)