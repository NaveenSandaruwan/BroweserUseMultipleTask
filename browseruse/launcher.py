import sys
import os
import io

def fix_windowed_mode():
    """Fix stdout/stderr issues in windowed mode"""
    if getattr(sys, 'frozen', False) and sys.stdout is None:
        # We're in a PyInstaller bundle and in windowed mode
        # Redirect stdout/stderr to prevent uvicorn logging errors
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

def main():
    # Fix windowed mode issues before doing anything else
    fix_windowed_mode()
    
    # Check for CLI argument or if running from command line with specific flags
    cli_requested = (
        len(sys.argv) > 1 and 
        (sys.argv[1] == "--cli" or sys.argv[1] == "-c" or sys.argv[1] == "cli")
    )
    
    if cli_requested:
        # Run command-line version
        try:
            from main import main as cli_main
            cli_main()
        except ImportError as e:
            print(f"Error importing CLI main: {e}")
            sys.exit(1)
    else:
        # Run GUI version by default (no console window needed)
        try:
            from gui_main import main as gui_main
            gui_main()
        except ImportError as e:
            print(f"Error importing GUI main: {e}")
            # Fallback to CLI if GUI fails
            try:
                from main import main as cli_main
                cli_main()
            except ImportError:
                print("Both GUI and CLI failed to import")
                sys.exit(1)

if __name__ == "__main__":
    main()