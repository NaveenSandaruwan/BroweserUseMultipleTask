// =========================
// Global Voice State Management
// =========================
// Initialize global voice state (only once)
if (typeof window.isVoiceEnabled === "undefined") {
  window.isVoiceEnabled = true;
  console.log("Initialized global voice state:", window.isVoiceEnabled);
}

// Debug function to test voice disable from console
window.testVoiceDisable = function () {
  console.log("=== Voice Disable Test ===");
  console.log("Current voice status:", window.isVoiceEnabled);
  console.log("Testing speakText with 'test' message...");
  if (typeof window.speakText === "function") {
    window.speakText("test");
  } else {
    console.log("speakText function not available");
  }
};

// =========================
// Lip Sync Management
// =========================
class LipSyncManager {
  constructor() {
    this.audioContext = null;
    this.analyser = null;
    this.audioSource = null;
    this.animationFrame = null;
    this.isAnalyzing = false;
    this.dataArray = null;
    this.bufferLength = 0;

    // Mouth animation parameters
    this.minMouthValue = 52; // Closed mouth Y position
    this.maxMouthValue = 65; // Open mouth Y position
    this.smoothingFactor = 0.7; // For smooth animation
    this.currentMouthValue = this.minMouthValue;

    console.log("LipSyncManager initialized");
  }

  // Initialize Web Audio API
  async initAudioContext() {
    try {
      this.audioContext = new (window.AudioContext ||
        window.webkitAudioContext)();
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 256;
      this.bufferLength = this.analyser.frequencyBinCount;
      this.dataArray = new Uint8Array(this.bufferLength);

      console.log("Audio context initialized for lip sync");
      return true;
    } catch (error) {
      console.error("Failed to initialize audio context:", error);
      return false;
    }
  }

  // Connect audio element to analyzer
  connectAudio(audioElement) {
    if (!this.audioContext || !this.analyser) {
      console.error("Audio context not initialized");
      return false;
    }

    try {
      // Disconnect previous source if exists
      if (this.audioSource) {
        this.audioSource.disconnect();
      }

      // Create new audio source and connect to analyser
      this.audioSource =
        this.audioContext.createMediaElementSource(audioElement);
      this.audioSource.connect(this.analyser);
      this.analyser.connect(this.audioContext.destination);

      console.log("Audio connected to lip sync analyzer");
      return true;
    } catch (error) {
      console.error("Failed to connect audio:", error);
      return false;
    }
  }

  // Start lip sync animation
  startLipSync() {
    if (!this.analyser || this.isAnalyzing) {
      return;
    }

    this.isAnalyzing = true;
    console.log("Starting lip sync animation");
    this.animateMouth();
  }

  // Stop lip sync animation
  stopLipSync() {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
      this.animationFrame = null;
    }
    this.isAnalyzing = false;

    // Return mouth to neutral position
    this.updateMouthShape(this.minMouthValue);
    console.log("Stopped lip sync animation");
  }

  // Main animation loop
  animateMouth() {
    if (!this.isAnalyzing) return;

    // Get audio frequency data
    this.analyser.getByteFrequencyData(this.dataArray);

    // Calculate audio energy (focus on speech frequencies 85Hz-255Hz)
    let sum = 0;
    const startFreq = Math.floor(
      (85 / (this.audioContext.sampleRate / 2)) * this.bufferLength
    );
    const endFreq = Math.floor(
      (255 / (this.audioContext.sampleRate / 2)) * this.bufferLength
    );

    for (let i = startFreq; i < endFreq && i < this.bufferLength; i++) {
      sum += this.dataArray[i];
    }

    const avgEnergy = sum / (endFreq - startFreq);

    // Normalize energy value (0-1)
    const normalizedEnergy = Math.min(avgEnergy / 128, 1);

    // Calculate target mouth opening
    const targetMouthValue =
      this.minMouthValue +
      normalizedEnergy * (this.maxMouthValue - this.minMouthValue);

    // Apply smoothing
    this.currentMouthValue =
      this.currentMouthValue * this.smoothingFactor +
      targetMouthValue * (1 - this.smoothingFactor);

    // Update mouth shape
    this.updateMouthShape(this.currentMouthValue);

    // Continue animation
    this.animationFrame = requestAnimationFrame(() => this.animateMouth());
  }

  // Update avatar mouth shape based on energy value (bigger emoji-style)
  updateMouthShape(openingAmount) {
    const avatarSvg = document.querySelector("#python-avatar svg");
    if (!avatarSvg) return;

    const upperMouth = avatarSvg.querySelector("#upper-mouth");
    const lowerMouth = avatarSvg.querySelector("#lower-mouth");

    if (!upperMouth || !lowerMouth) return;

    // Calculate opening based on energy (0 = closed, 1 = fully open)
    const normalizedOpening =
      (openingAmount - this.minMouthValue) /
      (this.maxMouthValue - this.minMouthValue);
    const clampedOpening = Math.max(0, Math.min(1, normalizedOpening));

    // Shift by 0.8 and re-normalize to focus on top 20% of values
    const shiftedValue = Math.max(0, clampedOpening - 0.8);
    const reNormalizedOpening = shiftedValue / 0.2; // Re-normalize from 0-0.2 range to 0-1 range

    // Apply quartic relation (y = x⁴) to create extreme sensitivity differences between quiet and loud sounds
    const quarticOpening =
      reNormalizedOpening *
      reNormalizedOpening *
      reNormalizedOpening *
      reNormalizedOpening;

    // Fixed corner positions (narrower mouth)
    const leftCornerX = 25;
    const rightCornerX = 55;
    const leftCornerY = 51;
    const rightCornerY = 51;

    // Middle points move up and down based on speech energy
    // Using quartic opening for extreme sensitivity - Upper lip moves less, lower lip moves 2x more for better visibility
    const upperMovement = quarticOpening * 10; // Increased range with quartic function
    const lowerMovement = quarticOpening * 20; // Lower curve moves 2x more

    const upperMiddleY = 51 - upperMovement; // Upper curve goes up
    const lowerMiddleY = 51 + lowerMovement; // Lower curve goes down more

    // Console log the lip change values for debugging
    // console.log(`Lip Sync Values:`, {
    //   openingAmount: openingAmount.toFixed(3),
    //   normalizedOpening: normalizedOpening.toFixed(3),
    //   clampedOpening: clampedOpening.toFixed(3),
    //   shiftedValue: shiftedValue.toFixed(3),
    //   reNormalizedOpening: reNormalizedOpening.toFixed(3),
    //   quarticOpening: quarticOpening.toFixed(5),
    //   upperMovement: upperMovement.toFixed(2),
    //   lowerMovement: lowerMovement.toFixed(2),
    //   upperMiddleY: upperMiddleY.toFixed(2),
    //   lowerMiddleY: lowerMiddleY.toFixed(2),
    // });

    // Update white background shape between lips
    const mouthBackground = avatarSvg.querySelector("#mouth-background");
    if (mouthBackground) {
      // Create a white area between upper and lower lips
      const backgroundPath = `M${leftCornerX} ${leftCornerY} Q40 ${upperMiddleY} ${rightCornerX} ${rightCornerY} Q40 ${lowerMiddleY} ${leftCornerX} ${leftCornerY}`;
      mouthBackground.setAttribute("d", backgroundPath);
    }

    // Update upper mouth curve - wider corners, middle moves up
    upperMouth.setAttribute(
      "d",
      `M${leftCornerX} ${leftCornerY} Q40 ${upperMiddleY} ${rightCornerX} ${rightCornerY}`
    );

    // Update lower mouth curve - wider corners, middle moves down 2x more
    lowerMouth.setAttribute(
      "d",
      `M${leftCornerX} ${leftCornerY} Q40 ${lowerMiddleY} ${rightCornerX} ${rightCornerY}`
    );
  }

  // Reset mouth to neutral position
  resetMouth() {
    this.updateMouthShape(this.minMouthValue);
  }
}

// Global lip sync manager instance
window.lipSyncManager = new LipSyncManager();

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
  console.log("createAvatarUI called");

  // Check if UI already exists
  if (document.getElementById("avatar-extension-container")) {
    console.log("UI already exists, returning existing elements");
    return getUIElements();
  }

  // --- Main Container (Position: Top Right, Draggable) ---
  const container = document.createElement("div");
  container.id = "avatar-extension-container";
  container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        width: 120px;
        height: 120px;
        cursor: move;
    `;

  // --- Avatar Graphic Element (Center of the circular menu) ---
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
            
            <!-- Emoji-style mouth with white background and black curves -->
            <g id="mouth-group">
                <!-- White background between lips -->
                <path id="mouth-background" d="M25 51 Q40 54 55 51 Q40 56 25 51" fill="white" stroke="none" />
                
                <!-- Upper mouth curve (narrower width, more downward curve) -->
                <path id="upper-mouth" d="M25 51 Q40 54 55 51" stroke="#000" stroke-width="2" fill="none" stroke-linecap="round" />
                
                <!-- Lower mouth curve (narrower width, deeper downward curve) -->
                <path id="lower-mouth" d="M25 51 Q40 56 55 51" stroke="#000" stroke-width="2" fill="none" stroke-linecap="round" />
            </g>
        </svg>
    `;
  avatar.style.cssText = `
        position: absolute;
        top: 20px;
        left: 20px;
        width: 80px;
        height: 80px;
        border-radius: 50%;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        cursor: grab;
        transition: transform 0.3s ease;
    `;

  // --- Circular Button Menu (Hidden by default, shows on hover) ---
  const buttonMenu = document.createElement("div");
  buttonMenu.id = "avatar-button-menu";
  buttonMenu.style.cssText = `
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 120px;
        height: 120px;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.3s ease;
    `;

  // --- Speech Bubble (Scrollable and fixed height/width) ---
  const speechBubble = document.createElement("div");
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
        right: 130px;
        font-size: 14px;
        line-height: 1.4;
        cursor: default;
    `;

  // Function to create a circular menu button
  function createMenuButton(id, emoji, title, background, angle) {
    const btn = document.createElement("button");
    btn.id = id;
    btn.innerHTML = emoji;
    btn.title = title;

    // Calculate position on circle (60px radius from center)
    const radius = 60;
    const radian = (angle * Math.PI) / 180;
    const x = radius * Math.cos(radian);
    const y = radius * Math.sin(radian);

    btn.style.cssText = `
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(calc(-50% + ${x}px), calc(-50% + ${y}px));
        width: 35px;
        height: 35px;
        border-radius: 50%;
        background: ${background};
        color: white;
        font-size: 16px;
        border: none;
        cursor: pointer;
        box-shadow: 0 3px 10px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
        pointer-events: auto;
        z-index: 1;
    `;

    // Hover effects
    btn.addEventListener("mouseenter", () => {
      btn.style.transform = `translate(calc(-50% + ${x}px), calc(-50% + ${y}px)) scale(1.2)`;
      btn.style.boxShadow = "0 5px 15px rgba(0,0,0,0.4)";
    });

    btn.addEventListener("mouseleave", () => {
      btn.style.transform = `translate(calc(-50% + ${x}px), calc(-50% + ${y}px)) scale(1)`;
      btn.style.boxShadow = "0 3px 10px rgba(0,0,0,0.3)";
    });

    return btn;
  }

  // Create circular menu buttons
  const micBtn = createMenuButton("mic", "🎤", "Voice input", "#4285f4", 0); // Right
  const ttsBtn = createMenuButton(
    "tts-test",
    "🔊",
    "Test text-to-speech",
    "#34A853",
    45
  ); // Top-right
  const elevenLabsBtn = createMenuButton(
    "elevenlabs-config",
    "🎵",
    "Configure ElevenLabs TTS",
    "#FF6B35",
    90
  ); // Top
  const emotionBtn = createMenuButton(
    "emotion-test",
    "🎭",
    "Test avatar emotions",
    "#FBBC05",
    135
  ); // Top-left
  const disableVoiceBtn = createMenuButton(
    "disable-voice",
    "🔇",
    "Disable/Enable voice",
    "#EA4335",
    180
  ); // Left
  const helpBtn = createMenuButton(
    "help-guide",
    "❓",
    "Help & Guide",
    "#9C27B0",
    225
  ); // Bottom-left
  const savePositionBtn = createMenuButton(
    "save-position",
    "📌",
    "Save current position",
    "#607D8B",
    270
  ); // Bottom
  const lipSyncBtn = createMenuButton(
    "lipsync-test",
    "👄",
    "Test lip sync animation",
    "#E91E63",
    315
  ); // Bottom-right

  // Add buttons to menu
  buttonMenu.appendChild(micBtn);
  buttonMenu.appendChild(ttsBtn);
  buttonMenu.appendChild(elevenLabsBtn);
  buttonMenu.appendChild(emotionBtn);
  buttonMenu.appendChild(disableVoiceBtn);
  buttonMenu.appendChild(helpBtn);
  buttonMenu.appendChild(savePositionBtn);
  buttonMenu.appendChild(lipSyncBtn);

  // --- Status element ---
  const statusEl = document.createElement("div");
  statusEl.id = "status";
  statusEl.style.cssText = `
        position: absolute;
        bottom: -30px;
        left: 50%;
        transform: translateX(-50%);
        font-family: Arial, sans-serif;
        font-size: 12px;
        color: #333;
        background: rgba(255,255,255,0.9);
        padding: 4px 8px;
        border-radius: 12px;
        white-space: nowrap;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        opacity: 0;
        transition: opacity 0.3s ease;
    `;

  // Append elements to container
  container.appendChild(avatar);
  container.appendChild(buttonMenu);
  container.appendChild(speechBubble);
  container.appendChild(statusEl);

  // Add hover effects for the entire container
  container.addEventListener("mouseenter", () => {
    buttonMenu.style.opacity = "1";
    buttonMenu.style.pointerEvents = "auto";
    avatar.style.transform = "scale(1.1)";
  });

  container.addEventListener("mouseleave", () => {
    buttonMenu.style.opacity = "0";
    buttonMenu.style.pointerEvents = "none";
    avatar.style.transform = "scale(1)";
  });

  console.log("Appending avatar container to document body");
  document.body.appendChild(container);
  console.log("Avatar UI created successfully");

  // Add event listener for TTS test button
  ttsBtn.addEventListener("click", () => {
    statusEl.textContent = "Testing TTS...";
    speakText("test");
  });

  // Add event listener for ElevenLabs config button
  elevenLabsBtn.addEventListener("click", () => {
    createElevenLabsConfigModal();
  });

  // Add event listener for Emotion test button
  emotionBtn.addEventListener("click", async () => {
    try {
      statusEl.textContent = "Testing emotion detection...";

      // Ensure WebSocket is connected
      if (!isSocketConnected) {
        console.log("WebSocket not connected, attempting to reconnect...");
        connectWebSocket();

        // Wait a bit for connection to establish
        await new Promise((resolve) => setTimeout(resolve, 1000));

        // If still not connected, use a fallback
        if (!isSocketConnected) {
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
      socket.send(
        JSON.stringify({
          type: "emotion",
          message: randomMessage,
        })
      );

      // Show what message was used
      showSpeech(`Testing emotion detection with: "${randomMessage}"`);
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
      updateAvatarEmotion(randomEmotion);

      setTimeout(() => {
        statusEl.textContent = "Fallback: " + randomEmotion;
      }, 2000);
    }
  });

  // Add event listener for save position button
  savePositionBtn.addEventListener("click", () => {
    saveAvatarPosition(true); // Show notification when button is clicked
  });

  // Add event listener for lip sync test button
  lipSyncBtn.addEventListener("click", async () => {
    statusEl.textContent = "Testing lip sync...";
    statusEl.style.opacity = "1";

    try {
      // Initialize lip sync manager
      if (!window.lipSyncManager.audioContext) {
        await window.lipSyncManager.initAudioContext();
      }

      // Test lip sync with sample text
      speakText(
        "This is a test of the lip sync animation. The avatar mouth should move with the speech patterns."
      );

      statusEl.textContent = "Lip sync test started";
      setTimeout(() => {
        statusEl.style.opacity = "0";
      }, 2000);
    } catch (error) {
      console.error("Lip sync test failed:", error);
      statusEl.textContent = "Lip sync test failed";
      setTimeout(() => {
        statusEl.style.opacity = "0";
      }, 2000);
    }
  });

  // Add event listener for disable voice button
  disableVoiceBtn.addEventListener("click", () => {
    window.isVoiceEnabled = !window.isVoiceEnabled; // Toggle global state directly

    console.log(
      "Voice disable button clicked - New status:",
      window.isVoiceEnabled
    );

    if (window.isVoiceEnabled) {
      disableVoiceBtn.innerHTML = "🔊";
      disableVoiceBtn.title = "Disable voice";
      statusEl.textContent = "Voice enabled";
      statusEl.style.opacity = "1";
    } else {
      disableVoiceBtn.innerHTML = "🔇";
      disableVoiceBtn.title = "Enable voice";
      statusEl.textContent = "Voice disabled";
      statusEl.style.opacity = "1";
      // Stop any current speech
      if (window.elevenLabsTTS && window.elevenLabsTTS.stopSpeaking) {
        window.elevenLabsTTS.stopSpeaking();
      }
    }
    setTimeout(() => {
      statusEl.style.opacity = "0";
    }, 2000);
  });

  // Initialize button state based on current voice status
  if (window.isVoiceEnabled) {
    disableVoiceBtn.innerHTML = "🔊";
    disableVoiceBtn.title = "Disable voice";
  } else {
    disableVoiceBtn.innerHTML = "🔇";
    disableVoiceBtn.title = "Enable voice";
  }

  // Add event listener for help button
  helpBtn.addEventListener("click", () => {
    showHelpGuide();
  });

  return {
    micBtn,
    statusEl,
    ttsBtn,
    emotionBtn,
    elevenLabsBtn,
    disableVoiceBtn,
    helpBtn,
    savePositionBtn,
  };
}

// Helper function to get UI elements
function getUIElements() {
  return {
    micBtn: document.getElementById("mic"),
    statusEl: document.getElementById("status"),
    ttsBtn: document.getElementById("tts-test"),
    emotionBtn: document.getElementById("emotion-test"),
    elevenLabsBtn: document.getElementById("elevenlabs-config"),
    disableVoiceBtn: document.getElementById("disable-voice"),
    helpBtn: document.getElementById("help-guide"),
    savePositionBtn: document.getElementById("save-position"),
    lipSyncBtn: document.getElementById("lipsync-test"),
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

// Show comprehensive help guide
function showHelpGuide() {
  // Remove existing help modal if present
  const existingModal = document.getElementById("avatar-help-modal");
  if (existingModal) {
    existingModal.remove();
  }

  const modal = document.createElement("div");
  modal.id = "avatar-help-modal";
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    z-index: 25000;
    display: flex;
    justify-content: center;
    align-items: center;
    font-family: Arial, sans-serif;
  `;

  const helpContent = document.createElement("div");
  helpContent.style.cssText = `
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 30px;
    border-radius: 15px;
    max-width: 600px;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    position: relative;
  `;

  helpContent.innerHTML = `
    <div style="text-align: center; margin-bottom: 25px;">
      <h2 style="margin: 0; font-size: 28px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">🤖 Avatar Assistant Guide</h2>
      <p style="margin: 10px 0 0 0; opacity: 0.9;">Your AI companion with voice interaction</p>
    </div>

    <div style="margin-bottom: 25px;">
      <h3 style="color: #FFD700; margin-bottom: 15px;">✨ How to Use</h3>
      <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
        <p><strong>🎯 Hover over the avatar</strong> to reveal the circular button menu</p>
        <p><strong>🎤 Click the microphone</strong> to start voice input</p>
        <p><strong>💬 Speak naturally</strong> - the AI will respond with both text and voice</p>
        <p><strong>🖱️ Drag the avatar</strong> to move it around your screen</p>
      </div>
    </div>

    <div style="margin-bottom: 25px;">
      <h3 style="color: #FFD700; margin-bottom: 15px;">🔘 Button Functions</h3>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 14px;">
        <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px;">
          <strong>🎤 Microphone</strong><br>Start/stop voice input
        </div>
        <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px;">
          <strong>🔊 Test TTS</strong><br>Test text-to-speech
        </div>
        <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px;">
          <strong>🎵 ElevenLabs</strong><br>Configure AI voice
        </div>
        <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px;">
          <strong>🎭 Emotions</strong><br>Test avatar emotions
        </div>
        <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px;">
          <strong>🔊 Disable Voice</strong><br>Mute/unmute speech
        </div>
        <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px;">
          <strong>📌 Save Position</strong><br>Remember location
        </div>
        <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px;">
          <strong>👄 Lip Sync</strong><br>Test mouth animation
        </div>
      </div>
    </div>

    <div style="margin-bottom: 25px;">
      <h3 style="color: #FFD700; margin-bottom: 15px;">🎵 ElevenLabs Setup</h3>
      <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;">
        <p><strong>1.</strong> Click the 🎵 button to open ElevenLabs configuration</p>
        <p><strong>2.</strong> Your API key is already configured in the code</p>
        <p><strong>3.</strong> Select your preferred voice from the dropdown</p>
        <p><strong>4.</strong> Click "Test TTS" to verify it works</p>
        <p><strong>5.</strong> Save configuration to enable high-quality AI voice</p>
      </div>
    </div>

    <div style="margin-bottom: 25px;">
      <h3 style="color: #FFD700; margin-bottom: 15px;">🎯 Features</h3>
      <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;">
        <p>✅ <strong>Voice Recognition:</strong> Speak naturally to interact</p>
        <p>✅ <strong>AI Responses:</strong> Get intelligent replies to your questions</p>
        <p>✅ <strong>Emotion Detection:</strong> Avatar shows emotions based on conversation</p>
        <p>✅ <strong>High-Quality TTS:</strong> ElevenLabs integration for natural speech</p>
        <p>✅ <strong>Text Display:</strong> See responses in the speech bubble</p>
        <p>✅ <strong>Draggable Interface:</strong> Move avatar anywhere on screen</p>
      </div>
    </div>

    <div style="margin-bottom: 25px;">
      <h3 style="color: #FFD700; margin-bottom: 15px;">🔧 Troubleshooting</h3>
      <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; font-size: 14px;">
        <p><strong>🔴 No voice input:</strong> Check microphone permissions</p>
        <p><strong>🔴 No speech output:</strong> Check audio permissions and volume</p>
        <p><strong>🔴 ElevenLabs not working:</strong> Verify API key is set correctly</p>
        <p><strong>🔴 Avatar not responding:</strong> Check WebSocket connection (see console)</p>
        <p><strong>💡 Tip:</strong> Press F12 and check Console tab for error messages</p>
      </div>
    </div>

    <div style="text-align: center; margin-top: 30px;">
      <button id="close-help-btn" style="
        background: linear-gradient(45deg, #FF6B6B, #FF8E53);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 25px;
        font-size: 16px;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: transform 0.2s ease;
      " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
        Got it! ✨
      </button>
    </div>
  `;

  modal.appendChild(helpContent);
  document.body.appendChild(modal);

  // Close button event
  document.getElementById("close-help-btn").addEventListener("click", () => {
    modal.remove();
  });

  // Close when clicking outside
  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.remove();
    }
  });
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

      // Check if there's an error
      if (data.error) {
        console.error("Server error:", data.error);
        const statusEl = document.getElementById("status");
        if (statusEl) statusEl.textContent = `Error: ${data.error}`;
        return;
      }

      // Handle different response types
      const responseType = data.type || "chat"; // Default to chat for backward compatibility

      if (responseType === "chat") {
        // Stop thinking animation when we get the response
        stopThinkingAnimation();

        // Chat response already has emotion processed earlier
        // Just display the reply and speak it

        // If emotion is provided again, update it (but it should already be updated)
        if (data.emotion) {
          console.log("Chat response includes emotion:", data.emotion);
          // No need to call updateAvatarEmotion again as we've already done it
          // in the separate emotion request, but do it as a fallback
          updateAvatarEmotion(data.emotion);
        }

        // Display and speak the reply
        if (data.reply) {
          // Display the reply with markdown rendering
          showSpeech(data.reply);

          // Speak the reply
          speakText(data.reply);

          const statusEl = document.getElementById("status");
          if (statusEl) statusEl.textContent = "Reply received";
        }
      } else if (responseType === "emotion") {
        // Handle emotion-only response - this comes first in our new flow
        if (data.emotion) {
          console.log("Got emotion response first:", data.emotion);
          // Update avatar based on received emotion immediately
          updateAvatarEmotion(data.emotion);

          const statusEl = document.getElementById("status");
          if (statusEl)
            statusEl.textContent = `Processing with emotion: ${data.emotion}`;

          // Start thinking animation instead of showing text
          startThinkingAnimation();
        }
      } else if (responseType === "error") {
        // Stop thinking animation on error
        stopThinkingAnimation();

        console.error("Server returned error:", data.error);
        const statusEl = document.getElementById("status");
        if (statusEl) statusEl.textContent = `Error: ${data.error}`;

        // Show the error in speech bubble
        showSpeech(`Error: ${data.error}`);
      }

      // Dispatch a custom event that other handlers can listen for
      // This is useful for promises waiting for specific responses
      const customEvent = new CustomEvent("websocketMessage", {
        detail: data,
      });
      document.dispatchEvent(customEvent);
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
    statusEl.textContent = "Processing...";

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

      // First, we detect emotion (which is faster)
      statusEl.textContent = "Detecting emotion...";

      // Send the message over WebSocket with type 'emotion'
      socket.send(
        JSON.stringify({
          type: "emotion",
          message: transcript,
        })
      );

      // Wait a short time for the emotion to be processed
      await new Promise((resolve) => setTimeout(resolve, 200));

      // Start thinking animation and send for full chat processing
      statusEl.textContent = "Getting AI response...";
      startThinkingAnimation();

      socket.send(
        JSON.stringify({
          type: "chat",
          message: transcript,
        })
      );

      // Note: We no longer need to handle the response here
      // The WebSocket onmessage handler will take care of it
    } catch (err) {
      console.error("Error:", err);

      // Stop thinking animation on error
      stopThinkingAnimation();

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

// Function to detect emotion for text via WebSocket
async function detectEmotion(text) {
  return new Promise((resolve, reject) => {
    try {
      // Ensure WebSocket is connected
      if (!isSocketConnected) {
        console.log("WebSocket not connected for emotion detection");
        resolve("neutral"); // Default fallback
        return;
      }

      // Create a one-time message handler for this specific request
      const messageHandler = (event) => {
        try {
          const data = JSON.parse(event.data);

          // Check if this is an emotion response
          if (data.type === "emotion" && data.emotion) {
            // Remove this one-time handler
            socket.removeEventListener("message", messageHandler);
            resolve(data.emotion);
          }
        } catch (e) {
          console.error("Error in emotion detection handler:", e);
        }
      };

      // Add the one-time message handler
      socket.addEventListener("message", messageHandler);

      // Send the emotion request
      socket.send(
        JSON.stringify({
          type: "emotion",
          message: text,
        })
      );

      // Set a timeout to prevent hanging if no response
      setTimeout(() => {
        socket.removeEventListener("message", messageHandler);
        console.log("Emotion detection timed out");
        resolve("neutral"); // Default fallback
      }, 3000);
    } catch (error) {
      console.error("Error detecting emotion:", error);
      resolve("neutral"); // Default fallback
    }
  });
}

// Function to update avatar face based on emotion
function updateAvatarEmotion(emotion) {
  const avatar = document.getElementById("python-avatar");
  if (!avatar) return;

  // Get the SVG elements
  const svgDoc = avatar.querySelector("svg");
  const upperMouth = svgDoc.getElementById("upper-mouth");
  const lowerMouth = svgDoc.getElementById("lower-mouth");
  const leftEyebrow = svgDoc.getElementById("left-eyebrow");
  const rightEyebrow = svgDoc.getElementById("right-eyebrow");
  const leftPupil = svgDoc.getElementById("left-pupil");
  const rightPupil = svgDoc.getElementById("right-pupil");

  if (!upperMouth || !lowerMouth) return;

  // Remove emoji indicator if it exists
  const existingIndicator = document.getElementById("emotion-indicator");
  if (existingIndicator) {
    existingIndicator.remove();
  }

  // Update SVG facial expressions based on emotion (bigger emoji-style)
  switch (emotion) {
    case "happy":
      // Happy smile - narrower corners, upper curve goes up, lower goes down more
      upperMouth.setAttribute("d", "M25 51 Q40 47 55 51");
      lowerMouth.setAttribute("d", "M25 51 Q40 59 55 51");
      leftEyebrow.setAttribute("d", "M20 22 Q30 18 35 22");
      rightEyebrow.setAttribute("d", "M45 22 Q50 18 60 22");
      leftPupil.setAttribute("cy", "29");
      rightPupil.setAttribute("cy", "29");
      break;

    case "sad":
      // Sad frown - both curves go down from corners, lower more pronounced
      upperMouth.setAttribute("d", "M25 51 Q40 54 55 51");
      lowerMouth.setAttribute("d", "M25 51 Q40 60 55 51");
      leftEyebrow.setAttribute("d", "M20 25 Q30 28 35 25");
      rightEyebrow.setAttribute("d", "M45 25 Q50 28 60 25");
      leftPupil.setAttribute("cy", "32");
      rightPupil.setAttribute("cy", "32");
      break;

    case "angry":
      // Angry - downward curves, narrower and more pronounced
      upperMouth.setAttribute("d", "M25 51 Q40 52 55 51");
      lowerMouth.setAttribute("d", "M25 51 Q40 57 55 51");
      leftEyebrow.setAttribute("d", "M20 20 Q30 15 35 25");
      rightEyebrow.setAttribute("d", "M45 25 Q50 15 60 20");
      leftPupil.setAttribute("cy", "30");
      rightPupil.setAttribute("cy", "30");
      break;

    case "surprised":
      // Surprised - narrower oval open mouth
      upperMouth.setAttribute("d", "M25 51 Q40 48 55 51");
      lowerMouth.setAttribute("d", "M25 51 Q40 60 55 51");
      leftEyebrow.setAttribute("d", "M20 18 Q30 13 35 18");
      rightEyebrow.setAttribute("d", "M45 18 Q50 13 60 18");
      leftPupil.setAttribute("cy", "28");
      rightPupil.setAttribute("cy", "28");
      break;

    case "fearful":
      // Fearful - narrower worried mouth
      upperMouth.setAttribute("d", "M25 51 Q40 50 55 51");
      lowerMouth.setAttribute("d", "M25 51 Q40 56 55 51");
      leftEyebrow.setAttribute("d", "M20 20 Q30 15 35 20");
      rightEyebrow.setAttribute("d", "M45 20 Q50 15 60 20");
      leftPupil.setAttribute("cy", "28");
      rightPupil.setAttribute("cy", "28");
      break;

    case "disgusted":
      // Disgusted - narrower asymmetric mouth, one side raised
      upperMouth.setAttribute("d", "M25 51 Q35 49 55 52");
      lowerMouth.setAttribute("d", "M25 51 Q35 58 55 52");
      leftEyebrow.setAttribute("d", "M20 20 Q30 18 35 25");
      rightEyebrow.setAttribute("d", "M45 25 Q50 15 60 20");
      leftPupil.setAttribute("cy", "31");
      rightPupil.setAttribute("cy", "29");
      break;

    case "neutral":
    default:
      // Neutral - narrower mouth with more downward curvature
      upperMouth.setAttribute("d", "M25 51 Q40 54 55 51");
      lowerMouth.setAttribute("d", "M25 51 Q40 56 55 51");
      leftEyebrow.setAttribute("d", "M20 22 Q30 20 35 22");
      rightEyebrow.setAttribute("d", "M45 22 Q50 20 60 22");
      leftPupil.setAttribute("cy", "30");
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
// Enhanced Text-to-Speech with ElevenLabs Integration
// =========================
async function speakText(text) {
  if (!text || text.trim() === "") {
    console.log("Empty text provided to speakText, ignoring");
    return;
  }

  // Check if voice is disabled
  console.log("speakText called - Voice status:", window.isVoiceEnabled);
  if (window.isVoiceEnabled === false) {
    console.log("Voice is disabled, skipping speech");
    return;
  }

  const statusEl = document.getElementById("status");
  if (statusEl) {
    statusEl.textContent = "Speaking...";
    statusEl.style.opacity = "1";
  }

  try {
    // Check if ElevenLabs is enabled and configured
    if (isElevenLabsEnabled() && window.elevenLabsTTS) {
      console.log("Using ElevenLabs TTS");

      // Use ElevenLabs TTS with progress tracking
      await window.elevenLabsTTS.speakText(text, (progress) => {
        if (statusEl) {
          switch (progress.status) {
            case "generating":
              statusEl.textContent = `Generating audio ${progress.current}/${progress.total}...`;
              break;
            case "playing":
              statusEl.textContent = `Speaking ${progress.current}/${progress.total}...`;
              break;
            case "completed":
              statusEl.textContent = "Speech completed";
              setTimeout(() => {
                statusEl.style.opacity = "0";
                setTimeout(() => {
                  statusEl.textContent = "";
                }, 300);
              }, 2000);
              break;
            case "error":
              statusEl.textContent = `TTS Error: ${progress.error}`;
              setTimeout(() => {
                statusEl.style.opacity = "0";
                setTimeout(() => {
                  statusEl.textContent = "";
                }, 300);
              }, 3000);
              break;
          }
        }
      });
    } else {
      // Fallback to browser TTS
      console.log("Using browser TTS (fallback)");

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
    }
  } catch (error) {
    console.error("Error in speakText:", error);

    // Fallback to browser TTS if ElevenLabs fails
    if (isElevenLabsEnabled()) {
      console.log("ElevenLabs failed, falling back to browser TTS");
      if (statusEl) {
        statusEl.textContent = "Switching to browser TTS...";
      }

      try {
        chrome.runtime.sendMessage(
          {
            action: "speak",
            text: text,
          },
          (response) => {
            if (statusEl) {
              if (response && response.success) {
                setTimeout(() => {
                  statusEl.textContent = "";
                }, 2000);
              } else {
                statusEl.textContent = "Speech error";
                setTimeout(() => {
                  statusEl.textContent = "";
                }, 3000);
              }
            }
          }
        );
      } catch (fallbackError) {
        console.error("Fallback TTS also failed:", fallbackError);
      }
    }
  }
}

// =========================
// Initialization
// =========================
// Add Avatar and Menu Styles
const avatarStyles = document.createElement("style");
avatarStyles.textContent = `
  /* Avatar animations */
  #left-eyebrow, #right-eyebrow, #left-pupil, #right-pupil {
    transition: all 0.5s ease-in-out;
  }
  
  /* Emoji-style mouth animation optimized for lip sync */
  #upper-mouth, #lower-mouth {
    transition: d 0.08s ease-out;
  }
  
  #mouth-group {
    transition: all 0.08s ease-out;
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

  /* Avatar container hover effects */
  #avatar-extension-container {
    transition: all 0.3s ease;
  }

  #avatar-extension-container:hover {
    filter: drop-shadow(0 0 20px rgba(55, 118, 171, 0.3));
  }

  /* Circular menu animations */
  #avatar-button-menu button {
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  }

  /* Status element improvements */
  #status {
    transition: all 0.3s ease;
  }

  /* Help modal scrollbar */
  #avatar-help-modal div::-webkit-scrollbar {
    width: 8px;
  }
  
  #avatar-help-modal div::-webkit-scrollbar-track {
    background: rgba(255,255,255,0.1);
    border-radius: 4px;
  }
  
  #avatar-help-modal div::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.3);
    border-radius: 4px;
  }
  
  #avatar-help-modal div::-webkit-scrollbar-thumb:hover {
    background: rgba(255,255,255,0.5);
  }
  
  /* Thinking animation styles */
  .thinking-dots {
    position: absolute;
    top: -10px;
    right: -10px;
    display: flex;
    gap: 3px;
  }
  
  .thinking-dot {
    width: 6px;
    height: 6px;
    background: #3776AB;
    border-radius: 50%;
    animation: thinkingPulse 1.4s ease-in-out infinite both;
  }
  
  .thinking-dot:nth-child(1) { animation-delay: -0.32s; }
  .thinking-dot:nth-child(2) { animation-delay: -0.16s; }
  .thinking-dot:nth-child(3) { animation-delay: 0; }
  
  @keyframes thinkingPulse {
    0%, 80%, 100% {
      transform: scale(0.8);
      opacity: 0.5;
    }
    40% {
      transform: scale(1.2);
      opacity: 1;
    }
  }
  
  /* Avatar thinking glow effect */
  .avatar-thinking {
    box-shadow: 0 0 20px rgba(55, 118, 171, 0.6) !important;
    animation: thinkingGlow 2s ease-in-out infinite alternate !important;
  }
  
  @keyframes thinkingGlow {
    from {
      box-shadow: 0 0 15px rgba(55, 118, 171, 0.4);
    }
    to {
      box-shadow: 0 0 25px rgba(55, 118, 171, 0.8);
    }
  }
`;
document.head.appendChild(avatarStyles);

// =========================
// Thinking Animation Functions
// =========================
function startThinkingAnimation() {
  const avatar = document.getElementById("python-avatar");
  const speechBubble = document.getElementById("python-avatar-speech");

  if (!avatar) return;

  // Hide speech bubble during thinking
  if (speechBubble) {
    speechBubble.style.opacity = 0;
  }

  // Add thinking class to avatar for glow effect
  avatar.classList.add("avatar-thinking");

  // Create thinking dots if they don't exist
  let thinkingDots = document.getElementById("thinking-dots");
  if (!thinkingDots) {
    thinkingDots = document.createElement("div");
    thinkingDots.id = "thinking-dots";
    thinkingDots.className = "thinking-dots";

    // Create three dots
    for (let i = 0; i < 3; i++) {
      const dot = document.createElement("div");
      dot.className = "thinking-dot";
      thinkingDots.appendChild(dot);
    }

    // Add to avatar container
    avatar.appendChild(thinkingDots);
  }

  // Make dots visible
  thinkingDots.style.display = "flex";
}

function stopThinkingAnimation() {
  const avatar = document.getElementById("python-avatar");
  const thinkingDots = document.getElementById("thinking-dots");

  if (avatar) {
    // Remove thinking class from avatar
    avatar.classList.remove("avatar-thinking");
  }

  if (thinkingDots) {
    // Hide thinking dots
    thinkingDots.style.display = "none";
  }
}

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

// Main initialization function
function initializeAvatarExtension() {
  console.log("Initializing Avatar Extension...");

  try {
    // Create the UI
    const avatarUI = createAvatarUI();
    console.log("Avatar UI created successfully");

    // Make the avatar container draggable
    const container = document.getElementById("avatar-extension-container");
    if (container) {
      makeDraggable(container);
      // Restore saved position if available
      restoreAvatarPosition();
      console.log("Avatar made draggable and position restored");
    }

    // Initialize ElevenLabs TTS if configured
    setTimeout(async () => {
      try {
        await initializeElevenLabsIfConfigured();
        console.log("ElevenLabs initialization completed");
      } catch (error) {
        console.error("ElevenLabs initialization failed:", error);
      }
    }, 1000);

    console.log("Avatar Extension initialization completed successfully");
  } catch (error) {
    console.error("Avatar Extension initialization failed:", error);
  }
}

// Multiple initialization strategies to ensure the extension loads
function safeInitialize() {
  if (document.readyState === "loading") {
    // DOM is still loading
    document.addEventListener("DOMContentLoaded", initializeAvatarExtension);
  } else {
    // DOM is already loaded
    initializeAvatarExtension();
  }

  // Backup initialization after a delay
  setTimeout(initializeAvatarExtension, 2000);
}

// Start initialization
console.log("Avatar Extension content script loaded");
safeInitialize();

// Demo function for testing (can be called from console)
window.avatarDemo = function () {
  console.log("🤖 Avatar Demo Started!");

  // Show help guide first
  setTimeout(() => {
    showHelpGuide();
  }, 500);

  // Demo the speech
  setTimeout(() => {
    speakText("Welcome to your new avatar assistant!");
    showSpeech(
      "🎉 **Welcome!** Your avatar now has a beautiful circular menu design. Hover over me to see all the new buttons!"
    );
  }, 2000);

  // Demo emotion
  setTimeout(() => {
    updateAvatarEmotion("happy");
  }, 3000);

  console.log("💡 Try these commands:");
  console.log("- avatarDemo() - Run this demo again");
  console.log("- Hover over the avatar to see the circular menu");
  console.log("- Click the ❓ button for the full help guide");
};
