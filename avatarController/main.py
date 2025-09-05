import asyncio
import logging
import sys
import argparse
from controller import AvatarController

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global controller reference
controller = None

# Helper function to print avatar responses in a visually appealing way
def print_avatar_response(text):
    """Print the avatar's response with visual formatting"""
    print("\n" + "🤖" * 10)
    print(f"\033[1;33m🗣️ AVATAR SAYS: \"{text}\"\033[0m")
    print("🤖" * 10 + "\n")

# Helper function to execute JavaScript code
async def execute_javascript(code):
    """Execute JavaScript code in the browser"""
    if controller:
        try:
            result = await controller.evaluate_javascript(code)
            if result is not None:
                result_text = f"JavaScript result: {result}"
                print_avatar_response(result_text)
                await controller.speak("Code executed successfully")
            else:
                await controller.speak("Code executed without return value")
        except Exception as e:
            error_message = f"JavaScript error: {str(e)}"
            print_avatar_response(error_message)
            await controller.speak("There was an error executing the JavaScript code")
    else:
        print("Controller not initialized")

# Helper function for delayed exit
async def delayed_exit():
    """Exit the program after a short delay"""
    await asyncio.sleep(2)  # Give time for speech to complete
    print("\n" + "👋" * 10)
    print("\033[1;31mExiting program as requested...\033[0m")
    print("👋" * 10 + "\n")
    # Use asyncio.get_event_loop().stop() to stop the event loop
    loop = asyncio.get_event_loop()
    loop.call_soon(loop.stop)

# Helper function for clipboard operations
async def read_and_speak_clipboard():
    """Read from clipboard and speak the contents"""
    if controller:
        clipboard_text = await controller.read_from_clipboard()
        if clipboard_text:
            # Truncate if too long
            if len(clipboard_text) > 50:
                display_text = clipboard_text[:50] + "..."
            else:
                display_text = clipboard_text
            
            response = f"Clipboard contains: {display_text}"
            print_avatar_response(response)
            await controller.speak(response)
        else:
            print_avatar_response("Clipboard is empty or access denied")
            await controller.speak("Clipboard is empty or access denied")

# Process speech input
def on_speech_received(text):
    """Process recognized speech"""
    original_text = text
    text = text.lower()
    
    # Print with colorful formatting (using ANSI escape codes)
    print("\n" + "🔊" * 20)
    print(f"\033[1;36m👂 YOU SAID: \"{text}\"\033[0m")
    print("🔊" * 20)
    
    logger.info(f"Processing speech: '{text}'")
    
    # Queue commands based on speech
    if text.startswith("move ") or (text.startswith("move to ") or "move avatar to" in text):
        # Extract coordinates (simple parsing)
        parts = text.split()
        try:
            # Handle different patterns
            if "to" in parts:
                x_idx = parts.index("to") + 1
            else:
                x_idx = 1  # Right after "move"
                
            # Skip "position" or "avatar" if present
            if x_idx < len(parts) and parts[x_idx] in ["position", "avatar"]:
                x_idx += 1
            
            # Extract X and Y coordinates
            x = int(parts[x_idx])
            y = int(parts[x_idx + 1])
            
            asyncio.create_task(controller.move_avatar(x, y))
            print_avatar_response(f"Moving to {x}, {y}")
            asyncio.create_task(controller.speak(f"Moving to {x}, {y}"))
        except (ValueError, IndexError):
            print_avatar_response("I didn't understand the coordinates")
            asyncio.create_task(controller.speak("I didn't understand the coordinates"))
    
    elif text.startswith("say "):
        # Extract text to say
        say_text = original_text[4:]  # Preserve case of original text
        print_avatar_response(say_text)
        asyncio.create_task(controller.speak(say_text))
    
    elif text.startswith("exec ") or text.startswith("execute ") or text.startswith("run "):
        # Extract code to execute
        if text.startswith("exec "):
            code = original_text[5:]
        elif text.startswith("execute "):
            code = original_text[8:]
        else:  # run
            code = original_text[4:]
            
        print_avatar_response(f"Executing JavaScript: {code}")
        asyncio.create_task(execute_javascript(code))
    
    elif text in ["exit", "quit", "close", "stop"]:
        print_avatar_response("Exiting the program. Goodbye!")
        asyncio.create_task(controller.speak("Exiting the program. Goodbye!"))
        # Add a delay before exit so the speech can be heard
        asyncio.create_task(delayed_exit())
    
    elif "hello" in text or "hi" in text or "hey" in text:
        print_avatar_response("Hello there! How can I help you?")
        asyncio.create_task(controller.speak("Hello there! How can I help you?"))
    
    elif "goodbye" in text or "bye" in text:
        print_avatar_response("Goodbye! Have a nice day!")
        asyncio.create_task(controller.speak("Goodbye! Have a nice day!"))
    
    elif "help" in text or "commands" in text or "what can you do" in text:
        help_text = "You can use these voice commands:\n" + \
                   "- 'move to X Y': Move to coordinates\n" + \
                   "- 'say TEXT': Make the avatar say something\n" + \
                   "- 'copy TEXT': Copy text to clipboard\n" + \
                   "- 'paste' or 'read clipboard': Read from clipboard\n" + \
                   "- 'exec CODE': Execute JavaScript code\n" + \
                   "- 'exit' or 'quit': Exit the program\n" + \
                   "- 'hello/goodbye': Greetings"
        print_avatar_response(help_text)
        asyncio.create_task(controller.speak("I can respond to various commands. Say help again for details."))
    
    elif text.startswith("copy "):
        # Extract text to copy
        text_to_copy = original_text[5:]  # Preserve case of original text
        if text_to_copy:
            asyncio.create_task(controller.copy_to_clipboard(text_to_copy))
            print_avatar_response(f"Copied to clipboard: {text_to_copy}")
            asyncio.create_task(controller.speak(f"Copied to clipboard"))
        else:
            print_avatar_response("Nothing to copy")
            asyncio.create_task(controller.speak("Nothing to copy"))
    
    elif "read clipboard" in text or "paste" in text or "read from clipboard" in text:
        # Read from clipboard
        asyncio.create_task(read_and_speak_clipboard())
    
    else:
        print_avatar_response(f"I heard: {original_text}, but I don't understand that command. Say 'help' for available commands.")
        asyncio.create_task(controller.speak(f"I heard you, but I don't understand that command. Say help for available commands."))

async def interactive_mode():
    """Run the avatar controller in interactive mode"""
    print("\nAvatar Controller Interactive Mode")
    print("----------------------------------")
    print("Text Commands (type here):")
    print("  move X Y - Move avatar to position X,Y")
    print("  say TEXT - Make avatar say something")
    print("  copy TEXT - Copy text to clipboard")
    print("  paste - Read from clipboard")
    print("  exec CODE - Execute JavaScript code")
    print("  exit - Exit the program")
    print("----------------------------------")
    print("Voice Commands (speak to avatar):")
    print("  'move to X Y' - Move avatar to position")
    print("  'say TEXT' - Make avatar say something")
    print("  'copy TEXT' - Copy text to clipboard")
    print("  'paste' or 'read clipboard' - Read from clipboard")
    print("  'exec CODE' - Execute JavaScript code")
    print("  'exit' or 'quit' - Exit the program")
    print("  'help' - Show available commands")
    print("----------------------------------")
    
    while True:
        try:
            command = input("\n> ")
            
            if command.lower() in ["exit", "quit", "q"]:
                break
            
            parts = command.split(maxsplit=1)
            if not parts:
                continue
                
            cmd = parts[0].lower()
            
            if cmd == "move" and len(parts) > 1:
                try:
                    coords = parts[1].split()
                    x, y = int(coords[0]), int(coords[1])
                    await controller.move_avatar(x, y)
                except (ValueError, IndexError):
                    print("Invalid coordinates. Use format: move X Y")
            
            elif cmd == "say" and len(parts) > 1:
                text = parts[1]
                await controller.speak(text)
            
            elif cmd == "copy" and len(parts) > 1:
                text = parts[1]
                success = await controller.copy_to_clipboard(text)
                if success:
                    print(f"Copied to clipboard: {text}")
                else:
                    print("Failed to copy to clipboard")
            
            elif cmd == "paste":
                text = await controller.read_from_clipboard()
                if text:
                    print(f"Clipboard content: {text}")
                else:
                    print("Failed to read from clipboard or clipboard is empty")
            
            elif cmd == "exec" and len(parts) > 1:
                js_code = parts[1]
                result = await controller.evaluate_javascript(js_code)
                print(f"Result: {result}")
            
            else:
                print(f"Unknown command: {cmd}")
        except Exception as e:
            print(f"Error: {e}")

async def main():
    global controller
    
    parser = argparse.ArgumentParser(description='Avatar Controller')
    parser.add_argument('--debugger-url', default='http://127.0.0.1:9222',
                      help='Chrome DevTools Protocol debugger URL')
    parser.add_argument('--speech-server-port', type=int, default=8000,
                      help='Port for the speech recognition server')
    parser.add_argument('--content-path', 
                      help='Path to content.js file (optional, will try to auto-detect)')
    
    args = parser.parse_args()
    
    # Create avatar controller
    controller = AvatarController(chrome_debugger_url=args.debugger_url)
    
    try:
        # Connect to Chrome
        logger.info("Connecting to Chrome...")
        try:
            connected = await controller.connect(content_path=args.content_path)
            if not connected:
                logger.error("Failed to connect to Chrome or find avatar extension")
                return
        except UnicodeDecodeError as e:
            logger.error(f"Character encoding error when reading content.js: {e}")
            logger.info("Try running with --content-path parameter to specify the correct path")
            return
        except Exception as e:
            logger.error(f"Error connecting to Chrome: {e}")
            return
        
        # Register speech callback
        controller.register_speech_callback(on_speech_received)
        
        # Start speech server
        await controller.start_speech_server(port=args.speech_server_port)
        
        # Initial position and greeting
        await controller.move_avatar(100, 100)
        greeting = "Hello! I'm your avatar assistant. Click the microphone button to speak to me."
        print("\n" + "🎉" * 10)
        print("\033[1;35m✨ AVATAR INITIALIZED ✨\033[0m")
        print_avatar_response(greeting)
        print("🎉" * 10 + "\n")
        await controller.speak(greeting)
        
        # Run interactive mode
        await interactive_mode()
    
    except KeyboardInterrupt:
        logger.info("Program interrupted by user")
    except Exception as e:
        logger.error(f"Error in main program: {e}", exc_info=True)
    finally:
        # Clean up
        if controller:
            await controller.disconnect()
        logger.info("Program terminated")



if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())