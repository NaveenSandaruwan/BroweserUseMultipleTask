// Avatar controller content script

// Create and inject avatar elements
function createAvatar() {
  // Check if avatar already exists
  if (document.getElementById("python-avatar-container")) {
    console.log("Python Avatar: Avatar already exists");
    return;
  }

  // Create the avatar container
  const avatarContainer = document.createElement("div");
  avatarContainer.id = "python-avatar-container";
  avatarContainer.style.cssText = `
    position: fixed;
    top: 100px;
    left: 100px;
    z-index: 10000;
    display: flex;
    flex-direction: column;
    align-items: center;
    pointer-events: none;
    transition: all 0.3s ease;
  `;

  // Create the avatar image - use inline SVG instead of external image for reliability
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
    pointer-events: none;
    transition: all 0.3s ease;
    box-shadow: 0 3px 10px rgba(0,0,0,0.3);
  `;

  // Create speech bubble
  const speechBubble = document.createElement("div");
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

  // Create microphone button
  const micButton = document.createElement("button");
  micButton.id = "python-avatar-mic";
  micButton.innerHTML = "🎤";
  micButton.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: #4285f4;
    color: white;
    font-size: 20px;
    border: none;
    cursor: pointer;
    z-index: 10001;
    box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    transition: all 0.2s ease;
  `;
  // Add hover effect
  micButton.onmouseover = () => {
    micButton.style.transform = "scale(1.1)";
  };
  micButton.onmouseout = () => {
    micButton.style.transform = "scale(1)";
  };

  // Create mic status indicator
  const micStatus = document.createElement("div");
  micStatus.id = "python-avatar-mic-status";
  micStatus.style.cssText = `
    position: fixed;
    bottom: 75px;
    right: 20px;
    padding: 5px 10px;
    background: rgba(0,0,0,0.7);
    color: white;
    border-radius: 5px;
    font-size: 12px;
    opacity: 0;
    transition: opacity 0.3s ease;
    z-index: 10001;
  `;

  // Create test button for permissions
  const testButton = document.createElement("button");
  testButton.id = "python-avatar-test";
  testButton.innerHTML = "🔍";
  testButton.title = "Test microphone permissions";
  testButton.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 80px;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #34A853;
    color: white;
    font-size: 18px;
    border: none;
    cursor: pointer;
    z-index: 10001;
    box-shadow: 0 2px 5px rgba(0,0,0,0.3);
  `;

  // Add click handler for testing permissions
  testButton.addEventListener("click", async () => {
    micStatus.textContent = "Checking permissions...";
    micStatus.style.opacity = 1;

    try {
      // Request microphone permissions directly
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      console.log("Python Avatar: Microphone permission granted", stream);
      micStatus.textContent = "Microphone permission: ✅ Granted";

      // Release the tracks
      stream.getTracks().forEach((track) => track.stop());

      // Update UI after checking
      setTimeout(() => {
        micStatus.style.opacity = 0;
      }, 3000);
    } catch (err) {
      console.error("Python Avatar: Microphone permission error", err);
      micStatus.textContent = `Microphone permission: ❌ ${err.name}`;
      setTimeout(() => {
        micStatus.style.opacity = 0;
      }, 3000);
    }
  });

  // Append elements
  avatarContainer.appendChild(avatar);
  avatarContainer.appendChild(speechBubble);
  document.body.appendChild(avatarContainer);
  document.body.appendChild(micButton);
  document.body.appendChild(testButton);
  document.body.appendChild(micStatus);

  // Set up speech recognition
  setupSpeechRecognition(micButton, micStatus);

  console.log("Python Avatar: Avatar initialized and ready for commands");
  return true;
}

// Handle speech recognition
function setupSpeechRecognition(micButton, micStatus) {
  // Try to use the standard SpeechRecognition first, then fall back to webkitSpeechRecognition
  const SpeechRecognitionAPI =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognitionAPI) {
    console.error(
      "Python Avatar: Speech recognition not supported in this browser"
    );
    micStatus.textContent = "Speech recognition not supported";
    micStatus.style.opacity = 1;
    setTimeout(() => {
      micStatus.style.opacity = 0;
    }, 3000);
    return;
  }

  // Log that we found the API
  console.log(
    "Python Avatar: Speech recognition API found",
    SpeechRecognitionAPI.name || "SpeechRecognition"
  );

  const recognition = new SpeechRecognitionAPI();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = "en-US";

  let isListening = false;

  micButton.addEventListener("click", () => {
    if (isListening) {
      recognition.stop();
    } else {
      recognition.start();
      micStatus.textContent = "Listening...";
      micStatus.style.opacity = 1;
    }
  });

  recognition.onstart = () => {
    console.log("Python Avatar: Speech recognition started");
    isListening = true;
    micButton.style.background = "#EA4335"; // Red when recording
    micStatus.textContent = "Listening...";
    micStatus.style.opacity = 1;
  };

  recognition.onend = () => {
    console.log("Python Avatar: Speech recognition ended");
    isListening = false;
    micButton.style.background = "#4285f4"; // Blue when not recording
    setTimeout(() => {
      micStatus.style.opacity = 0;
    }, 1000);
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    console.log("Python Avatar: Speech recognized:", transcript);

    // Send the result to the Python controller
    micStatus.textContent = `"${transcript}"`;

    // Use custom event for reliable communication
    const speechEvent = new CustomEvent("pythonAvatarSpeech", {
      detail: { text: transcript },
    });
    window.dispatchEvent(speechEvent);

    // Also use fetch API as a backup
    fetch("http://localhost:8000/speech", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: transcript }),
    }).catch((err) => {
      console.error("Error sending speech to Python:", err);
      // Don't update UI here since we're using both methods
    });
  };

  recognition.onerror = (event) => {
    console.error("Python Avatar: Recognition error", event.error);
    micStatus.textContent = `Error: ${event.error}`;
    micStatus.style.opacity = 1;
    setTimeout(() => {
      micStatus.style.opacity = 0;
    }, 3000);
    isListening = false;
    micButton.style.background = "#4285f4";

    // Additional logging for different error types
    switch (event.error) {
      case "not-allowed":
        console.error("Python Avatar: Microphone permission denied");
        micStatus.textContent = "Microphone permission denied";
        break;
      case "no-speech":
        console.error("Python Avatar: No speech detected");
        micStatus.textContent = "No speech detected";
        break;
      case "audio-capture":
        console.error("Python Avatar: Audio capture failed");
        micStatus.textContent = "Audio capture failed";
        break;
      case "network":
        console.error("Python Avatar: Network error");
        micStatus.textContent = "Network error";
        break;
      case "aborted":
        console.log("Python Avatar: Recognition aborted");
        micStatus.textContent = "Recognition stopped";
        break;
    }
  };
}

// Function to move avatar to specific coordinates
function moveAvatar(x, y) {
  const avatarContainer = document.getElementById("python-avatar-container");
  if (avatarContainer) {
    avatarContainer.style.left = `${x}px`;
    avatarContainer.style.top = `${y}px`;
    console.log(`Python Avatar: Moved to (${x}, ${y})`);
    return true;
  }
  return false;
}

// Function to display speech bubble
function showSpeech(text, duration = 5000) {
  const speechBubble = document.getElementById("python-avatar-speech");
  if (speechBubble) {
    speechBubble.textContent = text;
    speechBubble.style.opacity = 1;
    console.log(`Python Avatar: Says "${text}"`);

    if (duration > 0) {
      setTimeout(() => {
        speechBubble.style.opacity = 0;
      }, duration);
    }
    return true;
  }
  return false;
}

// Initialize avatar when the page is loaded
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", createAvatar);
} else {
  createAvatar();
}

// Function to handle clipboard operations safely
async function handleClipboard(text, operation = "copy") {
  try {
    if (operation === "copy") {
      await navigator.clipboard.writeText(text);
      console.log("Python Avatar: Text copied to clipboard successfully");
      return true;
    } else if (operation === "read") {
      const clipText = await navigator.clipboard.readText();
      console.log("Python Avatar: Text read from clipboard");
      return clipText;
    }
  } catch (err) {
    console.error("Python Avatar: Clipboard operation failed:", err);
    // Try fallback method for copying
    if (operation === "copy") {
      try {
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed"; // Prevent scrolling to bottom
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        const successful = document.execCommand("copy");
        document.body.removeChild(textArea);
        if (successful) {
          console.log("Python Avatar: Text copied using fallback method");
          return true;
        } else {
          console.error("Python Avatar: Fallback clipboard copy failed");
        }
      } catch (err) {
        console.error("Python Avatar: Fallback clipboard error:", err);
      }
    }
    return false;
  }
}

// Expose functions to global scope for CDP access
window.pythonAvatarControl = {
  move: moveAvatar,
  speak: showSpeech,
  copyToClipboard: (text) => handleClipboard(text, "copy"),
  readFromClipboard: () => handleClipboard("", "read"),
};

console.log("Python Avatar: Content script loaded");
