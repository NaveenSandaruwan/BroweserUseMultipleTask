// =========================
// Speech Recognition & Text-to-Speech
// =========================

// Speech Recognition API
const SpeechRecognitionAPI =
  window.SpeechRecognition || window.webkitSpeechRecognition;

let recognition = null;
let isListening = false;

/**
 * Initialize speech recognition
 * @returns {boolean} True if speech recognition is supported
 */
function initializeSpeechRecognition() {
  if (!SpeechRecognitionAPI) {
    console.error("Speech recognition not supported in this browser");
    return false;
  }

  recognition = new SpeechRecognitionAPI();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = "en-US";

  return true;
}

/**
 * Setup speech recognition event handlers
 * @param {HTMLElement} micBtn - Microphone button element
 * @param {HTMLElement} statusEl - Status element
 */
function setupSpeechRecognition(micBtn, statusEl) {
  if (!recognition) return;

  micBtn.addEventListener("click", () => {
    if (isListening) recognition.stop();
    else recognition.start();
  });

  recognition.onstart = () => {
    isListening = true;
    micBtn.style.background = "#EA4335";
    statusEl.textContent = "Listening...";
  };

  recognition.onend = () => {
    isListening = false;
    micBtn.style.background = "#4285f4";
    statusEl.textContent = "";
  };

  // Handle voice input result
  recognition.onresult = async (event) => {
    const transcript = event.results[0][0].transcript.trim();
    console.log("Heard:", transcript);
    statusEl.textContent = "Processing...";

    try {
      // Ensure WebSocket is connected
      if (!window.AvatarWebSocket.isSocketConnected()) {
        console.log("WebSocket not connected, attempting to reconnect...");
        window.AvatarWebSocket.connectWebSocket();

        // Wait a bit for connection to establish
        await new Promise((resolve) => setTimeout(resolve, 1000));

        // If still not connected, throw error
        if (!window.AvatarWebSocket.isSocketConnected()) {
          throw new Error("WebSocket connection failed");
        }
      }

      // First, we detect emotion (which is faster)
      statusEl.textContent = "Detecting emotion...";

      // Send the message over WebSocket with type 'emotion'
      window.AvatarWebSocket.sendMessage({
        type: "emotion",
        message: transcript,
      });

      // Wait a short time for the emotion to be processed
      await new Promise((resolve) => setTimeout(resolve, 200));

      // Start thinking animation and send for full chat processing
      statusEl.textContent = "Getting AI response...";
      window.AvatarAnimations.startThinkingAnimation();

      window.AvatarWebSocket.sendMessage({
        type: "chat",
        message: transcript,
      });

      // Note: We no longer need to handle the response here
      // The WebSocket onmessage handler will take care of it
    } catch (err) {
      console.error("Error:", err);

      // Stop thinking animation on error
      window.AvatarAnimations.stopThinkingAnimation();

      statusEl.textContent = "Error! Check console.";
      const fallbackReply = `AI says: 'I heard '${transcript}', but there was an error connecting to the backend.'`;
      window.AvatarUI.showSpeech(fallbackReply);
      speakText(fallbackReply);

      // Set to neutral emotion on error
      window.AvatarAnimations.updateAvatarEmotion("neutral");
    }
  };
}

/**
 * Speak text using browser TTS
 * @param {string} text - Text to speak
 */
function speakText(text) {
  if (!text || text.trim() === "") {
    console.log("Empty text provided to speakText, ignoring");
    return;
  }

  const statusEl = document.getElementById("status");
  if (statusEl) {
    statusEl.textContent = "Speaking...";
  }

  try {
    // Send message to background script to handle speech synthesis
    chrome.runtime.sendMessage(
      {
        action: "speak",
        text: text,
      },
      (response) => {
        if (chrome.runtime.lastError) {
          console.log(
            "Speech message status:",
            chrome.runtime.lastError.message
          );
          return;
        }

        if (response && !response.success) {
          console.error("Background speech failed:", response.error);
          if (statusEl) {
            statusEl.textContent = "Speech failed";
            setTimeout(() => {
              statusEl.textContent = "";
            }, 3000);
          }
        }
      }
    );
  } catch (error) {
    console.error("Exception while sending speech message:", error);
  }
}

/**
 * Test TTS functionality
 */
function testTTS() {
  const statusEl = document.getElementById("status");
  if (statusEl) statusEl.textContent = "Testing TTS...";
  speakText("Hello, this is a test of the text to speech functionality.");
}

// Export functions
window.AvatarSpeech = {
  initializeSpeechRecognition,
  setupSpeechRecognition,
  speakText,
  testTTS,
};
