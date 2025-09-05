import json
import logging
import asyncio
import requests
import websockets
import aiohttp
from aiohttp import web
from typing import Optional, Dict, Any, List, Callable

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AvatarController:
    """Controller for the browser avatar extension"""
    
    def __init__(self, chrome_debugger_url: str = "http://127.0.0.1:9222"):
        """Initialize the avatar controller
        
        Args:
            chrome_debugger_url: URL for Chrome DevTools Protocol
        """
        self.chrome_debugger_url = chrome_debugger_url
        self.ws = None
        self.speech_callbacks = []
        self.web_app = None
        self.server_runner = None
        self.message_id = 0
        self.pending_commands = {}
    
    async def connect(self, content_path=None) -> bool:
        """Connect to a Chrome tab with the avatar extension running
        
        Args:
            content_path: Optional path to content.js file
        """
        try:
            # First, get list of available tabs through HTTP
            logger.info(f"Connecting to Chrome DevTools at {self.chrome_debugger_url}")
            response = requests.get(f"{self.chrome_debugger_url}/json")
            if response.status_code != 200:
                logger.error(f"Failed to connect to Chrome debugger: HTTP {response.status_code}")
                return False
            
            tabs = response.json()
            logger.info(f"Found {len(tabs)} Chrome tabs")
            
            # Find a tab to attach to
            target_tab = None
            for tab in tabs:
                if 'webSocketDebuggerUrl' in tab and tab.get('type') == 'page':
                    target_tab = tab
                    logger.info(f"Selected tab: {tab.get('title', 'Unknown')} ({tab.get('url', 'No URL')})")
                    break
            
            if not target_tab:
                logger.error("No suitable Chrome tabs found. Is Chrome running with remote debugging?")
                return False
            
            # Connect to the WebSocket
            ws_url = target_tab['webSocketDebuggerUrl']
            logger.info(f"Connecting to WebSocket: {ws_url}")
            self.ws = await websockets.connect(ws_url)
            logger.info("WebSocket connection established")
            
            # Enable necessary domains
            await self.send_command("Runtime.enable")
            await self.send_command("DOM.enable")
            await self.send_command("Page.enable")
            logger.info("Enabled CDP domains")
            
            # Check if our extension is loaded
            check_result = await self.evaluate_javascript("typeof window.pythonAvatarControl !== 'undefined'")
            
            if check_result:
                logger.info("Avatar extension detected and ready")
                return True
            else:
                logger.warning("Avatar extension not detected, injecting script")
                
                # Inject the avatar script directly
                return await self.inject_avatar_script(content_path)
                
        except Exception as e:
            logger.error(f"Error connecting to Chrome: {e}")
            return False
    
    async def send_command(self, method: str, params: Dict[str, Any] = None) -> Any:
        """Send a command to Chrome DevTools Protocol"""
        if not self.ws:
            logger.error("Not connected to Chrome")
            return None
            
        message_id = self.message_id
        self.message_id += 1
        
        message = {
            "id": message_id,
            "method": method
        }
        
        if params:
            message["params"] = params
            
        # Send the message
        message_json = json.dumps(message)
        await self.ws.send(message_json)
        
        # Wait for response
        while True:
            response = await self.ws.recv()
            response_obj = json.loads(response)
            
            if 'id' in response_obj and response_obj['id'] == message_id:
                if 'error' in response_obj:
                    logger.error(f"Command error: {response_obj['error']}")
                    return None
                return response_obj.get('result')
    
    async def evaluate_javascript(self, expression: str) -> Any:
        """Evaluate JavaScript in the browser"""
        result = await self.send_command(
            "Runtime.evaluate", 
            {"expression": expression, "returnByValue": True}
        )
        
        if result and 'result' in result:
            return result['result'].get('value')
        return None
    
    async def inject_avatar_script(self, content_path=None) -> bool:
        """Inject the avatar script directly into the page
        
        Args:
            content_path: Optional path to content.js file
        """
        try:
            import os
            
            # Use provided path if available
            if content_path and os.path.exists(content_path):
                content_file = content_path
            else:
                # Get the path to the content.js file
                # Try multiple possible locations for better compatibility
                possible_paths = [
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "avatar_ext", "content.js"),
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), "../avatar_ext/content.js"),
                    "e:\\VS CODE\\Agentic AI\\BrowserUse\\avatar_ext\\content.js"
                ]
                
                content_file = None
                for path in possible_paths:
                    if os.path.exists(path):
                        content_file = path
                        break
                
                if not content_file:
                    logger.error("Could not find content.js file")
                    return False
            
            logger.info(f"Using content script at: {content_file}")
            
            # Use utf-8 encoding to handle special characters
            with open(content_file, "r", encoding="utf-8") as f:
                avatar_script = f.read()
                
            # Inject the script
            result = await self.send_command(
                "Page.addScriptToEvaluateOnNewDocument",
                {"source": avatar_script}
            )
            
            if result:
                logger.info("Avatar script injected for future page loads")
                
                # Also execute in current page
                try:
                    eval_result = await self.send_command(
                        "Runtime.evaluate",
                        {"expression": avatar_script}
                    )
                    
                    # Verify the script was injected correctly
                    check = await self.evaluate_javascript("typeof window.pythonAvatarControl !== 'undefined'")
                except Exception as e:
                    logger.error(f"Error executing script: {e}")
                    # Try a simplified version to check if it's a syntax error
                    try:
                        await self.evaluate_javascript("console.log('Testing connection')")
                        logger.info("Basic JavaScript execution works, but avatar script has errors")
                    except:
                        logger.error("Cannot execute any JavaScript in this context")
                    return False
                if check:
                    logger.info("Avatar script successfully injected into current page")
                    return True
                else:
                    logger.error("Failed to inject avatar script into current page")
                    return False
            else:
                logger.error("Failed to inject avatar script")
                return False
                
        except FileNotFoundError:
            logger.error("Could not find content.js script file")
            return False
        except Exception as e:
            logger.error(f"Error injecting script: {e}")
            return False
    
    async def move_avatar(self, x: int, y: int) -> bool:
        """Move the avatar to the specified coordinates"""
        result = await self.evaluate_javascript(f"window.pythonAvatarControl && window.pythonAvatarControl.move({x}, {y})")
        if result:
            logger.info(f"Avatar moved to ({x}, {y})")
            return True
        else:
            logger.warning(f"Failed to move avatar to ({x}, {y})")
            return False
    
    async def speak(self, text: str, duration: int = 5000) -> bool:
        """Make the avatar speak"""
        # Escape quotes in the text
        text = text.replace('"', '\\"')
        result = await self.evaluate_javascript(f'window.pythonAvatarControl && window.pythonAvatarControl.speak("{text}", {duration})')
        if result:
            logger.info(f"Avatar says: '{text}'")
            return True
        else:
            logger.warning(f"Failed to make avatar speak: '{text}'")
            return False
    
    async def copy_to_clipboard(self, text: str) -> bool:
        """Copy text to clipboard"""
        # Escape quotes in the text
        text = text.replace('"', '\\"')
        result = await self.evaluate_javascript(f'window.pythonAvatarControl && window.pythonAvatarControl.copyToClipboard("{text}")')
        if result:
            logger.info(f"Copied to clipboard: '{text[:30]}{'...' if len(text) > 30 else ''}'")
            return True
        else:
            logger.warning(f"Failed to copy to clipboard")
            return False
    
    async def read_from_clipboard(self) -> Optional[str]:
        """Read text from clipboard"""
        result = await self.evaluate_javascript('window.pythonAvatarControl && window.pythonAvatarControl.readFromClipboard()')
        if result:
            logger.info(f"Read from clipboard: '{result[:30]}{'...' if len(result) > 30 else ''}'")
            return result
        else:
            logger.warning("Failed to read from clipboard")
            return None
    
    def register_speech_callback(self, callback: Callable[[str], None]) -> None:
        """Register callback for speech recognition"""
        self.speech_callbacks.append(callback)
    
    async def start_speech_server(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        """Start server to receive speech recognition results"""
        app = web.Application()
        
        async def handle_speech(request):
            try:
                data = await request.json()
                text = data.get('text', '')
                logger.info(f"Received speech: '{text}'")
                
                # Call registered callbacks
                for callback in self.speech_callbacks:
                    try:
                        callback(text)
                    except Exception as e:
                        logger.error(f"Error in speech callback: {e}")
                
                return web.json_response({"status": "ok"})
            except Exception as e:
                logger.error(f"Error handling speech request: {e}")
                return web.json_response({"status": "error", "message": str(e)}, status=500)
        
        app.add_routes([web.post('/speech', handle_speech)])
        
        self.web_app = app
        runner = web.AppRunner(app)
        await runner.setup()
        self.server_runner = runner
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        logger.info(f"Speech server started on http://{host}:{port}")
    
    async def stop_speech_server(self) -> None:
        """Stop the speech server"""
        if self.server_runner:
            await self.server_runner.cleanup()
            logger.info("Speech server stopped")
    
    async def disconnect(self) -> None:
        """Disconnect from Chrome and clean up"""
        if self.ws:
            try:
                await self.ws.close()
                logger.info("Disconnected from Chrome tab")
            except Exception as e:
                logger.error(f"Error disconnecting from Chrome tab: {e}")
            
            self.ws = None
        
        await self.stop_speech_server()