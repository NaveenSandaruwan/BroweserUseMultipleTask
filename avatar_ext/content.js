// ===== Avatar Creation =====
function createAvatar() {
  if (document.getElementById("python-avatar-container")) {
    console.log("Python Avatar: Avatar already exists");
    return;
  }

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
    transition: left 0.6s ease, top 0.6s ease;
  `;

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

  // Mic button
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
  `;

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

  avatarContainer.appendChild(avatar);
  avatarContainer.appendChild(speechBubble);
  document.body.appendChild(avatarContainer);
  document.body.appendChild(micButton);
  document.body.appendChild(micStatus);

  setupSpeechRecognition(micButton, micStatus);
  console.log("Python Avatar: Ready for structured commands ✅");
  return true;
}

// ===== Helpers =====
function moveAvatar(x, y) {
  const avatarContainer = document.getElementById("python-avatar-container");
  if (avatarContainer && typeof x === "number" && typeof y === "number") {
    avatarContainer.style.left = `${x}px`;
    avatarContainer.style.top = `${y}px`;
    return true;
  }
  return false;
}

function showSpeech(text, duration = 5000) {
  const speechBubble = document.getElementById("python-avatar-speech");
  if (speechBubble) {
    speechBubble.textContent = text;
    speechBubble.style.opacity = 1;
    if (duration > 0) setTimeout(() => (speechBubble.style.opacity = 0), duration);
  }
}

function moveNearElement(id, offsetX = 50, offsetY = -20) {
  const element = document.getElementById(id);
  const avatarContainer = document.getElementById("python-avatar-container");
  if (element && avatarContainer) {
    const rect = element.getBoundingClientRect();
    avatarContainer.style.left = `${rect.left + window.scrollX + offsetX}px`;
    avatarContainer.style.top = `${rect.top + window.scrollY + offsetY}px`;
    return true;
  }
  return false;
}

// ===== Explain Handler =====
function explainElement(command) {
  let moved = false;

  if (command.x != null && command.y != null) {
    moved = moveAvatar(command.x, command.y);
  }

  if (!moved && command.id) {
    moved = moveNearElement(command.id);
  }

  showSpeech(command.text || "Sorry, I don’t have enough information.", 6000);
}

// ===== Command Handler =====
function handleCommand(command) {
  if (!command || !command.action) {
    console.error("Invalid command:", command);
    return;
  }

  switch (command.action) {
    case "move":
      moveAvatar(command.x, command.y);
      showSpeech(command.text || `Moving to (${command.x}, ${command.y})`, 3000);
      break;
    case "explain":
      explainElement(command);
      break;
    default:
      console.error("Unknown command action:", command.action);
  }
}

// ===== Speech Recognition =====
function setupSpeechRecognition(micButton, micStatus) {
  const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognitionAPI) return console.error("Speech recognition not supported");

  const recognition = new SpeechRecognitionAPI();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = "en-US";

  let isListening = false;

  micButton.addEventListener("click", () => {
    if (isListening) recognition.stop();
    else recognition.start();
  });

  recognition.onstart = () => {
    isListening = true;
    micButton.style.background = "#EA4335";
    micStatus.textContent = "Listening...";
    micStatus.style.opacity = 1;
  };

  recognition.onend = () => {
    isListening = false;
    micButton.style.background = "#4285f4";
    micStatus.style.opacity = 0;
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    console.log("Heard:", transcript);
    showSpeech("Processing...", 2000);

    fetch("http://127.0.0.1:8000/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: transcript }),
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("Structured command:", data);
        if (data.command) handleCommand(data.command);
      })
      .catch((err) => {
        console.error("Error talking to agent:", err);
        handleCommand({ action: "explain", text: "Sorry, something went wrong with the agent." });
      });
  };

  recognition.onerror = (event) => {
    console.error("Recognition error:", event.error);
    micStatus.textContent = `Error: ${event.error}`;
    micStatus.style.opacity = 1;
  };
}

// ===== Expose API =====
window.pythonAvatarControl = {
  move: moveAvatar,
  speak: showSpeech,
  explain: explainElement,
  moveNearElement: moveNearElement,
  handleCommand: handleCommand,
};

// ===== Initialize =====
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", createAvatar);
} else {
  createAvatar();
}
