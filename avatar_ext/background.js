// Simple background script for Avatar Controller extension

console.log("Avatar Controller: Background script loaded");

// Listen for install event to set up initial state
chrome.runtime.onInstalled.addListener(() => {
  console.log("Avatar Controller extension installed");
});

// Listen for extension icon clicks
chrome.action.onClicked.addListener((tab) => {
  console.log("Extension icon clicked");
  // Toggle the visibility of the avatar UI
  chrome.tabs.sendMessage(tab.id, { action: "toggleAvatarUI" });
});

// Enhanced message handler with speech synthesis
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "ping") {
    sendResponse({ status: "ok", message: "Avatar extension is active" });
    return true;
  }

  // Handle speech synthesis requests
  if (message.action === "speak") {
    console.log("Background script received speak request:", message.text);

    // Check if speechSynthesis is available in the background context
    if (!("speechSynthesis" in window)) {
      console.error("Speech Synthesis API not available in background script");
      sendResponse({
        success: false,
        error: "Speech Synthesis API not available",
      });
      return true;
    }

    try {
      // Cancel any ongoing speech
      window.speechSynthesis.cancel();

      // Create utterance with the text to be spoken
      const utterance = new SpeechSynthesisUtterance(message.text);

      // Configure speech properties
      utterance.lang = "en-US";
      utterance.pitch = 1.2;
      utterance.rate = 1.0;
      utterance.volume = 1.0;

      // Send an immediate response before starting speech
      // This is crucial - respond immediately before events happen
      sendResponse({ success: true, status: "starting" });

      // Add event handlers after responding
      utterance.onstart = () => {
        console.log("Speech started in background");
      };

      utterance.onend = () => {
        console.log("Speech ended in background");
      };

      utterance.onerror = (event) => {
        console.error("Speech error in background:", event);
      };

      // Speak the text
      window.speechSynthesis.speak(utterance);

      // Chrome bug fix: keep speechSynthesis active
      const keepAlive = setInterval(() => {
        if (window.speechSynthesis.speaking) {
          window.speechSynthesis.pause();
          window.speechSynthesis.resume();
        } else {
          clearInterval(keepAlive);
        }
      }, 10000);

      return true; // Keep the sendResponse function valid
    } catch (error) {
      console.error("Error with speech synthesis in background:", error);
      sendResponse({ success: false, error: error.toString() });
      return true;
    }
  }
});
