// Debug script - paste this into browser console to diagnose issues
console.log("=== Avatar Extension Debug ===");

// Check if content script is loaded
console.log("1. Checking if content script loaded...");
if (typeof createAvatarUI === "function") {
  console.log("✅ createAvatarUI function found");
} else {
  console.log("❌ createAvatarUI function NOT found - content.js not loaded");
}

// Check if ElevenLabs scripts are loaded
console.log("2. Checking ElevenLabs integration...");
if (typeof window.elevenLabsTTS !== "undefined") {
  console.log("✅ ElevenLabs TTS class found");
} else {
  console.log("❌ ElevenLabs TTS class NOT found - elevenlabs.js not loaded");
}

if (typeof createElevenLabsConfigModal === "function") {
  console.log("✅ ElevenLabs config function found");
} else {
  console.log(
    "❌ ElevenLabs config function NOT found - elevenlabs-config.js not loaded"
  );
}

if (typeof ELEVENLABS_API_KEY !== "undefined") {
  console.log(
    "✅ API key constant found:",
    ELEVENLABS_API_KEY !== "YOUR_ELEVENLABS_API_KEY_HERE"
      ? "CONFIGURED"
      : "NOT SET"
  );
} else {
  console.log("❌ API key constant NOT found");
}

// Check if avatar UI elements exist in DOM
console.log("3. Checking DOM elements...");
const avatar = document.getElementById("python-avatar");
const container = document.getElementById("avatar-extension-container");
const micBtn = document.getElementById("mic");
const elevenLabsBtn = document.getElementById("elevenlabs-config");

if (container) {
  console.log("✅ Avatar container found");
} else {
  console.log("❌ Avatar container NOT found");
}

if (avatar) {
  console.log("✅ Avatar element found");
} else {
  console.log("❌ Avatar element NOT found");
}

if (micBtn) {
  console.log("✅ Microphone button found");
} else {
  console.log("❌ Microphone button NOT found");
}

if (elevenLabsBtn) {
  console.log("✅ ElevenLabs config button found");
} else {
  console.log("❌ ElevenLabs config button NOT found");
}

// Check for JavaScript errors
console.log("4. Checking for console errors...");
console.log("Check the Console tab for any red error messages");

// Try to manually create the UI
console.log("5. Attempting to manually create UI...");
try {
  if (typeof createAvatarUI === "function") {
    createAvatarUI();
    console.log("✅ UI creation attempted");
  } else {
    console.log("❌ Cannot create UI - function not available");
  }
} catch (error) {
  console.log("❌ Error creating UI:", error);
}

console.log("=== Debug Complete ===");
console.log("Next steps:");
console.log("1. Check browser console for red error messages");
console.log(
  "2. Make sure extension is properly loaded in Chrome Extensions page"
);
console.log("3. Try refreshing the page after loading the extension");
console.log(
  "4. Check if Chrome is blocking the extension due to manifest issues"
);
