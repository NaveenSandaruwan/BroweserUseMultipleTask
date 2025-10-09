// =========================
// Markdown Parsing Utility
// =========================
// Correct the markdown parsing function
function simpleMarkdownToHtml(markdownText) {
  if (!markdownText) return "";

  // 1. Convert double newlines to paragraph breaks
  let html = markdownText.replace(/\n\s*\n/g, "<p>");

  // 2. Simple list items
  html = html.replace(/^\s*[\*\-]\s(.+)/gm, "<li>$1</li>");

  // 3. Bold (fix the regex patterns)
  html = html.replace(/\*\*(.*?)\*\*/g, "<b>$1</b>"); // **bold**
  html = html.replace(/__(.*?)__/g, "<b>$1</b>"); // __bold__

  // 4. Italics (fix the regex patterns)
  html = html.replace(/\*(.*?)\*/g, "<i>$1</i>"); // *italic*
  html = html.replace(/_(.*?)_/g, "<i>$1</i>"); // _italic_

  // 5. Convert single newlines to <br>
  html = html.replace(/\n/g, "<br>");

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

  // --- Main Container (Position: Top Right, Draggable) ---
  const container = document.createElement("div");
  container.id = "avatar-extension-container";
  container.style.cssText = `
        position: fixed;
        top: 20px;   /* Top positioning */
        right: 20px; /* Right positioning */
        z-index: 10000;
        display: flex;
        flex-direction: column;
        align-items: flex-end; /* Align avatar/mic button to the right */
        cursor: move; /* Show move cursor */
    `;

  // --- Avatar Graphic Element with drag handle ---
  const avatar = document.createElement("div");
  avatar.id = "python-avatar";
  avatar.innerHTML = `
        <svg width="80" height="80" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
            <!-- Background circle -->
            <circle cx="40" cy="40" r="38" fill="#3776AB" />
            
            <!-- Face -->
            <circle cx="40" cy="40" r="30" fill="#FFD43B" />
            
            <!-- Eyes group -->
            <g id="eyes">
                <!-- Left eye -->
                <circle cx="30" cy="30" r="7" fill="#FFFFFF" />
                <circle id="left-pupil" cx="30" cy="30" r="4" fill="#000000" />
                
                <!-- Right eye -->
                <circle cx="50" cy="30" r="7" fill="#FFFFFF" />
                <circle id="right-pupil" cx="50" cy="30" r="4" fill="#000000" />
            </g>
            
            <!-- Eyebrows - can be animated for different emotions -->
            <path id="left-eyebrow" d="M20 22 Q30 18 35 22" stroke="#000" stroke-width="2" fill="transparent" />
            <path id="right-eyebrow" d="M45 22 Q50 18 60 22" stroke="#000" stroke-width="2" fill="transparent" />
            
            <!-- Mouth - will be animated for different emotions -->
            <path id="avatar-mouth" d="M25 50 Q40 65 55 50" stroke="#000" stroke-width="3" fill="transparent" />
        </svg>
    `;
  avatar.style.cssText = `
        width: 80px;
        height: 80px;
        border-radius: 50%;
        margin-bottom: 15px; 
        box-shadow: 0 3px 10px rgba(0,0,0,0.3);
        position: relative;
        cursor: grab; /* Show grab cursor */
    `;

  // --- Speech Bubble (Scrollable and fixed height/width) ---
  const speechBubble = document.createElement("div");
  speechBubble.id = "python-avatar-speech";
  speechBubble.style.cssText = `
        background: white;
        border: 2px solid #333;
        border-radius: 10px;
        padding: 10px 15px;
        max-width: 400px; /* Increased width from 300px */
        min-width: 300px; /* Add minimum width */
        max-height: 250px; 
        overflow-y: auto; /* Enable vertical scrolling */
        opacity: 0; 
        transition: opacity 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        
        /* Positioning to the left of the avatar */
        position: absolute;
        top: 0;
        right: 90px; /* Position to the left of the avatar */
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
        margin-right: 5px;
    `;

  // --- Emotion Test button ---
  const emotionBtn = document.createElement("button");
  emotionBtn.id = "emotion-test";
  emotionBtn.innerHTML = "🎭";
  emotionBtn.title = "Test avatar emotions";
  emotionBtn.style.cssText = `
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: #FBBC05;
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

  // Save position button
  const savePositionBtn = document.createElement("button");
  savePositionBtn.id = "save-position";
  savePositionBtn.innerHTML = "📌";
  savePositionBtn.title = "Save current position";
  savePositionBtn.style.cssText = `
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: #4285f4;
        color: white;
        font-size: 14px;
        border: none;
        cursor: pointer;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        margin-right: 5px;
    `;

  // Create a button container for all the small buttons
  const buttonContainer = document.createElement("div");
  buttonContainer.style.cssText = `
        display: flex;
        gap: 10px;
        margin-bottom: 10px;
    `;
  buttonContainer.appendChild(ttsBtn);
  buttonContainer.appendChild(emotionBtn);
  buttonContainer.appendChild(savePositionBtn);

  // Append elements to container
  container.appendChild(avatar);
  container.appendChild(speechBubble);
  container.appendChild(micBtn);
  container.appendChild(buttonContainer);
  container.appendChild(statusEl);

  document.body.appendChild(container);

  // Add event listener for TTS test button
  ttsBtn.addEventListener("click", () => {
    statusEl.textContent = "Testing TTS...";
    speakText("Hello, this is a test of the text to speech functionality.");
  });

  // Add event listener for Emotion test button
  emotionBtn.addEventListener("click", async () => {
    const emotions = [
      "happy",
      "sad",
      "angry",
      "surprised",
      "fearful",
      "disgusted",
      "neutral",
    ];
    const randomEmotion = emotions[Math.floor(Math.random() * emotions.length)];

    statusEl.textContent = "Showing: " + randomEmotion;
    updateAvatarEmotion(randomEmotion);

    // Show a message
    showSpeech(`Avatar is now feeling ${randomEmotion}`);

    // Reset status after a delay
    setTimeout(() => {
      statusEl.textContent =
        randomEmotion.charAt(0).toUpperCase() + randomEmotion.slice(1);
    }, 2000);
  });

  // Add event listener for save position button
  savePositionBtn.addEventListener("click", () => {
    saveAvatarPosition(true); // Show notification when button is clicked
  });

  return { micBtn, statusEl, ttsBtn, emotionBtn };
}

// Helper function to get UI elements
function getUIElements() {
  return {
    micBtn: document.getElementById("mic"),
    statusEl: document.getElementById("status"),
    ttsBtn: document.getElementById("tts-test"),
    emotionBtn: document.getElementById("emotion-test"),
  };
}

// Save avatar position to local storage
function saveAvatarPosition(showNotification = false) {
  const container = document.getElementById("avatar-extension-container");
  if (container) {
    const position = {
      left: container.style.left,
      top: container.style.top,
      right: container.style.right,
    };
    localStorage.setItem("avatar-position", JSON.stringify(position));

    // Show saved confirmation only if explicitly requested
    if (showNotification) {
      const statusEl = document.getElementById("status");
      if (statusEl) {
        statusEl.textContent = "Position saved!";
        setTimeout(() => {
          statusEl.textContent = "";
        }, 2000);
      }
    }
  }
}

// Restore avatar position from local storage
function restoreAvatarPosition() {
  try {
    const savedPosition = localStorage.getItem("avatar-position");
    if (savedPosition) {
      const position = JSON.parse(savedPosition);
      const container = document.getElementById("avatar-extension-container");
      if (container) {
        if (position.left) container.style.left = position.left;
        if (position.top) container.style.top = position.top;
        if (position.right && !position.left)
          container.style.right = position.right;
      }
    }
  } catch (e) {
    console.error("Error restoring avatar position:", e);
  }
}

// Function to toggle avatar UI visibility
function toggleAvatarUI() {
  const container = document.getElementById("avatar-extension-container");
  if (container) {
    container.style.display =
      container.style.display === "none" ? "flex" : "none";
  } else {
    createAvatarUI();
    restoreAvatarPosition();
  }
}

// Listen for messages from background script
chrome.runtime.onMessage.addListener((message) => {
  if (message.action === "toggleAvatarUI") {
    toggleAvatarUI();
  }
});

// =========================
// Speech Recognition & WebSocket Connection
// =========================
const SpeechRecognitionAPI =
  window.SpeechRecognition || window.webkitSpeechRecognition;

// WebSocket connection variables
let socket;
let isSocketConnected = false;

// Function to establish WebSocket connection
function connectWebSocket() {
  if (
    socket &&
    (socket.readyState === WebSocket.OPEN ||
      socket.readyState === WebSocket.CONNECTING)
  ) {
    console.log("WebSocket already connected or connecting");
    return socket;
  }

  socket = new WebSocket("ws://127.0.0.1:5000/ws");

  socket.onopen = () => {
    console.log("WebSocket connection established");
    isSocketConnected = true;
    const statusEl = document.getElementById("status");
    if (statusEl) statusEl.textContent = "Connected to AI";
  };

  socket.onclose = () => {
    console.log("WebSocket connection closed");
    isSocketConnected = false;
    const statusEl = document.getElementById("status");
    if (statusEl) statusEl.textContent = "Disconnected";
    setTimeout(connectWebSocket, 3000); // Try to reconnect after 3 seconds
  };

  socket.onerror = (error) => {
    console.error("WebSocket error:", error);
    isSocketConnected = false;
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      console.log("WebSocket message received:", data);

      if (data.reply) {
        // Display the reply with markdown rendering
        showSpeech(data.reply);

        // Speak the reply
        speakText(data.reply);
      }

      if (data.emotion) {
        // Update avatar based on received emotion
        updateAvatarEmotion(data.emotion);
      }

      const statusEl = document.getElementById("status");
      if (statusEl) statusEl.textContent = "Reply received";
    } catch (e) {
      console.error("Error processing WebSocket message:", e);
    }
  };

  return socket;
}

if (!SpeechRecognitionAPI) {
  alert("Speech recognition not supported in this browser");
} else {
  // Create UI elements
  const { micBtn, statusEl, emotionBtn } = createAvatarUI();

  // TTS initialization check (optional but good practice)
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

  // Initialize WebSocket connection
  connectWebSocket();

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
      // Ensure WebSocket is connected
      if (!isSocketConnected) {
        console.log("WebSocket not connected, attempting to reconnect...");
        connectWebSocket();

        // Wait a bit for connection to establish
        await new Promise((resolve) => setTimeout(resolve, 1000));

        // If still not connected, throw error
        if (!isSocketConnected) {
          throw new Error("WebSocket connection failed");
        }
      }

      // Send the message over WebSocket
      socket.send(JSON.stringify({ message: transcript }));

      // Note: We no longer need to handle the response here
      // The WebSocket onmessage handler will take care of it
    } catch (err) {
      console.error("Error:", err);
      statusEl.textContent = "Error! Check console.";
      const fallbackReply = `AI says: 'I heard '${transcript}', but there was an error connecting to the backend.'`;
      showSpeech(fallbackReply);
      speakText(fallbackReply);

      // Set to neutral emotion on error
      updateAvatarEmotion("neutral");
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
            padding: 10px 15px;
            max-width: 400px;
            min-width: 300px;
            max-height: 250px;
            overflow-y: auto;
            opacity: 0;
            transition: opacity 0.3s ease;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            position: absolute;
            top: 0;
            right: 90px;
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
// Emotion Detection & Avatar Updates
// =========================

// This function is no longer needed as we get emotions directly from WebSocket
// Kept as a placeholder in case we need to revert or implement local detection
function detectEmotionLocally(text) {
  console.log("Local emotion detection called - using neutral as default");
  return "neutral"; // Default emotion
}

// Function to update avatar face based on emotion
function updateAvatarEmotion(emotion) {
  const avatar = document.getElementById("python-avatar");
  if (!avatar) return;

  // Get the SVG elements
  const svgDoc = avatar.querySelector("svg");
  const mouth = svgDoc.getElementById("avatar-mouth");
  const leftEyebrow = svgDoc.getElementById("left-eyebrow");
  const rightEyebrow = svgDoc.getElementById("right-eyebrow");
  const leftPupil = svgDoc.getElementById("left-pupil");
  const rightPupil = svgDoc.getElementById("right-pupil");

  // Remove emoji indicator if it exists
  const existingIndicator = document.getElementById("emotion-indicator");
  if (existingIndicator) {
    existingIndicator.remove();
  }

  // Update SVG facial expressions based on emotion
  switch (emotion) {
    case "happy":
      mouth.setAttribute("d", "M25 50 Q40 65 55 50"); // Big smile
      leftEyebrow.setAttribute("d", "M20 22 Q30 18 35 22"); // Normal eyebrows
      rightEyebrow.setAttribute("d", "M45 22 Q50 18 60 22");
      leftPupil.setAttribute("cy", "29"); // Slightly raised pupils
      rightPupil.setAttribute("cy", "29");
      break;

    case "sad":
      mouth.setAttribute("d", "M25 55 Q40 45 55 55"); // Frown
      leftEyebrow.setAttribute("d", "M20 25 Q30 28 35 25"); // Sad eyebrows
      rightEyebrow.setAttribute("d", "M45 25 Q50 28 60 25");
      leftPupil.setAttribute("cy", "32"); // Slightly lowered pupils
      rightPupil.setAttribute("cy", "32");
      break;

    case "angry":
      mouth.setAttribute("d", "M25 55 Q40 48 55 55"); // Straight/slight frown
      leftEyebrow.setAttribute("d", "M20 20 Q30 15 35 25"); // Angry eyebrows
      rightEyebrow.setAttribute("d", "M45 25 Q50 15 60 20");
      leftPupil.setAttribute("cy", "30"); // Center pupils
      rightPupil.setAttribute("cy", "30");
      break;

    case "surprised":
      mouth.setAttribute("d", "M30 55 Q40 60 50 55"); // Small O shape
      leftEyebrow.setAttribute("d", "M20 18 Q30 13 35 18"); // Raised eyebrows
      rightEyebrow.setAttribute("d", "M45 18 Q50 13 60 18");
      leftPupil.setAttribute("cy", "28"); // Raised pupils
      rightPupil.setAttribute("cy", "28");
      break;

    case "fearful":
      mouth.setAttribute("d", "M30 55 Q40 53 50 55"); // Small straight mouth
      leftEyebrow.setAttribute("d", "M20 20 Q30 15 35 20"); // Raised eyebrows
      rightEyebrow.setAttribute("d", "M45 20 Q50 15 60 20");
      leftPupil.setAttribute("cy", "28"); // Raised pupils
      rightPupil.setAttribute("cy", "28");
      break;

    case "disgusted":
      mouth.setAttribute("d", "M25 50 Q40 45 55 52"); // Asymmetric mouth
      leftEyebrow.setAttribute("d", "M20 20 Q30 18 35 25"); // Asymmetric eyebrows
      rightEyebrow.setAttribute("d", "M45 25 Q50 15 60 20");
      leftPupil.setAttribute("cy", "31"); // Asymmetric pupils
      rightPupil.setAttribute("cy", "29");
      break;

    case "neutral":
    default:
      mouth.setAttribute("d", "M25 52 Q40 55 55 52"); // Straight mouth
      leftEyebrow.setAttribute("d", "M20 22 Q30 20 35 22"); // Normal eyebrows
      rightEyebrow.setAttribute("d", "M45 22 Q50 20 60 22");
      leftPupil.setAttribute("cy", "30"); // Center pupils
      rightPupil.setAttribute("cy", "30");
      break;
  }

  // Add subtle animation effect to the avatar
  avatar.style.transform = "scale(1.05)";
  setTimeout(() => {
    avatar.style.transform = "scale(1)";
  }, 300);
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

// =========================
// Initialization
// =========================
// Add SVG animation styles
const avatarStyles = document.createElement("style");
avatarStyles.textContent = `
  #avatar-mouth, #left-eyebrow, #right-eyebrow, #left-pupil, #right-pupil {
    transition: all 0.5s ease-in-out;
  }
  
  @keyframes blink {
    0% { transform: scaleY(1); }
    45% { transform: scaleY(1); }
    50% { transform: scaleY(0.1); }
    55% { transform: scaleY(1); }
    100% { transform: scaleY(1); }
  }
  
  #eyes {
    transform-origin: center;
    animation: blink 4s infinite;
  }
`;
document.head.appendChild(avatarStyles);

// =========================
// Drag Functionality
// =========================
function makeDraggable(container) {
  let offsetX, offsetY;
  let isDragging = false;

  // Function to handle starting drag
  function dragStart(e) {
    // Check if we're clicking on a button or interactive element
    if (e.target.tagName === "BUTTON") {
      return; // Don't start dragging if clicking buttons
    }

    // Prevent default only for mouse events, not for touch events
    if (e.type !== "touchstart") {
      e.preventDefault();
    }

    // Get the initial position
    const boundingRect = container.getBoundingClientRect();

    // Use pageX/pageY for accurate positioning with scroll
    const pageX = e.pageX || e.touches[0].pageX;
    const pageY = e.pageY || e.touches[0].pageY;

    // Calculate the offset of the mouse pointer from the top-left corner of the container
    offsetX = pageX - boundingRect.left;
    offsetY = pageY - boundingRect.top;

    isDragging = true;

    // Change cursor style
    container.style.cursor = "grabbing";

    // Add event listeners for drag and end
    if (e.type === "mousedown") {
      document.addEventListener("mousemove", dragMove);
      document.addEventListener("mouseup", dragEnd);
    } else if (e.type === "touchstart") {
      document.addEventListener("touchmove", dragMove, { passive: false });
      document.addEventListener("touchend", dragEnd);
    }
  }

  // Function to handle drag movement
  function dragMove(e) {
    if (!isDragging) return;

    // Prevent default to stop text selection during drag
    e.preventDefault();

    // Get current pointer position
    const pageX = e.pageX || e.touches[0].pageX;
    const pageY = e.pageY || e.touches[0].pageY;

    // Calculate new position (with bounds checking)
    const newLeft = pageX - offsetX;
    const newTop = pageY - offsetY;

    // Get viewport dimensions
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    // Get container dimensions
    const containerWidth = container.offsetWidth;
    const containerHeight = container.offsetHeight;

    // Keep the avatar within the viewport
    const boundedLeft = Math.max(
      0,
      Math.min(newLeft, viewportWidth - containerWidth)
    );
    const boundedTop = Math.max(
      0,
      Math.min(newTop, viewportHeight - containerHeight)
    );

    // Convert from absolute position to fixed position
    container.style.left = boundedLeft + "px";
    container.style.top = boundedTop + "px";
    container.style.right = "auto"; // Clear the right position
  }

  // Function to handle end of drag
  function dragEnd() {
    isDragging = false;

    // Change cursor back
    container.style.cursor = "move";

    // Remove event listeners
    document.removeEventListener("mousemove", dragMove);
    document.removeEventListener("mouseup", dragEnd);
    document.removeEventListener("touchmove", dragMove);
    document.removeEventListener("touchend", dragEnd);

    // Automatically save the position when drag ends
    saveAvatarPosition();

    // Show subtle visual feedback that position was saved
    const saveBtn = document.getElementById("save-position");
    if (saveBtn) {
      // Flash the save button briefly
      const originalColor = saveBtn.style.backgroundColor;
      saveBtn.style.backgroundColor = "#34A853"; // Green flash
      setTimeout(() => {
        saveBtn.style.backgroundColor = originalColor;
      }, 300);
    }
  }

  // Add event listeners for drag start
  container.addEventListener("mousedown", dragStart);
  container.addEventListener("touchstart", dragStart, { passive: true });

  return container;
}

// Start the process of creating the UI when the script loads.
const avatarUI = createAvatarUI();

// Make the avatar container draggable
const container = document.getElementById("avatar-extension-container");
if (container) {
  makeDraggable(container);
  // Restore saved position if available
  restoreAvatarPosition();
}
