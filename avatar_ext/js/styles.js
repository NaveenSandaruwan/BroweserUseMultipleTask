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
    #avatar-mouth, #left-eyebrow, #right-eyebrow, #left-pupil, #right-pupil {
      transition: all 0.5s ease-in-out;
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
    
    /* General avatar container styles */
    #avatar-extension-container {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
    
    /* Status text styling */
    #status {
      text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
  `;
  
  document.head.appendChild(avatarStyles);
}

// Export functions
window.AvatarStyles = {
  initializeStyles
};