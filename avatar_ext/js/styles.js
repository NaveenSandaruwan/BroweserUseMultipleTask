// =========================
// CSS Styles for Avatar Extension
// =========================

/**
 * Initialize all CSS styles for the avatar extension
 */
function initializeStyles() {
  // Add SVG animation styles
  const avatarStyles = document.createElement("style");
  avatarStyles.textContent = `
    /* Avatar animations */
    #left-eyebrow, #right-eyebrow, #left-pupil, #right-pupil {
      transition: all 0.5s ease-in-out;
    }
    
    /* Emoji-style mouth animation optimized for lip sync */
    #upper-mouth, #lower-mouth {
      transition: all 0.08s ease-out;
    }
    
    #mouth-group {
      transition: all 0.08s ease-out;
    }
    
    @keyframes blink {
      0% { transform: scaleY(1); }
      45% { transform: scaleY(1); }
      50% { transform: scaleY(0.1); }
      55% { transform: scaleY(1); }
      100% { transform: scaleY(1); }
    }
    
    #eyes {
      transform-origin: center;
      animation: blink 4s infinite;
    }

    /* Avatar container hover effects */
    #avatar-extension-container {
      transition: all 0.3s ease;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    #avatar-extension-container:hover {
      filter: drop-shadow(0 0 20px rgba(55, 118, 171, 0.3));
    }

    /* Menu container styles */
    #avatar-menu-container {
      transition: all 0.3s ease;
    }

    #avatar-menu-button {
      transition: all 0.3s ease;
    }

    #avatar-menu-button:hover {
      transform: scale(1.1);
      box-shadow: 0 6px 20px rgba(0,0,0,0.4);
    }

    /* Dropdown menu animations */
    #avatar-dropdown-menu {
      transition: all 0.3s ease;
    }

    /* Menu item hover effects */
    .menu-item {
      transition: background-color 0.2s ease;
    }

    .menu-item:hover {
      background-color: #f5f5f5;
    }

    /* Status element improvements */
    #status {
      transition: all 0.3s ease;
      text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }

    /* Help modal scrollbar */
    #avatar-help-modal div::-webkit-scrollbar {
      width: 8px;
    }
    
    #avatar-help-modal div::-webkit-scrollbar-track {
      background: rgba(255,255,255,0.1);
      border-radius: 4px;
    }
    
    #avatar-help-modal div::-webkit-scrollbar-thumb {
      background: rgba(255,255,255,0.3);
      border-radius: 4px;
    }
    
    #avatar-help-modal div::-webkit-scrollbar-thumb:hover {
      background: rgba(255,255,255,0.5);
    }
    
    /* Speech bubble enhancements */
    #python-avatar-speech {
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
    }
    
    #python-avatar-speech::-webkit-scrollbar {
      width: 6px;
    }
    
    #python-avatar-speech::-webkit-scrollbar-track {
      background: #f1f1f1;
      border-radius: 3px;
    }
    
    #python-avatar-speech::-webkit-scrollbar-thumb {
      background: #888;
      border-radius: 3px;
    }
    
    #python-avatar-speech::-webkit-scrollbar-thumb:hover {
      background: #555;
    }
    
    /* Thinking animation styles */
    .thinking-dots {
      position: absolute;
      top: -10px;
      right: -10px;
      display: flex;
      gap: 3px;
    }
    
    .thinking-dot {
      width: 6px;
      height: 6px;
      background: #3776AB;
      border-radius: 50%;
      animation: thinkingPulse 1.4s ease-in-out infinite both;
    }
    
    .thinking-dot:nth-child(1) { animation-delay: -0.32s; }
    .thinking-dot:nth-child(2) { animation-delay: -0.16s; }
    .thinking-dot:nth-child(3) { animation-delay: 0; }
    
    @keyframes thinkingPulse {
      0%, 80%, 100% {
        transform: scale(0.8);
        opacity: 0.5;
      }
      40% {
        transform: scale(1.2);
        opacity: 1;
      }
    }
    
    /* Avatar thinking glow effect */
    .avatar-thinking {
      box-shadow: 0 0 20px rgba(55, 118, 171, 0.6) !important;
      animation: thinkingGlow 2s ease-in-out infinite alternate !important;
    }
    
    @keyframes thinkingGlow {
      from {
        box-shadow: 0 0 15px rgba(55, 118, 171, 0.4);
      }
      to {
        box-shadow: 0 0 25px rgba(55, 118, 171, 0.8);
      }
    }
    
    /* Word-by-word animation styles */
    @keyframes wordHighlight {
      0% {
        background-color: transparent;
        transform: scale(1);
      }
      50% {
        background-color: rgba(255, 212, 59, 0.3);
        transform: scale(1.02);
      }
      100% {
        background-color: transparent;
        transform: scale(1);
      }
    }
    
    /* Button hover effects */
    button {
      transition: all 0.2s ease;
    }
    
    button:hover {
      transform: scale(1.05);
      filter: brightness(1.1);
    }
    
    button:active {
      transform: scale(0.95);
    }

    /* Radial menu button styling - fixed positioning */
    .radial-button {
      position: absolute !important;
      border-radius: 50% !important;
      border: none !important;
      cursor: pointer !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      font-size: 18px !important;
      color: white !important;
      width: 45px !important;
      height: 45px !important;
      box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
      /* Fixed transition to prevent positioning shifts */
      transition: transform 0.3s ease, box-shadow 0.3s ease, opacity 0.3s ease !important;
      /* Ensure buttons maintain their exact positions */
      transform-origin: center center !important;
    }

    .radial-button:hover {
      /* Only scale without changing position */
      box-shadow: 0 6px 20px rgba(0,0,0,0.4) !important;
      /* Don't override transform here - let JavaScript handle it */
    }

    /* Radial buttons container */
    #avatar-radial-buttons {
      /* Ensure container doesn't affect button positioning */
      pointer-events: none !important;
    }

    #avatar-radial-buttons .radial-button {
      /* Re-enable pointer events for buttons */
      pointer-events: auto !important;
    }
  `;

  document.head.appendChild(avatarStyles);
}

// Export functions
window.AvatarStyles = {
  initializeStyles,
};
