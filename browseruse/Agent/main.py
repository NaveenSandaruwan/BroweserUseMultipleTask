import asyncio
import json
import pychrome
import requests
import time
from functools import partial

class AvatarController:
    def __init__(self, debug_port=9222):
        self.debug_url = f"http://127.0.0.1:{debug_port}"
        self.browser = pychrome.Browser(url=self.debug_url)
        self.tab = None
        self.loop = None
        self.last_speech = None

    async def connect(self):
        try:
            # Store the event loop
            self.loop = asyncio.get_running_loop()
            
            # Get raw debug info
            response = requests.get(f"{self.debug_url}/json/list")
            debug_info = response.json()
            
            print("\n🔍 Available Chrome pages:")
            for info in debug_info:
                print(f"""
                Title: {info.get('title', 'Unknown')}
                Type: {info.get('type', 'Unknown')}
                URL: {info.get('url', 'Unknown')}
                ID: {info.get('id', 'Unknown')}
                """)

            # Try to find existing tab with our extension
            active_tab = None
            for info in debug_info:
                if info.get('type') == 'page' and info.get('url', '').startswith('http'):
                    active_tab = info
                    break

            if active_tab:
                # Get the tab object
                for tab in self.browser.list_tab():
                    if tab.id == active_tab['id']:
                        self.tab = tab
                        break

                if self.tab:
                    self.tab.start()
                    
                    # Enable necessary domains
                    self.tab.Runtime.enable()
                    self.tab.Page.enable()
                    
                    # Set up debug logging and speech event listener
                    self.tab.Runtime.evaluate(expression='''
                        // Debug logging
                        console.log('Python Avatar: Setting up speech listener');
                        
                        // Function to handle speech
                        function handleSpeech(event) {
                            const text = event.detail.text;
                            console.log('DEBUG: Speech event received:', text);
                            // Send direct message to Python
                            console.log('PYTHON_SPEECH_EVENT:' + text);
                        }
                        
                        // Remove existing listener if any
                        if (window._speechHandler) {
                            window.removeEventListener('pythonAvatarSpeech', window._speechHandler);
                        }
                        
                        // Add new listener
                        window._speechHandler = handleSpeech;
                        window.addEventListener('pythonAvatarSpeech', handleSpeech);
                        
                        // Debug confirmation
                        console.log('Python Avatar: Speech listener setup complete');
                    ''')
                    
                    # Add callback for console messages
                    self.tab.Runtime.consoleAPICalled = self._handle_console_message
                    
                    print(f"✓ Connected to active tab: {active_tab['url']}")
                    return True

            print("\n❌ No suitable active tab found!")
            print("\n🔧 Steps to fix:")
            print("1. Make sure Chrome is running with: --remote-debugging-port=9222")
            print("2. Open a webpage in Chrome (e.g., google.com)")
            print("3. Load your extension in chrome://extensions/")
            print("4. Enable Developer mode")
            return False

        except Exception as e:
            print(f"❌ Connection error: {str(e)}")
            return False

    def _handle_console_message(self, **kwargs):
        """Handle console messages from the browser"""
        try:
            if 'args' in kwargs:
                for arg in kwargs['args']:
                    if arg.get('type') == 'string':
                        value = arg.get('value', '')
                        
                        # Debug print for all console messages
                        print(f"Debug - Console message: {value}")
                        
                        if value.startswith('PYTHON_SPEECH_EVENT:'):
                            text = value.replace('PYTHON_SPEECH_EVENT:', '').strip()
                            if text != self.last_speech:
                                self.last_speech = text
                                print(f"\n🎤 Speech received: {text}")
                                
                                if self.loop and self.loop.is_running():
                                    self.loop.create_task(self._process_speech_async(text))
                                else:
                                    print("❌ Event loop not available")
        except Exception as e:
            print(f"❌ Error handling console message: {str(e)}")

    async def _process_speech_async(self, text):
        """Process received speech text asynchronously"""
        try:
            if text:
                print(f"🤖 Processing speech: {text}")
                await self.send_message(f"I heard: {text}")
            else:
                print("❌ Empty speech text received")
        except Exception as e:
            print(f"❌ Error processing speech: {str(e)}")

    async def send_message(self, text):
        if not self.tab:
            print("❌ Not connected to any tab")
            return

        try:
            result = self.tab.Runtime.evaluate(expression=f'''
                try {{
                    if (window.pythonAvatarControl && window.pythonAvatarControl.speak) {{
                        window.pythonAvatarControl.speak({json.dumps(text)});
                        "Message sent: " + {json.dumps(text)};
                    }} else {{
                        throw new Error("Avatar control not available");
                    }}
                }} catch (e) {{
                    console.error('Error:', e);
                    throw e;
                }}
            ''')
            print(f"✓ Message sent: {text}")
            
        except Exception as e:
            print(f"❌ Failed to send message: {str(e)}")

async def main():
    avatar = AvatarController()
    
    print("🔌 Connecting to Chrome...")
    if await avatar.connect():
        await avatar.send_message("Hello! I'm listening for your voice input.")
        
        try:
            print("\n✓ Connection established")
            print("🎤 Listening for speech... (Press Ctrl+C to exit)")
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            
        if avatar.tab:
            avatar.tab.stop()

if __name__ == "__main__":
    asyncio.run(main())