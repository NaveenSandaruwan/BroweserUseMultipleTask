(function () {
  console.log("Avatar Extension loaded");
  
  // Create the avatar image element
  let avatar = document.createElement("img");
  avatar.src = chrome.runtime.getURL("images/avatar.png"); // Path to your avatar image
  avatar.id = "py-controlled-avatar";
  
  // Set initial styling for the avatar
  // avatar.style.position = "fixed";        // Fixed positioning so it stays in viewport
  // avatar.style.left = "50px";             // Initial X position
  // avatar.style.top = "50px";              // Initial Y position
  // avatar.style.width = "80px";            // Avatar width
  // avatar.style.height = "80px";           // Avatar height
  // avatar.style.zIndex = "9999";           // High z-index to appear on top
  // avatar.style.borderRadius = "50%";      // Make it circular
  // avatar.style.border = "3px solid #4CAF50"; // Green border
  // avatar.style.cursor = "pointer";        // Pointer cursor on hover
  // avatar.style.transition = "all 0.2s ease"; // Smooth animations
  // avatar.style.boxShadow = "0 4px 8px rgba(0,0,0,0.3)"; // Shadow effect
  
  Object.assign(avatar.style, {
        position: "fixed",
        left: "50px",
        top: "50px",
        width: "80px",
        height: "80px",
        zIndex: "9999",
        borderRadius: "50%",
        border: "3px solid #4CAF50",
        cursor: "pointer",
        transition: "all 0.2s ease",
        pointerEvents: "none"
    });

  // Add the avatar to the page
  document.body.appendChild(avatar);

  // Position tracking object
  let pos = { x: 50, y: 50 };
  
  // Function to update avatar position on screen
  function updatePos() {
    // Prevent avatar from going off-screen
    pos.x = Math.max(0, Math.min(window.innerWidth - 80, pos.x));
    pos.y = Math.max(0, Math.min(window.innerHeight - 80, pos.y));
    
    avatar.style.left = pos.x + "px";
    avatar.style.top = pos.y + "px";
  }

  // Listen for messages from Python (via Selenium WebDriver)
  window.addEventListener("message", (event) => {
    // Check if message is valid and for our extension
    if (!event.data || event.data.type !== "AVATAR_CMD") return;
    
    const cmd = event.data.cmd; // Extract command type
    console.log("Received command:", cmd, event.data);

    // Handle different command types
    if (cmd === "move") {
      // Move avatar by specified amounts
      pos.x += event.data.dx || 0;  // Move horizontally
      pos.y += event.data.dy || 0;  // Move vertically
      updatePos();
      
    } else if (cmd === "hide") {
      // Hide the avatar
      avatar.style.display = "none";
      
    } else if (cmd === "show") {
      // Show the avatar
      avatar.style.display = "block";
      
    } else if (cmd === "center") {
      // Center avatar on screen
      pos.x = (window.innerWidth / 2) - 40;   // Center horizontally
      pos.y = (window.innerHeight / 2) - 40;  // Center vertically
      updatePos();
      
    } else if (cmd === "rotate") {
      // Rotate avatar by specified degrees
      avatar.style.transform = `rotate(${event.data.deg || 0}deg)`;
      
    } else if (cmd === "teleport") {
      // Jump to specific coordinates
      pos.x = event.data.x || pos.x;
      pos.y = event.data.y || pos.y;
      updatePos();
      
    } else if (cmd === "resize") {
      // Change avatar size
      const size = event.data.size || 80;
      avatar.style.width = size + "px";
      avatar.style.height = size + "px";
      
    } else if (cmd === "color") {
      // Change border color
      avatar.style.border = `3px solid ${event.data.color || '#4CAF50'}`;
    }
  });

  // Keyboard controls for manual movement
  document.addEventListener("keydown", (e) => {
    const step = e.shiftKey ? 40 : 20; // Larger steps when holding Shift
    
    switch(e.key) {
      case "ArrowUp":
        pos.y -= step;
        e.preventDefault(); // Prevent page scrolling
        break;
      case "ArrowDown":
        pos.y += step;
        e.preventDefault();
        break;
      case "ArrowLeft":
        pos.x -= step;
        e.preventDefault();
        break;
      case "ArrowRight":
        pos.x += step;
        e.preventDefault();
        break;
      case " ": // Spacebar to center
        pos.x = (window.innerWidth / 2) - 40;
        pos.y = (window.innerHeight / 2) - 40;
        e.preventDefault();
        break;
    }
    updatePos();
  });

  // Handle window resize to keep avatar in bounds
  window.addEventListener("resize", updatePos);
  
  // Add click handler for fun interaction
  avatar.addEventListener("click", () => {
    // Bounce effect on click
    avatar.style.transform = "scale(1.2)";
    setTimeout(() => {
      avatar.style.transform = "scale(1)";
    }, 200);
  });
  
  console.log("Avatar Extension fully initialized");
})();