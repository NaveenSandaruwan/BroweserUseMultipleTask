# OBO JUNIOR AI - GUI Version

## Overview

This GUI version of OBO JUNIOR AI provides a user-friendly interface for browser automation and AI assistance with Scratch projects.

## Features

- **Modern GUI Interface**: Easy-to-use graphical interface with real-time status updates
- **Configuration Management**: Save and load Chrome path and API key settings
- **Process Management**: Start/stop servers with visual feedback
- **Real-time Logging**: View application logs and status in real-time
- **Extension Setup Guide**: Built-in instructions for browser extension setup

## How to Run

### GUI Version (Default)

```bash
python gui_main.py
```

### Command Line Version

```bash
python main.py
```

### Universal Launcher

```bash
python launcher.py          # Runs GUI version
python launcher.py --cli    # Runs command-line version
```

## Setup Instructions

### 1. Configuration

1. **Chrome/Edge Path**: Click "Browse" and select your Chrome or Edge executable

   - Windows: Usually `C:\Program Files\Google\Chrome\Application\chrome.exe`
   - Or Edge: `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`

2. **Gemini API Key**: Enter your Google Gemini API key

   - Get one from: https://makersuite.google.com/app/apikey

3. Click "Save Config" to store your settings

### 2. Browser Extension Setup

1. Open Chrome/Edge and go to: `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the "extension" folder inside your Package directory
5. Refresh any Scratch pages

### 3. Start the Application

1. Click "🚀 Start OBO JUNIOR AI"
2. Wait for both servers to start (browser server and AI agent server)
3. The application will automatically open Scratch editor
4. The AI avatar extension should be visible on the page

## GUI Components

### Configuration Panel

- **Chrome/Edge Path**: Browser executable location
- **Gemini API Key**: Your AI service API key (hidden for security)
- **Browse Button**: File picker for Chrome executable
- **Save Config Button**: Persist settings to disk

### Control Panel

- **Start Button**: Launch all services
- **Stop Button**: Gracefully shutdown all processes
- **Save Config Button**: Save current configuration

### Status Panel

- **Status Indicator**: Current application state
- **Log Area**: Real-time application logs with timestamps
- **Auto-scroll**: Automatically shows latest log entries

### Extension Setup Panel

- Step-by-step instructions for browser extension installation

## Multiprocessing Architecture

The GUI safely manages multiple processes:

1. **Main Process**: GUI interface (tkinter)
2. **Browser Server Process**: Handles browser automation
3. **AI Agent Process**: Handles WebSocket communication with extension

### Process Communication

- Uses `multiprocessing.Queue` for thread-safe communication
- GUI updates via queue messages to avoid blocking
- Graceful shutdown ensures all processes are properly terminated

## Error Handling

The GUI provides comprehensive error handling:

- **Configuration Validation**: Checks paths and API keys before starting
- **Process Monitoring**: Detects failed server starts
- **Graceful Shutdown**: Properly terminates all processes on exit
- **Error Logging**: All errors are logged with timestamps

## Files Created

The application creates these files/folders:

- `userdata/user_data.json`: Stores configuration
- `userdata/profile/`: Chrome profile directory
- Various temporary files for browser automation

## Troubleshooting

### Extension Not Loading

1. Ensure Chrome path is correct
2. Check that extension folder contains `manifest.json`
3. Verify "Developer mode" is enabled in Chrome
4. Try restarting the application

### AI Not Responding

1. Check Gemini API key is valid
2. Ensure WebSocket server is running (check logs)
3. Verify extension is loaded and active

### GUI Not Responding

1. Check console for Python errors
2. Ensure all dependencies are installed
3. Try restarting the application

## Benefits of GUI Version

1. **User Friendly**: No command-line knowledge required
2. **Visual Feedback**: Real-time status and progress updates
3. **Error Prevention**: Input validation prevents common mistakes
4. **Process Management**: Easy start/stop of complex multiprocess application
5. **Configuration Persistence**: Settings saved between sessions
6. **Professional Appearance**: Modern, clean interface

## Technical Details

- **Framework**: tkinter (included with Python, no extra dependencies)
- **Threading**: Uses threading for non-blocking operations
- **Process Communication**: Queue-based message passing
- **Error Handling**: Comprehensive exception handling and user feedback
- **Cross-platform**: Works on Windows, macOS, and Linux

The GUI maintains all the functionality of the command-line version while providing a much more accessible and user-friendly experience.
