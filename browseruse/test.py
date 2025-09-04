import pychrome
import requests
import json

DEBUG_PORT = 8093

# Get available targets (tabs, extension pages, etc.)
targets = requests.get(f"http://127.0.0.1:{DEBUG_PORT}/json").json()

# Pick the first normal webpage tab (where your content.js is injected)
tab_info = next(t for t in targets if t["type"] == "page" and t["url"].startswith("http"))
print("Using tab:", tab_info["url"])

# Attach to that tab
browser = pychrome.Browser(url=f"http://127.0.0.1:{DEBUG_PORT}")
tab = browser.list_tab()[0]   # or use browser.list_tab()[id] if needed
tab.start()
tab.Runtime.enable()

def send_avatar_cmd(cmd, **kwargs):
    """Send a command to the avatar via postMessage."""
    message = {
        "type": "AVATAR_CMD",
        "cmd": cmd,
        **kwargs
    }
    js_code = f"window.postMessage({json.dumps(message)}, '*');"
    tab.Runtime.evaluate(expression=js_code)

# === Example Commands ===
send_avatar_cmd("move", dx=50, dy=0)       # move right
send_avatar_cmd("move", dx=0, dy=50)       # move down
send_avatar_cmd("center")                  # center on screen
send_avatar_cmd("resize", size=120)        # resize avatar
send_avatar_cmd("color", color="red")      # change border color
send_avatar_cmd("teleport", x=200, y=100)  # jump to coords
send_avatar_cmd("rotate", deg=45)          # rotate avatar
send_avatar_cmd("hide")                    # hide avatar
send_avatar_cmd("show")                    # show avatar

print("Commands sent to avatar!")
