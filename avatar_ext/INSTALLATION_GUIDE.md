# 🚀 Avatar Extension Installation & Troubleshooting Guide

## 📦 Installation Steps

### 1. Prepare the Extension

1. Make sure all files are in the `avatar_ext` folder
2. Verify the `manifest.json` file is present and valid

### 2. Load in Chrome

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (toggle in top-right)
3. Click **"Load unpacked"**
4. Select the `avatar_ext` folder
5. The extension should appear in the list

### 3. Verify Installation

1. Look for the extension in the Chrome extensions list
2. Make sure it's **enabled** (toggle switch on)
3. Check for any **error messages** in red

## 🧪 Testing the Extension

### Option 1: Use the Test Page

1. Open `test-page.html` in Chrome (double-click the file)
2. The page will automatically check for the extension
3. Use the buttons to test various features

### Option 2: Manual Testing

1. Go to any website (e.g., google.com)
2. Look for the avatar in the **top-right corner**
3. You should see:
   - 🤖 Python avatar (blue circle with yellow face)
   - 🎤 Microphone button (blue)
   - 🔊 Test TTS button (green)
   - 🎵 ElevenLabs Config button (orange)
   - 🎭 Emotion Test button (yellow)
   - 📌 Save Position button (blue)

## 🐛 Troubleshooting

### Problem: Extension doesn't load

**Symptoms:** Extension appears with errors in chrome://extensions/

**Solutions:**

1. Check `manifest.json` syntax (use a JSON validator)
2. Verify all files mentioned in manifest exist
3. Look for specific error messages in extension details

### Problem: Avatar doesn't appear

**Symptoms:** Extension loads but no avatar visible on pages

**Solutions:**

1. **Check Console Errors:**

   - Press `F12` on any webpage
   - Go to **Console** tab
   - Look for red error messages
   - Common errors: "Failed to load resource", "Uncaught SyntaxError"

2. **Manual Check:**

   - Press `F12` → Console tab
   - Type: `document.getElementById('avatar-extension-container')`
   - If it returns `null`, the content script isn't running

3. **Force Reload:**
   - Go to `chrome://extensions/`
   - Click the **reload icon** on your extension
   - Refresh the webpage

### Problem: ElevenLabs button missing

**Symptoms:** Avatar appears but no 🎵 button

**Possible Causes:**

1. `elevenlabs-config.js` not loading
2. JavaScript errors preventing button creation
3. API key not set correctly

**Solutions:**

1. Check browser console for errors
2. Verify API key is set in `js/elevenlabs-config.js`
3. Make sure `ELEVENLABS_API_KEY` is not `"YOUR_ELEVENLABS_API_KEY_HERE"`

### Problem: Console errors

**Common Error Messages and Solutions:**

#### "Uncaught ReferenceError: createElevenLabsConfigModal is not defined"

- **Cause:** `elevenlabs-config.js` not loading
- **Fix:** Check file exists and manifest.json lists it correctly

#### "Failed to load resource: net::ERR_FILE_NOT_FOUND"

- **Cause:** Missing file referenced in manifest
- **Fix:** Check all paths in manifest.json are correct

#### "Uncaught SyntaxError: Unexpected token"

- **Cause:** JavaScript syntax error
- **Fix:** Check for missing brackets, quotes, or semicolons

#### "Content Security Policy violation"

- **Cause:** Trying to load external resources
- **Fix:** Already handled in manifest.json

## 🔧 Debug Commands

Copy and paste these into the browser console (F12 → Console):

### Check if extension loaded:

```javascript
console.log(
  "Avatar container:",
  document.getElementById("avatar-extension-container")
);
console.log("ElevenLabs function:", typeof createElevenLabsConfigModal);
console.log(
  "API key set:",
  typeof ELEVENLABS_API_KEY !== "undefined" &&
    ELEVENLABS_API_KEY !== "YOUR_ELEVENLABS_API_KEY_HERE"
);
```

### Force create avatar:

```javascript
if (typeof createAvatarUI === "function") {
  createAvatarUI();
  console.log("Avatar creation attempted");
} else {
  console.log("createAvatarUI function not found");
}
```

### Check ElevenLabs integration:

```javascript
if (window.elevenLabsTTS) {
  console.log("ElevenLabs class found");
  console.log(
    "API key configured:",
    window.elevenLabsTTS.apiKey ? "Yes" : "No"
  );
} else {
  console.log("ElevenLabs class not found");
}
```

## ✅ Success Indicators

When everything is working correctly, you should see:

- 🤖 Avatar in top-right corner of web pages
- 5 buttons around the avatar
- Console messages: "Avatar Extension content script loaded" and "Avatar UI created successfully"
- No red error messages in console
- Ability to drag the avatar around
- Click 🎵 button opens ElevenLabs configuration modal

## 📞 Still Need Help?

If you're still having issues:

1. **Check browser console** for specific error messages
2. **Try a clean install:**
   - Remove extension from chrome://extensions/
   - Restart Chrome
   - Load unpacked again
3. **Test on a simple page** like about:blank or google.com
4. **Check file permissions** - make sure Chrome can read all files

The most common issue is JavaScript syntax errors preventing the content script from loading properly. Always check the browser console first!
