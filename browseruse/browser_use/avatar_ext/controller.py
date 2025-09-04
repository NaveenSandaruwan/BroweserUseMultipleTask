import time
import json
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class AvatarController:
    def __init__(self, extension_path):
        """
        Initialize the Avatar Controller with Chrome WebDriver
        
        Args:
            extension_path (str): Full path to your Chrome extension folder
        """
        self.extension_path = extension_path
        self.driver = None
        
    # def setup_chrome(self):
    #     """
    #     Set up Chrome browser with the extension loaded
    #     """
    #     print("Setting up Chrome browser...")
        
    #     # Configure Chrome options
    #     options = Options()
        
    #     # Load your extension
    #     options.add_argument(f"--load-extension={self.extension_path}")
        
    #     # Use your existing Chrome profile (optional - remove these lines for clean profile)
    #     # options.add_argument("--user-data-dir=/path/to/chrome/profile")
    #     # options.add_argument("--profile-directory=Default")
        
    #     # Browser window settings
    #     options.add_argument("--start-maximized")        # Start with maximized window
    #     options.add_argument("--disable-notifications")  # Disable browser notifications
    #     options.add_argument("--disable-popup-blocking") # Allow popups if needed
        
    #     # Create Chrome WebDriver instance
    #     self.driver = webdriver.Chrome(options=options)
    #     print("Chrome browser started successfully!")

    def setup_chrome(self):
        print("Setting up Chrome browser...")
        options = Options()
        options.add_argument(f"--load-extension={self.extension_path}")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        
        # Add these debug options
        options.add_argument("--disable-extensions-except={self.extension_path}")
        options.add_argument("--enable-logging")
        options.add_argument("--v=1")
        
        self.driver = webdriver.Chrome(options=options)
        
        # Wait for extension to be ready
        time.sleep(2)
        print("Chrome browser started successfully!")
        
    def cdp_eval(self, expression):
        """
        Execute JavaScript code in the browser using Chrome DevTools Protocol
        
        Args:
            expression (str): JavaScript code to execute
            
        Returns:
            dict: Result from JavaScript execution
        """
        return self.driver.execute_cdp_cmd("Runtime.evaluate", {"expression": expression})
    
    def send_avatar_command(self, command_obj):
        """
        Send a command to the avatar extension
        
        Args:
            command_obj (dict): Command object with type, cmd, and parameters
        """
        # Convert Python dict to JSON string for JavaScript
        js_code = f"window.postMessage({json.dumps(command_obj)}, '*');"
        
        # Execute the JavaScript command
        result = self.cdp_eval(js_code)
        print(f"Sent command: {command_obj.get('cmd', 'unknown')}")
        return result
    
    def move_avatar(self, dx=0, dy=0):
        """Move avatar by relative amounts"""
        return self.send_avatar_command({
            "type": "AVATAR_CMD",
            "cmd": "move",
            "dx": dx,
            "dy": dy
        })
    
    def hide_avatar(self):
        """Hide the avatar"""
        return self.send_avatar_command({
            "type": "AVATAR_CMD",
            "cmd": "hide"
        })
    
    def show_avatar(self):
        """Show the avatar"""
        return self.send_avatar_command({
            "type": "AVATAR_CMD",
            "cmd": "show"
        })
    
    def center_avatar(self):
        """Center avatar on screen"""
        return self.send_avatar_command({
            "type": "AVATAR_CMD",
            "cmd": "center"
        })
    
    def rotate_avatar(self, degrees):
        """Rotate avatar by specified degrees"""
        return self.send_avatar_command({
            "type": "AVATAR_CMD",
            "cmd": "rotate",
            "deg": degrees
        })
    
    def teleport_avatar(self, x, y):
        """Move avatar to specific coordinates"""
        return self.send_avatar_command({
            "type": "AVATAR_CMD",
            "cmd": "teleport",
            "x": x,
            "y": y
        })
    
    def resize_avatar(self, size):
        """Change avatar size"""
        return self.send_avatar_command({
            "type": "AVATAR_CMD",
            "cmd": "resize",
            "size": size
        })
    
    def change_avatar_color(self, color):
        """Change avatar border color"""
        return self.send_avatar_command({
            "type": "AVATAR_CMD",
            "cmd": "color",
            "color": color
        })
    
    def demo_sequence(self):
        """
        Run a demonstration sequence of avatar movements
        """
        print("Starting avatar demonstration...")
        
        # Navigate to a webpage
        print("Loading webpage...")
        self.driver.get("https://www.google.com")
        time.sleep(3)  # Wait for page to load
        WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

        # Inject check for extension
        check_script = """
        return new Promise((resolve) => {
            let attempts = 0;
            const checkAvatar = () => {
                const avatar = document.getElementById('py-controlled-avatar');
                if (avatar) {
                    resolve(true);
                } else if (attempts < 10) {
                    attempts++;
                    setTimeout(checkAvatar, 500);
                } else {
                    resolve(false);
                }
            };
            checkAvatar();
        });
        """
        
        # Wait for avatar to be available
        max_retries = 10
        for i in range(max_retries):
            is_ready = self.driver.execute_script(check_script)
            if is_ready:
                print("Avatar is ready!")
                break
            time.sleep(0.5)
            if i == max_retries - 1:
                raise Exception("Avatar failed to initialize")
        
        # Continue with demo sequence
        
        # Show avatar
        print("Showing avatar...")
        self.show_avatar()
        time.sleep(1)
        
        # Move avatar in a square pattern
        print("Moving avatar in square pattern...")
        moves = [
            (100, 0),   # Right
            (0, 100),   # Down  
            (-100, 0),  # Left
            (0, -100)   # Up
        ]
        
        for dx, dy in moves:
            self.move_avatar(dx, dy)
            time.sleep(0.5)
        
        # Rotate avatar
        print("Rotating avatar...")
        for angle in range(0, 360, 45):
            self.rotate_avatar(angle)
            time.sleep(0.3)
        
        # Center and resize
        print("Centering and resizing avatar...")
        self.center_avatar()
        time.sleep(1)
        
        # Change size
        for size in [120, 60, 100, 80]:
            self.resize_avatar(size)
            time.sleep(0.5)
        
        # Change colors
        print("Changing avatar colors...")
        colors = ["#FF5722", "#2196F3", "#4CAF50", "#FFC107", "#9C27B0"]
        for color in colors:
            self.change_avatar_color(color)
            time.sleep(0.5)
        
        # Random movements
        print("Random movements...")
        for _ in range(10):
            dx = random.randint(-50, 50)
            dy = random.randint(-50, 50)
            self.move_avatar(dx, dy)
            time.sleep(0.3)
        
        # Final center
        self.center_avatar()
        print("Demonstration complete!")
    
    def cleanup(self):
        """Close the browser and cleanup"""
        if self.driver:
            print("Closing browser...")
            self.driver.quit()
            self.driver = None

def main():
    """
    Main function to run the avatar controller
    """
    # IMPORTANT: Update this path to match your extension folder location
    EXTENSION_PATH = "/Users/bishmajayasundara/Documents/sem 5/DS project/untitled folder/chromeExtentionControl/test"

    # Create controller instance
    controller = AvatarController(EXTENSION_PATH)
    
    try:
        # Setup Chrome browser with extension
        controller.setup_chrome()
        
        # Run the demonstration
        controller.demo_sequence()
        
        # Keep browser open for manual testing
        print("Browser will stay open for 30 seconds for manual testing...")
        print("Use arrow keys to move the avatar manually!")
        time.sleep(30)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        # Always cleanup
        controller.cleanup()
        print("Script finished!")

if __name__ == "__main__":
    main()