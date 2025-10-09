import os
import sys
import json
import socket
import time
import multiprocessing
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import queue

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from browseruse.tools.browserUseClient import send_task
from browseruse.tools.browserUseServer import start_server


class OBOJuniorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OBO JUNIOR AI - Browser Automation")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Process references
        self.server_process = None
        self.agent_process = None
        
        # Queue for thread communication
        self.message_queue = queue.Queue()
        
        # User data
        self.user_data = {}
        self.base_dir = self.get_base_dir()
        self.userdata_dir = os.path.join(self.base_dir, "userdata")
        self.userdata_file = os.path.join(self.userdata_dir, "user_data.json")
        
        # Load existing user data
        self.load_user_data()
        
        # Setup GUI
        self.setup_gui()
        
        # Start message processing
        self.process_queue()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def get_base_dir(self):
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(__file__)

    def load_user_data(self):
        if not os.path.exists(self.userdata_file):
            self.user_data = {}
            return
        try:
            with open(self.userdata_file, "r", encoding="utf-8") as f:
                self.user_data = json.load(f)
        except Exception:
            self.user_data = {}

    def save_user_data(self):
        os.makedirs(os.path.dirname(self.userdata_file), exist_ok=True)
        with open(self.userdata_file, "w", encoding="utf-8") as f:
            json.dump(self.user_data, f, indent=2)

    def setup_gui(self):
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖 OBO JUNIOR AI", font=("Arial", 24, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        subtitle_label = ttk.Label(main_frame, text="Browser Automation Assistant", font=("Arial", 12))
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 30))
        
        # Configuration Section
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        config_frame.columnconfigure(1, weight=1)
        
        # Chrome Path
        ttk.Label(config_frame, text="Chrome/Edge Path:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.chrome_path_var = tk.StringVar(value=self.user_data.get("chrome_path", ""))
        chrome_entry = ttk.Entry(config_frame, textvariable=self.chrome_path_var, width=50)
        chrome_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(config_frame, text="Browse", command=self.browse_chrome).grid(row=0, column=2)
        
        # API Key
        ttk.Label(config_frame, text="Gemini API Key:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.api_key_var = tk.StringVar(value=self.user_data.get("gemini_api_key", ""))
        api_entry = ttk.Entry(config_frame, textvariable=self.api_key_var, show="*", width=50)
        api_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        
        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="🚀 Start OBO JUNIOR AI", 
                                      command=self.start_application, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="🛑 Stop", 
                                     command=self.stop_application, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="💾 Save Config", command=self.save_config).pack(side=tk.LEFT)
        
        # Status Section
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(1, weight=1)
        
        self.status_var = tk.StringVar(value="Ready to start")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, font=("Arial", 10, "bold"))
        status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Log text area
        log_frame = ttk.Frame(status_frame)
        log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_frame, height=15, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Extension Setup Instructions
        instructions_frame = ttk.LabelFrame(main_frame, text="Extension Setup", padding="10")
        instructions_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        instructions_text = """1. Open Chrome and go to: chrome://extensions/
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the "extension" folder inside the Package directory
5. Refresh the Scratch page"""
        
        ttk.Label(instructions_frame, text=instructions_text, justify=tk.LEFT).grid(row=0, column=0, sticky=tk.W)

    def browse_chrome(self):
        filename = filedialog.askopenfilename(
            title="Select Chrome/Edge Executable",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if filename:
            self.chrome_path_var.set(filename)

    def save_config(self):
        chrome_path = self.chrome_path_var.get().strip()
        api_key = self.api_key_var.get().strip()
        
        if not chrome_path or not os.path.exists(chrome_path):
            messagebox.showerror("Error", "Please select a valid Chrome/Edge executable path")
            return
            
        if not api_key:
            messagebox.showerror("Error", "Please enter your Gemini API key")
            return
        
        # Create profile directory
        profile_dir = os.path.join(self.userdata_dir, "profile")
        os.makedirs(profile_dir, exist_ok=True)
        
        self.user_data = {
            "chrome_path": chrome_path,
            "gemini_api_key": api_key,
            "profile_dir": profile_dir
        }
        
        self.save_user_data()
        self.log_message("✅ Configuration saved successfully!")
        messagebox.showinfo("Success", "Configuration saved successfully!")

    def start_application(self):
        # Validate configuration
        if not self.validate_config():
            return
            
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Starting servers...")
        
        # Start in a separate thread to avoid blocking the GUI
        threading.Thread(target=self._start_servers, daemon=True).start()

    def validate_config(self):
        chrome_path = self.chrome_path_var.get().strip()
        api_key = self.api_key_var.get().strip()
        
        if not chrome_path or not os.path.exists(chrome_path):
            messagebox.showerror("Error", "Please select a valid Chrome/Edge executable path")
            return False
            
        if not api_key:
            messagebox.showerror("Error", "Please enter your Gemini API key")
            return False
            
        return True

    def _start_servers(self):
        try:
            # Save configuration first
            chrome_path = self.chrome_path_var.get().strip()
            api_key = self.api_key_var.get().strip()
            profile_dir = os.path.join(self.userdata_dir, "profile")
            os.makedirs(profile_dir, exist_ok=True)
            
            self.user_data = {
                "chrome_path": chrome_path,
                "gemini_api_key": api_key,
                "profile_dir": profile_dir
            }
            self.save_user_data()
            
            # Start server process
            self.message_queue.put(("log", "🚀 Starting browser server..."))
            self.server_process = multiprocessing.Process(
                target=start_server, 
                args=(chrome_path, profile_dir)
            )
            self.server_process.start()
            
            # Wait for server to be ready
            self.message_queue.put(("log", "⏳ Waiting for server to be ready..."))
            if not self.wait_for_server():
                self.message_queue.put(("error", "❌ Server failed to start"))
                return
                
            self.message_queue.put(("log", "✅ Browser server is ready"))
            
            # Send initial task
            self.message_queue.put(("log", "🌐 Opening Scratch editor..."))
            success = send_task("Go to https://scratch.mit.edu/projects/editor/?tutorial=getStarted")
            
            if success:
                self.message_queue.put(("log", "✅ Scratch editor opened successfully"))
                
                # Start agent server
                self.message_queue.put(("log", "🤖 Starting AI agent server..."))
                from browseruse.Agent.main import start_agent_server
                self.agent_process = multiprocessing.Process(target=start_agent_server)
                self.agent_process.start()
                time.sleep(2)
                
                self.message_queue.put(("log", "✅ AI agent server started"))
                self.message_queue.put(("status", "🟢 OBO JUNIOR AI is running"))
                self.message_queue.put(("log", "🎯 Ready to assist with Scratch projects!"))
            else:
                self.message_queue.put(("error", "❌ Failed to open Scratch editor"))
                
        except Exception as e:
            self.message_queue.put(("error", f"❌ Error starting application: {str(e)}"))

    def wait_for_server(self, host="127.0.0.1", port=65432, timeout=30):
        for i in range(timeout):
            try:
                with socket.create_connection((host, port), timeout=2):
                    return True
            except (OSError, ConnectionRefusedError):
                time.sleep(1)
        return False

    def stop_application(self):
        self.status_var.set("Stopping...")
        self.stop_button.config(state=tk.DISABLED)
        
        threading.Thread(target=self._stop_servers, daemon=True).start()

    def _stop_servers(self):
        try:
            self.message_queue.put(("log", "🛑 Stopping OBO JUNIOR AI..."))
            
            # Send exit command
            send_task("exit")
            time.sleep(2)
            
            # Terminate processes
            if self.server_process and self.server_process.is_alive():
                self.server_process.terminate()
                self.message_queue.put(("log", "✅ Browser server stopped"))
                
            if self.agent_process and self.agent_process.is_alive():
                self.agent_process.terminate()
                self.message_queue.put(("log", "✅ AI agent server stopped"))
                
            self.message_queue.put(("status", "Ready to start"))
            self.message_queue.put(("log", "🏁 OBO JUNIOR AI stopped successfully"))
            self.message_queue.put(("enable_start", None))
            
        except Exception as e:
            self.message_queue.put(("error", f"❌ Error stopping application: {str(e)}"))

    def log_message(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

    def process_queue(self):
        try:
            while True:
                message_type, message = self.message_queue.get_nowait()
                
                if message_type == "log":
                    self.log_message(message)
                elif message_type == "error":
                    self.log_message(message)
                    self.status_var.set("Error occurred")
                    self.start_button.config(state=tk.NORMAL)
                    self.stop_button.config(state=tk.DISABLED)
                elif message_type == "status":
                    self.status_var.set(message)
                elif message_type == "enable_start":
                    self.start_button.config(state=tk.NORMAL)
                    self.stop_button.config(state=tk.DISABLED)
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_queue)

    def on_closing(self):
        if self.server_process and self.server_process.is_alive():
            if messagebox.askokcancel("Quit", "OBO JUNIOR AI is still running. Do you want to stop it and quit?"):
                self._stop_servers()
                time.sleep(2)  # Wait for processes to stop
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    # Enable multiprocessing support for Windows
    multiprocessing.freeze_support()
    
    # Create and run GUI
    root = tk.Tk()
    
    # Set up modern theme
    style = ttk.Style()
    available_themes = style.theme_names()
    if "clam" in available_themes:
        style.theme_use("clam")
    
    a = OBOJuniorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()