// =========================
// ElevenLabs Text-to-Speech Integration
// =========================

class ElevenLabsTTS {
  constructor() {
    this.apiKey = null;
    this.voiceId = "21m00Tcm4TlvDq8ikWAM"; // Default voice (Rachel)
    this.baseUrl = "https://api.elevenlabs.io/v1";
    this.isInitialized = false;
    this.audioQueue = [];
    this.isPlaying = false;
  }

  // Initialize with API key (you'll need to set this)
  async initialize(apiKey = null) {
    if (apiKey) {
      this.apiKey = apiKey;
    } else {
      // Try to get from storage or environment
      this.apiKey = await this.getStoredApiKey();
    }

    if (!this.apiKey) {
      console.warn(
        "ElevenLabs API key not provided. Please set it using setApiKey()"
      );
      return false;
    }

    this.isInitialized = true;
    return true;
  }

  // Set API key
  setApiKey(apiKey) {
    this.apiKey = apiKey;
    this.isInitialized = true;
    // Store in local storage for future use
    this.storeApiKey(apiKey);
  }

  // Set voice ID
  setVoiceId(voiceId) {
    this.voiceId = voiceId;
  }

  // Store API key in local storage
  async storeApiKey(apiKey) {
    try {
      localStorage.setItem("elevenlabs_api_key", apiKey);
    } catch (error) {
      console.error("Error storing API key:", error);
    }
  }

  // Get stored API key
  async getStoredApiKey() {
    try {
      return localStorage.getItem("elevenlabs_api_key");
    } catch (error) {
      console.error("Error retrieving API key:", error);
      return null;
    }
  }

  // Split text into sentences (handling multiple sentences)
  splitIntoSentences(text) {
    // Remove markdown formatting for TTS
    const cleanText = this.removeMarkdown(text);

    // Split by sentence endings, keeping the punctuation
    const sentences = cleanText
      .split(/(?<=[.!?])\s+/)
      .filter((sentence) => sentence.trim().length > 0);

    // Group sentences into pairs (2 sentences at a time)
    const sentencePairs = [];
    for (let i = 0; i < sentences.length; i += 2) {
      const pair = sentences
        .slice(i, i + 2)
        .join(" ")
        .trim();
      if (pair) {
        sentencePairs.push(pair);
      }
    }

    return sentencePairs.length > 0 ? sentencePairs : [cleanText];
  }

  // Remove markdown formatting for cleaner TTS
  removeMarkdown(text) {
    return text
      .replace(/\*\*(.*?)\*\*/g, "$1") // Remove bold
      .replace(/\*(.*?)\*/g, "$1") // Remove italic
      .replace(/__(.*?)__/g, "$1") // Remove bold
      .replace(/_(.*?)_/g, "$1") // Remove italic
      .replace(/`(.*?)`/g, "$1") // Remove inline code
      .replace(/#+\s/g, "") // Remove headers
      .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1") // Remove links, keep text
      .replace(/\n/g, " ") // Replace newlines with spaces
      .replace(/\s+/g, " ") // Normalize spaces
      .trim();
  }

  // Generate speech using ElevenLabs API
  async generateSpeech(text) {
    if (!this.isInitialized || !this.apiKey) {
      throw new Error("ElevenLabs TTS not initialized or API key missing");
    }

    const url = `${this.baseUrl}/text-to-speech/${this.voiceId}`;

    const requestData = {
      text: text,
      model_id: "eleven_monolingual_v1",
      voice_settings: {
        stability: 0.5,
        similarity_boost: 0.75,
        style: 0.0,
        use_speaker_boost: true,
      },
    };

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          Accept: "audio/mpeg",
          "Content-Type": "application/json",
          "xi-api-key": this.apiKey,
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `ElevenLabs API error: ${response.status} - ${errorText}`
        );
      }

      const audioBlob = await response.blob();
      return audioBlob;
    } catch (error) {
      console.error("Error generating speech:", error);
      throw error;
    }
  }

  // Create audio element from blob and play it
  async playAudioBlob(audioBlob) {
    return new Promise((resolve, reject) => {
      try {
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);

        audio.onended = () => {
          URL.revokeObjectURL(audioUrl);
          resolve();
        };

        audio.onerror = (error) => {
          URL.revokeObjectURL(audioUrl);
          reject(error);
        };

        audio.play().catch(reject);
      } catch (error) {
        reject(error);
      }
    });
  }

  // Process and speak text in chunks of 2 sentences
  async speakText(text, onProgress = null) {
    if (!text || text.trim() === "") {
      return;
    }

    const sentencePairs = this.splitIntoSentences(text);
    console.log("Processing text in chunks:", sentencePairs);

    this.isPlaying = true;

    try {
      for (let i = 0; i < sentencePairs.length; i++) {
        const chunk = sentencePairs[i];

        if (onProgress) {
          onProgress({
            current: i + 1,
            total: sentencePairs.length,
            text: chunk,
            status: "generating",
          });
        }

        // Generate audio for this chunk
        const audioBlob = await this.generateSpeech(chunk);

        if (onProgress) {
          onProgress({
            current: i + 1,
            total: sentencePairs.length,
            text: chunk,
            status: "playing",
          });
        }

        // Play the audio and wait for it to finish
        await this.playAudioBlob(audioBlob);
      }

      if (onProgress) {
        onProgress({
          current: sentencePairs.length,
          total: sentencePairs.length,
          text: "",
          status: "completed",
        });
      }
    } catch (error) {
      console.error("Error in speakText:", error);
      if (onProgress) {
        onProgress({
          current: 0,
          total: sentencePairs.length,
          text: "",
          status: "error",
          error: error.message,
        });
      }
      throw error;
    } finally {
      this.isPlaying = false;
    }
  }

  // Stop current playback
  stopSpeaking() {
    this.isPlaying = false;
    // Stop all audio elements
    const audioElements = document.querySelectorAll("audio");
    audioElements.forEach((audio) => {
      if (!audio.paused) {
        audio.pause();
        audio.currentTime = 0;
      }
    });
  }

  // Check if currently playing
  isSpeaking() {
    return this.isPlaying;
  }

  // Get available voices from ElevenLabs
  async getAvailableVoices() {
    if (!this.isInitialized || !this.apiKey) {
      throw new Error("ElevenLabs TTS not initialized or API key missing");
    }

    try {
      const response = await fetch(`${this.baseUrl}/voices`, {
        headers: {
          "xi-api-key": this.apiKey,
        },
      });

      if (!response.ok) {
        throw new Error(`Error fetching voices: ${response.status}`);
      }

      const data = await response.json();
      return data.voices;
    } catch (error) {
      console.error("Error fetching voices:", error);
      throw error;
    }
  }

  // Test the TTS with a sample text
  async testTTS(testText = "test") {
    try {
      await this.speakText(testText, (progress) => {
        console.log("TTS Progress:", progress);
      });
      return true;
    } catch (error) {
      console.error("TTS test failed:", error);
      return false;
    }
  }
}

// Create global instance
window.elevenLabsTTS = new ElevenLabsTTS();

// Export for use in other scripts
if (typeof module !== "undefined" && module.exports) {
  module.exports = ElevenLabsTTS;
}
