// =========================
// Avatar Animation & Emotion Functions
// =========================

/**
 * Update avatar face based on emotion
 * @param {string} emotion - The emotion to display
 */
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

/**
 * Start thinking animation
 */
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

/**
 * Stop thinking animation
 */
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

/**
 * Detect emotion for text via WebSocket
 * @param {string} text - Text to analyze for emotion
 * @returns {Promise<string>} Detected emotion
 */
async function detectEmotion(text) {
  return new Promise((resolve, reject) => {
    try {
      // Ensure WebSocket is connected
      if (!window.AvatarWebSocket.isSocketConnected()) {
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
            window.AvatarWebSocket.getSocket().removeEventListener(
              "message",
              messageHandler
            );
            resolve(data.emotion);
          }
        } catch (e) {
          console.error("Error in emotion detection handler:", e);
        }
      };

      // Add the one-time message handler
      window.AvatarWebSocket.getSocket().addEventListener(
        "message",
        messageHandler
      );

      // Send the emotion request
      window.AvatarWebSocket.send({
        type: "emotion",
        message: text,
      });

      // Set a timeout to prevent hanging if no response
      setTimeout(() => {
        window.AvatarWebSocket.getSocket().removeEventListener(
          "message",
          messageHandler
        );
        console.log("Emotion detection timed out");
        resolve("neutral"); // Default fallback
      }, 3000);
    } catch (error) {
      console.error("Error detecting emotion:", error);
      resolve("neutral"); // Default fallback
    }
  });
}

// Export functions
window.AvatarAnimations = {
  updateAvatarEmotion,
  startThinkingAnimation,
  stopThinkingAnimation,
  detectEmotion,
};
