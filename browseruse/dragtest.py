import pychrome
import time

DEBUG_PORT = 9222
browser = pychrome.Browser(url=f"http://127.0.0.1:{DEBUG_PORT}")
tab = browser.list_tab()[0]
tab.start()
# tab.Input.enable()  <-- remove this line

def drag_and_drop(x_start, y_start, x_end, y_end, steps=10, delay=0.05):
    # Move to starting position
    tab.Input.dispatchMouseEvent(type="mouseMoved", x=x_start, y=y_start)
    time.sleep(delay)
    
    # Press mouse down
    tab.Input.dispatchMouseEvent(type="mousePressed", x=x_start, y=y_start, button="left", clickCount=1)
    time.sleep(delay)
    
    # Move to destination
    for i in range(1, steps + 1):
        x = x_start + (x_end - x_start) * i / steps
        y = y_start + (y_end - y_start) * i / steps
        tab.Input.dispatchMouseEvent(type="mouseMoved", x=x, y=y, buttons=1)
        time.sleep(delay)
    
    # Release mouse
    tab.Input.dispatchMouseEvent(type="mouseReleased", x=x_end, y=y_end, button="left", clickCount=1)
    time.sleep(delay)

# Example usage
drag_and_drop(100, 190, 400, 270)
print("Drag and drop simulated!")
