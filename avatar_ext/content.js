// =========================
// Markdown Parsing Utility
// =========================
function simpleMarkdownToHtml(markdownText) {
  if (!markdownText) return "";
  
  // 1. Convert double newlines to paragraph breaks
  let html = markdownText.replace(/\n\s*\n/g, '<p>'); 

  // 2. Simple list items (e.g., "* item")
  // This is a basic approach; more robust parsing would be needed for complex lists.
  html = html.replace(/^\s*[\-\*]\s*(.+)/gm, '<li>$1</li>');
  
  // 3. Bold (e.g., **text** or __text__)
  html = html.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
  html = html.replace(/__(.*?)__/g, '<b>$1</b>');
  
  // 4. Italics (e.g., *text* or _text_)
  html = html.replace(/\*(.*?)\*/g, '<i>$1</i>');
  html = html.replace(/_(.*?)_/g, '<i>$1</i>');

  // 5. Convert single newlines to <br> for better text flow within a block
  html = html.replace(/\n/g, '<br>');

  return html;
}


// =========================
// Create and Insert UI Elements
// =================================
function createAvatarUI() {
  // Check if UI already exists
  if (document.getElementById("avatar-extension-container")) {
      return getUIElements();
  }

  // --- Main Container (Position: Top Left) ---
  const container = document.createElement("div");
  container.id = "avatar-extension-container";
  container.style.cssText = `
      position: fixed;
      top: 20px;   /* Top-Left Positioning */
      left: 20px;  /* Top-Left Positioning */
      z-index: 10000;
      display: flex;
      flex-direction: column;
      align-items: flex-start; /* Align avatar/mic button to the left */
  `;

  // --- Avatar Graphic Element ---
  const avatar = document.createElement("div");
  avatar.id = "python-avatar";
  avatar.innerHTML = `
      <svg width="80" height="80" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
          <circle cx="40" cy="40" r="38" fill="#3776AB" />
          <circle cx="40" cy="40" r="30" fill="#FFD43B" />
          <circle cx="30" cy="30" r="8" fill="#000" />
          <circle cx="50" cy="30" r="8" fill="#000" />
          <path d="M25 50 Q40 65 55 50" stroke="#000" stroke-width="3" fill="transparent" />
      </svg>
  `;
  avatar.style.cssText = `
      width: 80px;
      height: 80px;
      border-radius: 50%;
      margin-bottom: 15px; 
      box-shadow: 0 3px 10px rgba(0,0,0,0.3);
      pointer-events: none;
  `;
  
  // --- Speech Bubble (Scrollable and fixed height/width) ---
  const speechBubble = document.createElement("div");
  speechBubble.id = "python-avatar-speech";
  speechBubble.style.cssText = `
      background: white;
      border: 2px solid #333;
      border-radius: 10px;
      padding: 8px 12px;
      max-width: 300px; 
      max-height: 250px; 
      overflow-y: auto; /* Enable vertical scrolling */
      opacity: 0; 
      transition: opacity 0.3s ease;
      /* SCROLL FIX: Removed pointer-events: none; */
      box-shadow: 0 2px 5px rgba(0,0,0,0.2);
      
      /* Positioning next to the avatar */
      position: absolute;
      top: 0;
      left: 100px; 
      font-size: 14px;
      line-height: 1.4;
      cursor: default; /* Indicates scrollability */
  `;

  // --- Mic button ---
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
      margin-bottom: 10px;
  `;

  // --- Test TTS button ---
  const ttsBtn = document.createElement("button");
  ttsBtn.id = "tts-test";
  ttsBtn.innerHTML = "🔊";
  ttsBtn.title = "Test text-to-speech";
  ttsBtn.style.cssText = `
      width: 30px;
      height: 30px;
      border-radius: 50%;
      background: #34A853;
      color: white;
      font-size: 14px;
      border: none;
      cursor: pointer;
      box-shadow: 0 2px 5px rgba(0,0,0,0.3);
  `;

  // --- Status element ---
  const statusEl = document.createElement("div");
  statusEl.id = "status";
  statusEl.style.cssText = `
      margin-top: 10px;
      font-family: Arial, sans-serif;
      font-size: 14px;
      color: #333;
  `;

  // Append elements to container
  container.appendChild(avatar); 
  container.appendChild(speechBubble);
  container.appendChild(micBtn);
  container.appendChild(ttsBtn);
  container.appendChild(statusEl);
  
  document.body.appendChild(container);

  // Add event listener for TTS test button
  ttsBtn.addEventListener("click", () => {
      statusEl.textContent = "Testing TTS...";
      speakText("Hello, this is a test of the text to speech functionality.");
  });

  return { micBtn, statusEl, ttsBtn };
}

// Helper function to get UI elements
function getUIElements() {
  return {
      micBtn: document.getElementById("mic"),
      statusEl: document.getElementById("status"),
      ttsBtn: document.getElementById("tts-test"),
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
  alert("Speech recognition not supported in this browser");
} else {
  // Create UI elements
  const { micBtn, statusEl } = createAvatarUI();

  // TTS initialization check (optional but good practice)
  setTimeout(() => {
      chrome.runtime.sendMessage({ action: "speak", text: "" }, (response) => {
          if (chrome.runtime.lastError) {
              console.log("Background speech initialization check failed:", chrome.runtime.lastError.message);
          } else if (response && response.success) {
              console.log("Background speech system initialized successfully");
          }
      });
  }, 1000);
  
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

  // Handle voice input result
  recognition.onresult = async (event) => {
      const transcript = event.results[0][0].transcript.trim();
      console.log("Heard:", transcript);
      statusEl.textContent = "Sending to LLM...";

      try {
          const response = await fetch("http://127.0.0.1:5000/speak", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ message: transcript }),
          });

          if (!response.ok) throw new Error("Network response not OK");

          const data = await response.json();
          console.log("Backend reply:", data);
          statusEl.textContent = "Reply received.";

          // Display the reply with markdown rendering
          showSpeech(data.reply); 

          // Speak the reply
          speakText(data.reply);
      } catch (err) {
          console.error("Error:", err);
          statusEl.textContent = "Error! Check console.";
          const fallbackReply = `AI says: I heard '${transcript}', but there was an error connecting to the backend.`;
          showSpeech(fallbackReply); 
          speakText(fallbackReply);
      }
  };
}

// =========================
// Avatar Bubble Functions
// =========================
function showSpeech(text) { 
  let speechBubble = document.getElementById("python-avatar-speech");
  const avatarContainer = document.getElementById("avatar-extension-container");

  if (!speechBubble && avatarContainer) {
      // Fallback/Safety creation if it wasn't there
      speechBubble = document.createElement("div");
      speechBubble.id = "python-avatar-speech";
      speechBubble.style.cssText = `
          background: white;
          border: 2px solid #333;
          border-radius: 10px;
          padding: 8px 12px;
          max-width: 300px;
          max-height: 250px;
          overflow-y: auto;
          opacity: 0;
          transition: opacity 0.3s ease;
          box-shadow: 0 2px 5px rgba(0,0,0,0.2);
          position: absolute;
          top: 0;
          left: 100px;
          font-size: 14px;
          line-height: 1.4;
          cursor: default;
      `;
      avatarContainer.appendChild(speechBubble);
  } else if (!speechBubble) {
      console.error("Speech bubble element not found.");
      return;
  }

  // APPLY MARKDOWN CONVERSION AND SET INNER HTML
  const htmlContent = simpleMarkdownToHtml(text);
  speechBubble.innerHTML = htmlContent;
  
  speechBubble.style.opacity = 1;

  // Scroll to top of the new message
  speechBubble.scrollTop = 0;
}

// =========================
// Browser TTS (Speech Synthesis)
// =========================
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
                  console.log("Speech message status:", chrome.runtime.lastError.message);
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

// =========================
// Initialization
// =========================
// Start the process of creating the UI when the script loads.
createAvatarUI();