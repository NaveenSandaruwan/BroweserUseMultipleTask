// =========================
// Elements
// =========================
const micBtn = document.getElementById("mic");
const statusEl = document.getElementById("status");

// =========================
// Speech Recognition
// =========================
const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;

if (!SpeechRecognitionAPI) {
  alert("Speech recognition not supported");
} else {
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
  
  // This is the part of your JavaScript code that runs after the user has finished speaking.
  recognition.onresult = async (event) => {
    const transcript = event.results[0][0].transcript.trim();
    console.log("Heard:", transcript);

    try {
        const response = await fetch("http://127.0.0.1:5000/speak", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: transcript }),
        });

        if (!response.ok) throw new Error("Network response not OK");

        // The backend's JSON response is parsed here.
        const data = await response.json(); 
        console.log("Backend reply:", data);

        // The reply from the backend is passed to the showSpeech function.
        showSpeech(data.reply, 6000); 

        // The same reply is also passed to the function that speaks the text.
        speakText(data.reply);

    } catch (err) {
        console.error("Error:", err);
        const fallbackReply = `AI says: I heard '${transcript}'.`;
        showSpeech(fallbackReply, 4000);
        speakText(fallbackReply);
    }
  };

}

// =========================
// Avatar Bubble Functions
// =========================
function showSpeech(text, duration = 5000) {
  let speechBubble = document.getElementById("python-avatar-speech");

  // Create bubble if not exists
  if (!speechBubble) {
    const avatarContainer = document.getElementById("python-avatar-container");
    if (!avatarContainer) return;

    speechBubble = document.createElement("div");
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
    avatarContainer.appendChild(speechBubble);
  }

  speechBubble.textContent = text;
  speechBubble.style.opacity = 1;

  if (duration > 0) {
    setTimeout(() => (speechBubble.style.opacity = 0), duration);
  }
}

// =========================
// Browser TTS
// =========================
function speakText(text) {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel(); // stop previous speech

    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = 'en-US';
    utter.pitch = 1.5; // child-like voice
    utter.rate = 1.1;

    utter.onstart = () => console.log("Speech started");
    utter.onend = () => console.log("Speech ended");
    utter.onerror = (e) => console.error("Speech error", e);

    window.speechSynthesis.speak(utter);
  } else {
    console.log("Browser TTS not supported");
  }
}
