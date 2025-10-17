// =========================
// ElevenLabs Configuration UI
// =========================

// HARDCODED API KEY CONFIGURATION
// ================================
// Instructions:
// 1. Get your API key from https://elevenlabs.io (sign up/login → Profile → API Keys)
// 2. Replace "YOUR_ELEVENLABS_API_KEY_HERE" below with your actual API key
// 3. Keep the quotes around your API key
// Example: const ELEVENLABS_API_KEY = "sk-1234567890abcdef...";

const ELEVENLABS_API_KEY = "sk_f4b3bb0d47ca1343ea38c5a2542652559fffe589bddeccf5";

// Create configuration modal for ElevenLabs
function createElevenLabsConfigModal() {
  // Remove existing modal if present
  const existingModal = document.getElementById("elevenlabs-config-modal");
  if (existingModal) {
    existingModal.remove();
  }

  const modal = document.createElement("div");
  modal.id = "elevenlabs-config-modal";
  modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        z-index: 20000;
        display: flex;
        justify-content: center;
        align-items: center;
        font-family: Arial, sans-serif;
    `;

  const modalContent = document.createElement("div");
  modalContent.style.cssText = `
        background: white;
        padding: 30px;
        border-radius: 10px;
        max-width: 500px;
        width: 90%;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    `;

  modalContent.innerHTML = `
        <h2 style="margin-top: 0; color: #333;">ElevenLabs Configuration</h2>
        <p style="color: #666; margin-bottom: 20px;">
            ElevenLabs TTS is configured with a hardcoded API key.
            ${
              ELEVENLABS_API_KEY !== "YOUR_ELEVENLABS_API_KEY_HERE"
                ? '<span style="color: #34A853;">✅ API Key is set</span>'
                : '<span style="color: #EA4335;">❌ Please set ELEVENLABS_API_KEY in elevenlabs-config.js</span>'
            }
        </p>
        
        <div style="margin-bottom: 20px;">
            <label for="api-key-input" style="display: block; margin-bottom: 5px; font-weight: bold;">API Key Status:</label>
            <input 
                type="text" 
                id="api-key-input" 
                value="${
                  ELEVENLABS_API_KEY !== "YOUR_ELEVENLABS_API_KEY_HERE"
                    ? "Hardcoded API key configured"
                    : "Please set ELEVENLABS_API_KEY in code"
                }"
                disabled
                style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; background: #f8f9fa;"
            />
        </div>

        <div style="margin-bottom: 20px;">
            <label for="voice-select" style="display: block; margin-bottom: 5px; font-weight: bold;">Voice:</label>
            <select 
                id="voice-select"
                style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;"
            >
                <option value="21m00Tcm4TlvDq8ikWAM">Rachel (Default)</option>
                <option value="AZnzlk1XvdvUeBnXmlld">Domi</option>
                <option value="EXAVITQu4vr4xnSDxMaL">Bella</option>
                <option value="ErXwobaYiN019PkySvjV">Antoni</option>
                <option value="MF3mGyEYCl7XYWbV9V6O">Elli</option>
                <option value="TxGEqnHWrfWFTfGW9XjX">Josh</option>
            </select>
        </div>

        <div style="margin-bottom: 20px;">
            <button 
                id="test-tts-btn"
                style="padding: 8px 16px; background: #34A853; color: white; border: none; border-radius: 5px; cursor: pointer; margin-right: 10px;"
            >
                Test TTS
            </button>
            <button 
                id="load-voices-btn"
                style="padding: 8px 16px; background: #4285f4; color: white; border: none; border-radius: 5px; cursor: pointer;"
            >
                Load My Voices
            </button>
        </div>

        <div style="display: flex; gap: 10px; justify-content: flex-end;">
            <button 
                id="cancel-config-btn"
                style="padding: 10px 20px; background: #f1f1f1; color: #333; border: none; border-radius: 5px; cursor: pointer;"
            >
                Cancel
            </button>
            <button 
                id="save-config-btn"
                style="padding: 10px 20px; background: #4285f4; color: white; border: none; border-radius: 5px; cursor: pointer;"
            >
                Save & Use ElevenLabs
            </button>
        </div>

        <div id="config-status" style="margin-top: 15px; padding: 10px; border-radius: 5px; display: none;"></div>
    `;

  modal.appendChild(modalContent);
  document.body.appendChild(modal);

  // Load existing configuration
  loadExistingConfig();

  // Event listeners
  document.getElementById("cancel-config-btn").addEventListener("click", () => {
    modal.remove();
  });

  document
    .getElementById("save-config-btn")
    .addEventListener("click", async () => {
      const voiceId = document.getElementById("voice-select").value;

      // Check if hardcoded API key is set
      if (ELEVENLABS_API_KEY === "YOUR_ELEVENLABS_API_KEY_HERE") {
        showConfigStatus(
          "Please set ELEVENLABS_API_KEY in elevenlabs-config.js file",
          "error"
        );
        return;
      }

      try {
        // Configure ElevenLabs with hardcoded API key
        window.elevenLabsTTS.setApiKey(ELEVENLABS_API_KEY);
        window.elevenLabsTTS.setVoiceId(voiceId);
        await window.elevenLabsTTS.initialize();

        // Store voice preference
        localStorage.setItem("elevenlabs_voice_id", voiceId);

        showConfigStatus("ElevenLabs TTS configured successfully!", "success");

        setTimeout(() => {
          modal.remove();
          // Update status in main UI
          const statusEl = document.getElementById("status");
          if (statusEl) {
            statusEl.textContent = "ElevenLabs TTS ready";
            setTimeout(() => {
              statusEl.textContent = "";
            }, 3000);
          }
        }, 1500);
      } catch (error) {
        showConfigStatus(
          "Error configuring ElevenLabs: " + error.message,
          "error"
        );
      }
    });

  document
    .getElementById("test-tts-btn")
    .addEventListener("click", async () => {
      const voiceId = document.getElementById("voice-select").value;

      // Check if hardcoded API key is set
      if (ELEVENLABS_API_KEY === "YOUR_ELEVENLABS_API_KEY_HERE") {
        showConfigStatus(
          "Please set ELEVENLABS_API_KEY in elevenlabs-config.js file",
          "error"
        );
        return;
      }

      try {
        showConfigStatus("Testing TTS...", "info");

        // Configure for test with hardcoded API key
        window.elevenLabsTTS.setApiKey(ELEVENLABS_API_KEY);
        window.elevenLabsTTS.setVoiceId(voiceId);
        await window.elevenLabsTTS.initialize();

        await window.elevenLabsTTS.testTTS();
        showConfigStatus("TTS test successful!", "success");
      } catch (error) {
        showConfigStatus("TTS test failed: " + error.message, "error");
      }
    });

  document
    .getElementById("load-voices-btn")
    .addEventListener("click", async () => {
      // Check if hardcoded API key is set
      if (ELEVENLABS_API_KEY === "YOUR_ELEVENLABS_API_KEY_HERE") {
        showConfigStatus(
          "Please set ELEVENLABS_API_KEY in elevenlabs-config.js file",
          "error"
        );
        return;
      }

      try {
        showConfigStatus("Loading voices...", "info");

        window.elevenLabsTTS.setApiKey(ELEVENLABS_API_KEY);
        await window.elevenLabsTTS.initialize();

        const voices = await window.elevenLabsTTS.getAvailableVoices();
        updateVoiceSelect(voices);
        showConfigStatus("Voices loaded successfully!", "success");
      } catch (error) {
        showConfigStatus("Error loading voices: " + error.message, "error");
      }
    });

  // Close modal when clicking outside
  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.remove();
    }
  });
}

// Load existing configuration
function loadExistingConfig() {
  // Load voice preference from localStorage
  const voiceId = localStorage.getItem("elevenlabs_voice_id");

  if (voiceId) {
    const voiceSelect = document.getElementById("voice-select");
    if (voiceSelect.querySelector(`option[value="${voiceId}"]`)) {
      voiceSelect.value = voiceId;
    }
  }

  // Update API key status display
  const apiKeyInput = document.getElementById("api-key-input");
  if (apiKeyInput) {
    apiKeyInput.value =
      ELEVENLABS_API_KEY !== "YOUR_ELEVENLABS_API_KEY_HERE"
        ? "Hardcoded API key configured"
        : "Please set ELEVENLABS_API_KEY in code";
  }
}

// Update voice select dropdown with user's voices
function updateVoiceSelect(voices) {
  const voiceSelect = document.getElementById("voice-select");

  // Clear existing options except defaults
  voiceSelect.innerHTML = `
        <option value="21m00Tcm4TlvDq8ikWAM">Rachel (Default)</option>
        <option value="AZnzlk1XvdvUeBnXmlld">Domi</option>
        <option value="EXAVITQu4vr4xnSDxMaL">Bella</option>
        <option value="ErXwobaYiN019PkySvjV">Antoni</option>
        <option value="MF3mGyEYCl7XYWbV9V6O">Elli</option>
        <option value="TxGEqnHWrfWFTfGW9XjX">Josh</option>
    `;

  // Add user's custom voices
  if (voices && voices.length > 0) {
    const userVoices = voices.filter(
      (voice) =>
        ![
          "21m00Tcm4TlvDq8ikWAM",
          "AZnzlk1XvdvUeBnXmlld",
          "EXAVITQu4vr4xnSDxMaL",
          "ErXwobaYiN019PkySvjV",
          "MF3mGyEYCl7XYWbV9V6O",
          "TxGEqnHWrfWFTfGW9XjX",
        ].includes(voice.voice_id)
    );

    if (userVoices.length > 0) {
      // Add separator
      const separator = document.createElement("option");
      separator.disabled = true;
      separator.textContent = "--- Your Custom Voices ---";
      voiceSelect.appendChild(separator);

      // Add user voices
      userVoices.forEach((voice) => {
        const option = document.createElement("option");
        option.value = voice.voice_id;
        option.textContent = `${voice.name} (Custom)`;
        voiceSelect.appendChild(option);
      });
    }
  }
}

// Show status message in config modal
function showConfigStatus(message, type) {
  const statusEl = document.getElementById("config-status");
  if (!statusEl) return;

  statusEl.style.display = "block";
  statusEl.textContent = message;

  // Style based on type
  switch (type) {
    case "success":
      statusEl.style.background = "#d4edda";
      statusEl.style.color = "#155724";
      statusEl.style.border = "1px solid #c3e6cb";
      break;
    case "error":
      statusEl.style.background = "#f8d7da";
      statusEl.style.color = "#721c24";
      statusEl.style.border = "1px solid #f5c6cb";
      break;
    case "info":
      statusEl.style.background = "#d1ecf1";
      statusEl.style.color = "#0c5460";
      statusEl.style.border = "1px solid #bee5eb";
      break;
    default:
      statusEl.style.background = "#f8f9fa";
      statusEl.style.color = "#495057";
      statusEl.style.border = "1px solid #dee2e6";
  }
}

// Check if ElevenLabs is configured and enabled
function isElevenLabsEnabled() {
  // Always return true when hardcoded API key is available
  return (
    ELEVENLABS_API_KEY && ELEVENLABS_API_KEY !== "YOUR_ELEVENLABS_API_KEY_HERE"
  );
}

// Initialize ElevenLabs if configured
async function initializeElevenLabsIfConfigured() {
  if (isElevenLabsEnabled()) {
    try {
      // Use hardcoded API key
      const apiKey = ELEVENLABS_API_KEY;
      const voiceId =
        localStorage.getItem("elevenlabs_voice_id") || "21m00Tcm4TlvDq8ikWAM";

      window.elevenLabsTTS.setApiKey(apiKey);
      window.elevenLabsTTS.setVoiceId(voiceId);
      await window.elevenLabsTTS.initialize();

      console.log(
        "ElevenLabs TTS initialized successfully with hardcoded API key"
      );
      return true;
    } catch (error) {
      console.error("Error initializing ElevenLabs:", error);
      return false;
    }
  }
  console.log("ElevenLabs not enabled - please set ELEVENLABS_API_KEY");
  return false;
}
