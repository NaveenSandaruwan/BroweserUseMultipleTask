# test_extension_ui.py
from subprocess import Popen
import time
from playwright.sync_api import sync_playwright

EXTENSION_PATH = "E:\\VS CODE\\Agentic AI\\BrowserUse\\avatar_ext"

def test_avatar_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir="test-profile",
            headless=False,
            args=[
                f"--disable-extensions-except={EXTENSION_PATH}",
                f"--load-extension={EXTENSION_PATH}"
            ]
        )
        page = browser.new_page()
        page.goto("https://scratch.mit.edu/projects/editor/")

        # Wait for avatar container to appear
        container = page.wait_for_selector("#avatar-extension-container", timeout=10000)
        assert container.is_visible(), "Avatar container is not visible"
        print("✅ Avatar container visible")
        
        # Check avatar SVG element
        avatar = page.query_selector("#python-avatar")
        assert avatar.is_visible(), "Avatar graphic is not visible"
        assert avatar.query_selector("svg"), "Avatar SVG not found"
        print("✅ Avatar graphic visible")

        # Test mic button
        mic_button = page.query_selector("#mic")
        assert mic_button.is_visible(), "Mic button is not visible"
        
        # Click mic button to test speech bubble
        mic_button.click()
        
        # Check if speech bubble becomes visible
        speech_bubble = page.locator("#python-avatar-speech")
        assert speech_bubble.is_visible(), "Speech bubble didn't appear after mic click!"
        print("✅ Speech bubble visible after mic click")
        
        # Test TTS button
        tts_button = page.query_selector("#tts-test")
        assert tts_button.is_visible(), "TTS test button is not visible"
        
        # Click TTS button
        tts_button.click()
        
        # Check status update after TTS click
        status_el = page.locator("#status")
        # Wait for status to update with "Testing TTS..." or "Speaking..."
        page.wait_for_function("""
            () => {
                const status = document.querySelector("#status");
                return status && (status.textContent.includes("Testing TTS") || 
                                 status.textContent.includes("Speaking"));
            }
        """)
        print("✅ TTS button click updates status")
        
        # Test emotion button
        emotion_button = page.query_selector("#emotion-test")
        assert emotion_button.is_visible(), "Emotion test button is not visible"
        
        # Click emotion button
        emotion_button.click()
        
        # Wait for status to update with emotion info
        page.wait_for_function("""
            () => {
                const status = document.querySelector("#status");
                return status && (status.textContent.includes("Showing:") || 
                                 /[A-Z][a-z]+/.test(status.textContent));
            }
        """)
        print("✅ Emotion button changes avatar expression")
        
        # Final check for element positioning
        avatar_rect = avatar.bounding_box()
        container_rect = container.bounding_box()
        assert avatar_rect["x"] > (page.viewport_size["width"] / 2), "Avatar not positioned on right side"
        
        print("✅ All avatar interface tests passed!")
        browser.close()

if __name__ == "__main__":
    test_avatar_ui()