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


function createAvatarUI() {
  // Check if UI already exists
  if (document.getElementById("avatar-extension-container")) {
    return getUIElements();
  }

  // --- Main Container (Position: Top Right) ---
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
    `;

  // --- Avatar Graphic Element ---
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
        
        /* Positioning to the left of the avatar (since we're on right side of window) */
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

  // Create a button container for all the small buttons
  const buttonContainer = document.createElement("div");
  buttonContainer.style.cssText = `
        display: flex;
        gap: 10px;
        margin-bottom: 10px;
    `;
  buttonContainer.appendChild(ttsBtn);
  buttonContainer.appendChild(emotionBtn);

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


const SpeechRecognitionAPI =
  window.SpeechRecognition || window.webkitSpeechRecognition;

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
      // First, detect emotion from user input
      const emotion = await detectEmotion(transcript);

      // Update avatar based on detected emotion
      updateAvatarEmotion(emotion);

      // Now send the message to the LLM for response
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
      const fallbackReply = `AI says: 'I heard '${transcript}', but there was an error connecting to the backend.'`;
      showSpeech(fallbackReply);
      speakText(fallbackReply);

      // Set to neutral emotion on error
      updateAvatarEmotion("neutral");
    }
  };
}


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



// Function to detect emotion from text
async function detectEmotion(text) {
  try {
    const response = await fetch("http://127.0.0.1:5000/emotion", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: text,
        include_history: true,
      }),
    });

    if (!response.ok) {
      throw new Error(`Emotion detection failed: ${response.status}`);
    }

    const data = await response.json();
    console.log("Emotion detected:", data.emotion);
    return data.emotion;
  } catch (error) {
    console.error("Emotion detection error:", error);
    return "neutral"; // Default fallback
  }
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

// Start the process of creating the UI when the script loads.
createAvatarUI();
