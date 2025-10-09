// =========================
// Avatar Extension - Main Coordinator
// =========================
// This file coordinates all the different modules of the avatar extension

// Import all modules (they're loaded via script tags in manifest.json)
// All modules export their functions to window.Avatar* objects

/**
 * Initialize the avatar extension
 */
function initializeAvatarExtension() {
  console.log("Initializing Avatar Extension...");

  // 1. Initialize styles first
  window.AvatarStyles.initializeStyles();

  // 2. Initialize speech recognition
  if (!window.AvatarSpeech.initializeSpeechRecognition()) {
    alert("Speech recognition not supported in this browser");
    return;
  }

  // 3. Create the UI
  const { micBtn, statusEl, ttsBtn, emotionBtn } = window.AvatarUI.createAvatarUI();

  // 4. Setup speech recognition with UI elements
  window.AvatarSpeech.setupSpeechRecognition(micBtn, statusEl);

  // 5. Initialize WebSocket connection
  window.AvatarWebSocket.connectWebSocket();

  // 6. Make the container draggable
  const container = document.getElementById("avatar-extension-container");
  if (container) {
    window.AvatarDrag.makeDraggable(container);
    // Restore saved position if available
    window.AvatarUI.restoreAvatarPosition();
  }

  // 7. TTS initialization check (optional but good practice)
  setTimeout(() => {
    chrome.runtime.sendMessage({ action: "speak", text: "" }, (response) => {
      if (chrome.runtime.lastError) {
        console.log(
          "Background speech initialization check failed:",
          chrome.runtime.lastError.message
        );
      } else if (response && response.success) {
        console.log("Background speech system initialized successfully");
      }
    });
  }, 1000);

  console.log("Avatar Extension initialized successfully!");
}

/**
 * Handle messages from background script
 */
function setupMessageListeners() {
  // Listen for messages from background script
  chrome.runtime.onMessage.addListener((message) => {
    if (message.action === "toggleAvatarUI") {
      window.AvatarUI.toggleAvatarUI();
    }
  });
}

// =========================
// Extension Initialization
// =========================

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    setupMessageListeners();
    initializeAvatarExtension();
  });
} else {
  // DOM is already ready
  setupMessageListeners();
  initializeAvatarExtension();
}