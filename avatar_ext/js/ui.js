// =========================
// UI Creation and Management
// =========================

/**
 * Create the main avatar UI
 * @returns {Object} UI elements
 */
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

  // Setup event listeners
  setupEventListeners(ttsBtn, emotionBtn, savePositionBtn, statusEl);

  return { micBtn, statusEl, ttsBtn, emotionBtn };
}

/**
 * Setup event listeners for UI buttons
 */
function setupEventListeners(ttsBtn, emotionBtn, savePositionBtn, statusEl) {
  // Add event listener for TTS test button
  ttsBtn.addEventListener("click", () => {
    window.AvatarSpeech.testTTS();
  });

  // Add event listener for Emotion test button
  emotionBtn.addEventListener("click", async () => {
    try {
      statusEl.textContent = "Testing emotion detection...";

      // Ensure WebSocket is connected
      if (!window.AvatarWebSocket.isSocketConnected()) {
        console.log("WebSocket not connected, attempting to reconnect...");
        window.AvatarWebSocket.connectWebSocket();

        // Wait a bit for connection to establish
        await new Promise((resolve) => setTimeout(resolve, 1000));

        // If still not connected, use a fallback
        if (!window.AvatarWebSocket.isSocketConnected()) {
          throw new Error("WebSocket connection failed");
        }
      }

      // Create a sample message to detect emotion from
      const testMessages = [
        "I'm so happy today!",
        "That makes me sad",
        "I'm really angry about this",
        "Wow, that's surprising!",
        "I'm afraid of what might happen",
        "That's really disgusting",
        "Just a normal day",
      ];
      const randomMessage =
        testMessages[Math.floor(Math.random() * testMessages.length)];

      // Send an emotion-only request
      window.AvatarWebSocket.sendMessage({
        type: "emotion",
        message: randomMessage,
      });

      // Show what message was used (instant for test messages)
      showSpeechInstant(`Testing emotion detection with: "${randomMessage}"`);
    } catch (err) {
      // Fallback in case of error
      console.error("Emotion test error:", err);
      statusEl.textContent = "Error testing emotion";

      // Use a random emotion as fallback
      const emotions = [
        "happy",
        "sad",
        "angry",
        "surprised",
        "fearful",
        "disgusted",
        "neutral",
      ];
      const randomEmotion =
        emotions[Math.floor(Math.random() * emotions.length)];
      window.AvatarAnimations.updateAvatarEmotion(randomEmotion);

      setTimeout(() => {
        statusEl.textContent = "Fallback: " + randomEmotion;
      }, 2000);
    }
  });

  // Add event listener for save position button
  savePositionBtn.addEventListener("click", () => {
    saveAvatarPosition(true); // Show notification when button is clicked
  });
}

/**
 * Helper function to get UI elements
 * @returns {Object} UI elements
 */
function getUIElements() {
  return {
    micBtn: document.getElementById("mic"),
    statusEl: document.getElementById("status"),
    ttsBtn: document.getElementById("tts-test"),
    emotionBtn: document.getElementById("emotion-test"),
  };
}

// Global variable to track current animation
let currentSpeechAnimation = null;

/**
 * Display speech in the avatar's speech bubble with word-by-word animation
 * @param {string} text - Text to display
 * @param {number} wordsPerSecond - Speed of word animation (default: 3)
 */
function showSpeech(text, wordsPerSecond = 3) {
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
            font-size: 16px;
            line-height: 1.6;
            cursor: default;
            font-family: 'Comic Sans MS', cursive, sans-serif;
        `;
    avatarContainer.appendChild(speechBubble);
  } else if (!speechBubble) {
    console.error("Speech bubble element not found.");
    return;
  }

  // Cancel any existing animation
  if (currentSpeechAnimation) {
    clearInterval(currentSpeechAnimation);
    currentSpeechAnimation = null;
  }

  // Show the speech bubble
  speechBubble.style.opacity = 1;

  // Convert markdown to HTML first
  const htmlContent = window.AvatarUtils.simpleMarkdownToHtml(text);

  // Extract plain text for word-by-word animation (removing HTML tags for splitting)
  const tempDiv = document.createElement("div");
  tempDiv.innerHTML = htmlContent;
  const plainText = tempDiv.textContent || tempDiv.innerText || "";

  // Split into words while preserving the HTML structure
  const words = plainText.split(/\s+/).filter((word) => word.length > 0);

  // Calculate delay between words (in milliseconds)
  const delayBetweenWords = 1000 / wordsPerSecond;

  // Clear the speech bubble and start animation
  speechBubble.innerHTML = "";

  let currentWordIndex = 0;
  let displayedText = "";

  // Add a cursor element for typing effect
  const cursor = document.createElement("span");
  cursor.style.cssText = `
    animation: blink 1s infinite;
    font-weight: bold;
    color: #3776AB;
  `;
  cursor.textContent = "|";

  // Start the word-by-word animation
  currentSpeechAnimation = setInterval(() => {
    if (currentWordIndex < words.length) {
      // Add the next word
      displayedText +=
        (currentWordIndex > 0 ? " " : "") + words[currentWordIndex];
      currentWordIndex++;

      // Convert the current text to HTML and display it
      const currentHtmlContent =
        window.AvatarUtils.simpleMarkdownToHtml(displayedText);
      speechBubble.innerHTML = currentHtmlContent;

      // Add cursor temporarily
      speechBubble.appendChild(cursor);

      // Scroll to bottom to follow the text
      speechBubble.scrollTop = speechBubble.scrollHeight;

      // Add a subtle highlight effect to the latest word
      const words_elements = speechBubble.querySelectorAll("*");
      if (words_elements.length > 0) {
        const lastElement = words_elements[words_elements.length - 2]; // -2 because cursor is last
        if (lastElement) {
          lastElement.style.animation = "wordHighlight 0.5s ease-in-out";
        }
      }
    } else {
      // Animation complete - remove cursor and clean up
      if (cursor.parentNode) {
        cursor.parentNode.removeChild(cursor);
      }
      clearInterval(currentSpeechAnimation);
      currentSpeechAnimation = null;

      // Final content update to ensure proper HTML formatting
      const finalHtmlContent = window.AvatarUtils.simpleMarkdownToHtml(text);
      speechBubble.innerHTML = finalHtmlContent;
    }
  }, delayBetweenWords);
}

/**
 * Show speech instantly (for test messages or quick responses)
 * @param {string} text - Text to display
 */
function showSpeechInstant(text) {
  showSpeech(text, 10); // Very fast animation for instant effect
}

/**
 * Save avatar position to local storage
 * @param {boolean} showNotification - Whether to show save confirmation
 */
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

/**
 * Restore avatar position from local storage
 */
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

/**
 * Toggle avatar UI visibility
 */
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

// Export functions
window.AvatarUI = {
  createAvatarUI,
  getUIElements,
  showSpeech,
  showSpeechInstant,
  saveAvatarPosition,
  restoreAvatarPosition,
  toggleAvatarUI,
};
