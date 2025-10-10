// =========================
// WebSocket Communication
// =========================

// WebSocket connection variables
let socket = null;
let isSocketConnected = false;

/**
 * Establish WebSocket connection
 * @returns {WebSocket} Socket instance
 */
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
        window.AvatarAnimations.stopThinkingAnimation();

        // Chat response already has emotion processed earlier
        // Just display the reply and speak it

        // If emotion is provided again, update it (but it should already be updated)
        if (data.emotion) {
          console.log("Chat response includes emotion:", data.emotion);
          // No need to call updateAvatarEmotion again as we've already done it
          // in the separate emotion request, but do it as a fallback
          window.AvatarAnimations.updateAvatarEmotion(data.emotion);
        }

        // Display and speak the reply
        if (data.reply) {
          // Display the reply with markdown rendering
          window.AvatarUI.showSpeech(data.reply);

          // Speak the reply
          window.AvatarSpeech.speakText(data.reply);

          const statusEl = document.getElementById("status");
          if (statusEl) statusEl.textContent = "Reply received";
        }
      } else if (responseType === "emotion") {
        // Handle emotion-only response - this comes first in our new flow
        if (data.emotion) {
          console.log("Got emotion response first:", data.emotion);
          // Update avatar based on received emotion immediately
          window.AvatarAnimations.updateAvatarEmotion(data.emotion);

          const statusEl = document.getElementById("status");
          if (statusEl)
            statusEl.textContent = `Processing with emotion: ${data.emotion}`;

          // Start thinking animation instead of showing text
          window.AvatarAnimations.startThinkingAnimation();
        }
      } else if (responseType === "error") {
        // Stop thinking animation on error
        window.AvatarAnimations.stopThinkingAnimation();

        console.error("Server returned error:", data.error);
        const statusEl = document.getElementById("status");
        if (statusEl) statusEl.textContent = `Error: ${data.error}`;

        // Show the error in speech bubble (instant for errors)
        window.AvatarUI.showSpeechInstant(`Error: ${data.error}`);
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

/**
 * Send message via WebSocket
 * @param {Object} message - Message object to send
 */
function sendMessage(message) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(message));
  } else {
    console.error("WebSocket not connected");
  }
}

/**
 * Check if WebSocket is connected
 * @returns {boolean} Connection status
 */
function isConnected() {
  return isSocketConnected;
}

/**
 * Get socket instance
 * @returns {WebSocket} Socket instance
 */
function getSocket() {
  return socket;
}

// Export functions
window.AvatarWebSocket = {
  connectWebSocket,
  sendMessage: sendMessage,
  isSocketConnected: isConnected,
  getSocket,
};
