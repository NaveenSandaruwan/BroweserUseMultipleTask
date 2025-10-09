import sys
import os

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        # Run command-line version
        from main import main as cli_main
        cli_main()
    else:
        # Run GUI version by default
        from gui_main import main as gui_main
        gui_main()

if __name__ == "__main__":
    main()