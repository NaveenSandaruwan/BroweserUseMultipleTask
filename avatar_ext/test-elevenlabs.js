// Test script for ElevenLabs TTS integration
// Run this in browser console to test the integration

console.log("Testing ElevenLabs TTS Integration...");

// Test 1: Check if ElevenLabs module is loaded
if (typeof window.elevenLabsTTS !== "undefined") {
  console.log("✅ ElevenLabs TTS module loaded successfully");
} else {
  console.error("❌ ElevenLabs TTS module not found");
}

// Test 2: Check if configuration functions exist
if (typeof createElevenLabsConfigModal === "function") {
  console.log("✅ Configuration modal function available");
} else {
  console.error("❌ Configuration modal function not found");
}

// Test 3: Check if utility functions exist
if (typeof isElevenLabsEnabled === "function") {
  console.log("✅ Utility functions available");
  console.log("ElevenLabs enabled:", isElevenLabsEnabled());
} else {
  console.error("❌ Utility functions not found");
}

// Test 4: Check avatar UI elements
const avatar = document.getElementById("python-avatar");
const configBtn = document.getElementById("elevenlabs-config");
const speechBubble = document.getElementById("python-avatar-speech");

if (avatar) {
  console.log("✅ Avatar element found");
} else {
  console.error("❌ Avatar element not found");
}

if (configBtn) {
  console.log("✅ ElevenLabs config button found");
} else {
  console.error("❌ ElevenLabs config button not found");
}

if (speechBubble) {
  console.log("✅ Speech bubble found");
} else {
  console.error("❌ Speech bubble not found");
}

// Test 5: Test markdown conversion
if (window.elevenLabsTTS && window.elevenLabsTTS.removeMarkdown) {
  const testMarkdown =
    "**Bold text** and *italic text* with `code` and [link](url)";
  const converted = window.elevenLabsTTS.removeMarkdown(testMarkdown);
  console.log("✅ Markdown conversion test:");
  console.log("Input:", testMarkdown);
  console.log("Output:", converted);
} else {
  console.error("❌ Markdown conversion function not available");
}

// Test 6: Test sentence splitting
if (window.elevenLabsTTS && window.elevenLabsTTS.splitIntoSentences) {
  const testText = "test";
  const sentences = window.elevenLabsTTS.splitIntoSentences(testText);
  console.log("✅ Sentence splitting test:");
  console.log("Input:", testText);
  console.log("Output pairs:", sentences);
} else {
  console.error("❌ Sentence splitting function not available");
}

// Test 7: Quick voice test
if (
  window.elevenLabsTTS &&
  typeof ELEVENLABS_API_KEY !== "undefined" &&
  ELEVENLABS_API_KEY !== "YOUR_ELEVENLABS_API_KEY_HERE"
) {
  console.log("🎵 Testing ElevenLabs voice with word 'test'");

  // Test the voice
  window.elevenLabsTTS.setApiKey(ELEVENLABS_API_KEY);
  window.elevenLabsTTS
    .initialize()
    .then(() => {
      return window.elevenLabsTTS.speakText("test");
    })
    .then(() => {
      console.log("✅ Voice test completed successfully!");
    })
    .catch((error) => {
      console.error("❌ Voice test failed:", error);
    });
} else {
  console.log("⚠️ Skipping voice test - ElevenLabs not properly configured");
}

// Instructions
console.log("\n📋 To fully test ElevenLabs integration:");
console.log("1. Click the 🎵 button to open configuration");
console.log("2. Enter your ElevenLabs API key");
console.log('3. Click "Test TTS" to verify API connection');
console.log("4. Save configuration and test with voice input");

console.log("\n🔧 If issues occur:");
console.log("- Check browser console for errors");
console.log("- Verify API key is correct");
console.log("- Check network connectivity");
console.log("- Try the fallback browser TTS by removing API key");
