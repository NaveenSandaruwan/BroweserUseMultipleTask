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

# Process speech input
def on_speech_received(text):
    """Process recognized speech"""
    text = text.lower()
    logger.info(f"Processing speech: '{text}'")
    
    # Queue commands based on speech
    if "move" in text:
        # Extract coordinates (simple parsing)
        parts = text.split()
        try:
            # Look for patterns like "move to 100 200" or "move to position 100 200"
            x_idx = parts.index("to") + 1
            if x_idx < len(parts) and parts[x_idx] == "position":
                x_idx += 1
            
            x = int(parts[x_idx])
            y = int(parts[x_idx + 1])
            
            asyncio.create_task(controller.move_avatar(x, y))
            asyncio.create_task(controller.speak(f"Moving to {x}, {y}"))
        except (ValueError, IndexError):
            asyncio.create_task(controller.speak("I didn't understand the coordinates"))
    
    elif "hello" in text or "hi" in text:
        asyncio.create_task(controller.speak("Hello there! How can I help you?"))
    
    elif "goodbye" in text or "bye" in text:
        asyncio.create_task(controller.speak("Goodbye! Have a nice day!"))
    
    elif "help" in text:
        asyncio.create_task(controller.speak("You can ask me to move to specific coordinates by saying 'move to X Y'"))
    
    else:
        asyncio.create_task(controller.speak(f"I heard: {text}"))

async def interactive_mode():
    """Run the avatar controller in interactive mode"""
    print("\nAvatar Controller Interactive Mode")
    print("----------------------------------")
    print("Commands:")
    print("  move X Y - Move avatar to position X,Y")
    print("  say TEXT - Make avatar say something")
    print("  exec CODE - Execute JavaScript code")
    print("  exit - Exit the program")
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
    
    args = parser.parse_args()
    
    # Create avatar controller
    controller = AvatarController(chrome_debugger_url=args.debugger_url)
    
    try:
        # Connect to Chrome
        logger.info("Connecting to Chrome...")
        connected = await controller.connect()
        if not connected:
            logger.error("Failed to connect to Chrome or find avatar extension")
            return
        
        # Register speech callback
        controller.register_speech_callback(on_speech_received)
        
        # Start speech server
        await controller.start_speech_server(port=args.speech_server_port)
        
        # Initial position and greeting
        await controller.move_avatar(100, 100)
        await controller.speak("Hello! I'm your avatar assistant. Click the microphone button to speak to me.")
        
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