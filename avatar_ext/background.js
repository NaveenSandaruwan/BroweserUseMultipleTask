// Simple background script for Avatar Controller extension

console.log("Avatar Controller: Background script loaded");

// Listen for install event to set up initial state
chrome.runtime.onInstalled.addListener(() => {
  console.log("Avatar Controller extension installed");
});

// Listen for extension icon clicks
chrome.action.onClicked.addListener((tab) => {
  console.log("Extension icon clicked");
  // Toggle the visibility of the avatar UI
  chrome.tabs.sendMessage(tab.id, { action: "toggleAvatarUI" });
});

// Simple message handler
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "ping") {
    sendResponse({ status: "ok", message: "Avatar extension is active" });
    return true;
  }
});
