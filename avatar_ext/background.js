// Simple background script for Avatar Controller extension

console.log("Avatar Controller: Background script loaded");

// Listen for install event to set up initial state
chrome.runtime.onInstalled.addListener(() => {
  console.log("Avatar Controller extension installed");
});

// Simple message handler
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "ping") {
    sendResponse({status: "ok", message: "Avatar extension is active"});
    return true;
  }
});