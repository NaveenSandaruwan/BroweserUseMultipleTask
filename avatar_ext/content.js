// =========================
// Create and Insert UI Elements
// =========================
function createAvatarUI() {
  // Check if UI already exists
  if (document.getElementById("avatar-extension-container")) {
    return getUIElements();
  }

  // Create container
  const container = document.createElement("div");
  container.id = "avatar-extension-container";
  container.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 10000;
    display: flex;
    flex-direction: column;
    align-items: center;
  `;

  // Create mic button
  const micBtn = document.createElement("button");
  micBtn.id = "mic";
  micBtn.innerHTML = "🎤";
  micBtn.style.cssText = `
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: #4285f4;
    color: white;
    font-size: 20px;
    border: none;
    cursor: pointer;
    box-shadow: 0 2px 5px rgba(0,0,0,0.3);
  `;

  // Create status element
  const statusEl = document.createElement("div");
  statusEl.id = "status";
  statusEl.style.cssText = `
    margin-top: 10px;
    font-family: Arial, sans-serif;
    font-size: 14px;
    color: #333;
  `;

  // Append elements
  container.appendChild(micBtn);
  container.appendChild(statusEl);
  document.body.appendChild(container);

  return { micBtn, statusEl };
}

// Helper function to get UI elements
function getUIElements() {
  return {
    micBtn: document.getElementById("mic"),
    statusEl: document.getElementById("status"),
  };
}

// Function to toggle avatar UI visibility
function toggleAvatarUI() {
  const container = document.getElementById("avatar-extension-container");
  if (container) {
    container.style.display =
      container.style.display === "none" ? "flex" : "none";
  } else {
    createAvatarUI();
  }
}

// Listen for messages from background script
chrome.runtime.onMessage.addListener((message) => {
  if (message.action === "toggleAvatarUI") {
    toggleAvatarUI();
  }
});

// =========================
// Speech Recognition
// =========================
const SpeechRecognitionAPI =
  window.SpeechRecognition || window.webkitSpeechRecognition;

if (!SpeechRecognitionAPI) {
  alert("Speech recognition not supported");
} else {
  // Create UI elements
  const { micBtn, statusEl } = createAvatarUI();

  const recognition = new SpeechRecognitionAPI();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = "en-US";

  let isListening = false;

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

  // This is the part of your JavaScript code that runs after the user has finished speaking.
  recognition.onresult = async (event) => {
    const transcript = event.results[0][0].transcript.trim();
    console.log("Heard:", transcript);

    try {
      const response = await fetch("http://127.0.0.1:5000/speak", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: transcript }),
      });

      if (!response.ok) throw new Error("Network response not OK");

      // The backend's JSON response is parsed here.
      const data = await response.json();
      console.log("Backend reply:", data);

      // The reply from the backend is passed to the showSpeech function.
      showSpeech(data.reply, 6000);

      // The same reply is also passed to the function that speaks the text.
      speakText(data.reply);
    } catch (err) {
      console.error("Error:", err);
      const fallbackReply = `AI says: I heard '${transcript}'.`;
      showSpeech(fallbackReply, 4000);
      speakText(fallbackReply);
    }
  };
}

// =========================
// Avatar Bubble Functions
// =========================
function showSpeech(text, duration = 5000) {
  let speechBubble = document.getElementById("python-avatar-speech");
  const avatarContainer = document.getElementById("avatar-extension-container");

  // Create bubble if not exists
  if (!speechBubble && avatarContainer) {
    speechBubble = document.createElement("div");
    speechBubble.id = "python-avatar-speech";
    speechBubble.style.cssText = `
      background: white;
      border: 2px solid #333;
      border-radius: 10px;
      padding: 8px 12px;
      margin-top: 10px;
      max-width: 250px;
      opacity: 0;
      transition: opacity 0.3s ease;
      pointer-events: none;
      box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    `;
    avatarContainer.appendChild(speechBubble);
  }

  speechBubble.textContent = text;
  speechBubble.style.opacity = 1;

  if (duration > 0) {
    setTimeout(() => (speechBubble.style.opacity = 0), duration);
  }
}

// =========================
// Browser TTS
// =========================
function speakText(text) {
  if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel(); // stop previous speech

    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = "en-US";
    utter.pitch = 1.5; // child-like voice
    utter.rate = 1.1;

    utter.onstart = () => console.log("Speech started");
    utter.onend = () => console.log("Speech ended");
    utter.onerror = (e) => console.error("Speech error", e);

    window.speechSynthesis.speak(utter);
  } else {
    console.log("Browser TTS not supported");
  }
}
