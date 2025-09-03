document.addEventListener("DOMContentLoaded", () => {
  const elements = {
    userInput: document.getElementById("user-input"),
    sendBtn: document.getElementById("send-btn"),
    attachBtn: document.getElementById("attach-btn"),
    chatMessages: document.getElementById("chat-messages"),
    modelSelect: document.querySelector(".model-select"),
    messageInputContainer: document.querySelector(".message-input-container"),
    rightActions: document.querySelector(".right-actions"),
    clearChatBtn: document.getElementById("clear-chat-btn"),
    downloadChatBtn: document.getElementById("download-chat-btn"),
  };

  // Configuration - SINGLE SOURCE OF TRUTH
  const CONFIG = {
    MAX_MESSAGES: 100,
    MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
    TOTAL_FILE_LIMIT: 3, // Fixed to 3 as required
    MAX_TEXTAREA_HEIGHT: 150,
    ALLOWED_TYPES: [
      "application/pdf",
      "application/vnd.ms-excel",
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "text/plain",
    ],
    ALLOWED_EXTENSIONS: [".pdf", ".xls", ".xlsx", ".txt"],
    SESSION_KEY: "fenny_session_id",
    HISTORY_KEY: "fenny_chat_history",
    FILE_COUNT_KEY: "fenny_total_file_count",
    WELCOME_MESSAGE: "Hi, I'm Fenny! How can I help you today? Feel free to ask me any question on finance, investing, and also feel free to upload any financial documents for analysis."
  };

  let attachedFiles = [];
  let isBotTyping = false;
  let totalFilesInChat = 0;
  let typingIndicator = null;

  /** Initialize file counter - SAFE INITIALIZATION */
  function initializeFileCounter() {
    // Get count from localStorage (always authoritative)
    const storedCount = parseInt(localStorage.getItem(CONFIG.FILE_COUNT_KEY)) || 0;
    
    // Validate against actual chat history
    const history = JSON.parse(localStorage.getItem(CONFIG.HISTORY_KEY) || "[]");
    let actualCount = 0;
    
    history.forEach(msg => {
      // Count files stored in history
      if (msg.files) {
        actualCount += msg.files.length;
      }
    });

    // Resolve discrepancies
    if (storedCount !== actualCount) {
      console.warn(`File count mismatch: localStorage=${storedCount}, actual=${actualCount}`);
      totalFilesInChat = actualCount;
      localStorage.setItem(CONFIG.FILE_COUNT_KEY, actualCount);
    } else {
      totalFilesInChat = storedCount;
    }

    // Enforce UI state
    elements.attachBtn.disabled = totalFilesInChat >= CONFIG.TOTAL_FILE_LIMIT;
  }

  /** Generate secure session ID */
  function generateSessionId() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    return Array(32).fill(null).map(() => 
      chars.charAt(Math.floor(Math.random() * chars.length))
    ).join('');
  }

  /** Sanitize HTML content */
  function sanitizeHTML(str) {
    if (!str) return '';
    const temp = document.createElement('div');
    temp.textContent = str;
    return temp.innerHTML;
  }

  /** Auto-resize textarea */
  function handleTextareaResize() {
    this.style.height = 'auto';
    const newHeight = Math.min(this.scrollHeight, CONFIG.MAX_TEXTAREA_HEIGHT);
    this.style.height = `${newHeight}px`;
  }

  /** Handle Enter to send */
  function handleKeyPress(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  /** File Attachment */
  function handleFileAttachment() {
    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = CONFIG.ALLOWED_EXTENSIONS.join(",");
    fileInput.multiple = true;
    fileInput.style.display = "none";

    fileInput.onchange = () => {
      const files = Array.from(fileInput.files);
      
      // Calculate available slots correctly
      const currentTotal = totalFilesInChat + attachedFiles.length;
      const availableSlots = Math.max(0, CONFIG.TOTAL_FILE_LIMIT - currentTotal);

      if (availableSlots <= 0) {
        alert(`You've reached the limit of ${CONFIG.TOTAL_FILE_LIMIT} files for this conversation.`);
        return;
      }

      // Process only available slots
      const validFiles = files.slice(0, availableSlots).filter(file => {
        const ext = file.name.split(".").pop().toLowerCase();
        const isValidType = 
          CONFIG.ALLOWED_TYPES.includes(file.type) || 
          CONFIG.ALLOWED_EXTENSIONS.some(ext => 
            file.name.toLowerCase().endsWith(ext)
          );

        if (!isValidType) {
          alert(`"${file.name}" is not allowed. Only PDF, Excel, and TXT files are permitted.`);
          return false;
        }

        if (file.size > CONFIG.MAX_FILE_SIZE) {
          alert(`"${file.name}" exceeds ${CONFIG.MAX_FILE_SIZE/1024/1024}MB limit.`);
          return false;
        }

        return true;
      });

      if (validFiles.length > 0) {
        validFiles.forEach(addAttachedFile);
        
        // Notify about partial attachment
        if (validFiles.length < files.length) {
          alert(`Only ${validFiles.length} file(s) attached (limit: ${CONFIG.TOTAL_FILE_LIMIT}).`);
        }
      }
      
      fileInput.remove();
    };

    document.body.appendChild(fileInput);
    fileInput.click();
  }

  function getFileIcon(fileName) {
    const ext = fileName.split(".").pop().toLowerCase();
    if (ext === "pdf") return "fa-file-pdf";
    if (ext === "txt") return "fa-file-lines";
    if (["xls", "xlsx"].includes(ext)) return "fa-file-excel";
    return "fa-file";
  }

  function addAttachedFile(file) {
    if (attachedFiles.some(f => f.name === file.name && f.size === file.size)) return;

    attachedFiles.push(file);
    const fileIndicator = document.createElement("div");
    fileIndicator.className = "attached-file";
    fileIndicator.file = file;
    
    // Sanitize file name
    const safeName = sanitizeHTML(file.name);
    
    fileIndicator.innerHTML = `
      <i class="fa-solid ${getFileIcon(file.name)}"></i>
      <span class="file-name">${safeName}</span>
      <button class="remove-file" title="Remove file">
        <i class="fa-solid fa-xmark"></i>
      </button>
    `;
    
    fileIndicator.querySelector(".remove-file").onclick = () => 
      removeAttachedFile(fileIndicator);
      
    elements.rightActions.insertBefore(
      fileIndicator,
      elements.rightActions.firstChild
    );
  }

  function removeAttachedFile(fileElement) {
    attachedFiles = attachedFiles.filter(f => f !== fileElement.file);
    fileElement.remove();
  }

  /** Send Message */
  function sendMessage() {
    const message = elements.userInput.value.trim();
    if (isBotTyping || (!message && attachedFiles.length === 0)) return;

    disableUserInput(true);
    isBotTyping = true;

    // Generate session ID BEFORE sending
    let sessionId = localStorage.getItem(CONFIG.SESSION_KEY);
    if (!sessionId) {
      sessionId = generateSessionId();
      localStorage.setItem(CONFIG.SESSION_KEY, sessionId);
    }

    // Add the user message with RAW TEXT (not HTML)
    addMessage(message, true, null, false, attachedFiles.slice());

    // Prepare request
    const formData = new FormData();
    formData.append("message", message);
    formData.append("session_id", sessionId);
    attachedFiles.forEach(file => formData.append("files", file));

    // Reset UI
    elements.userInput.value = "";
    elements.userInput.style.height = "auto";
    clearAttachedFiles();
    
    // Remove existing typing indicator
    if (typingIndicator) {
      typingIndicator.remove();
      typingIndicator = null;
    }
    
    // Show new typing indicator
    typingIndicator = showTypingIndicator();

    fetch("/api/chat", {
      method: "POST",
      body: formData,
    })
    .then(response => {
      if (!response.ok) {
        return response.json().then(err => {
          // More detailed error handling
          let errorMessage = "Request failed";
          if (err.detail) {
            errorMessage = err.detail;
          } else if (err.error) {
            errorMessage = err.error;
          }
          throw new Error(errorMessage);
        }).catch(() => {
          // Handle case where response isn't JSON
          throw new Error(`Server error: ${response.status} ${response.statusText}`);
        });
      }
      return response.json();
    })
    .then(data => {
      // Critical: Parse file count as integer
      totalFilesInChat = parseInt(data.file_count, 10);
      localStorage.setItem(CONFIG.FILE_COUNT_KEY, totalFilesInChat);
      
      // Update UI
      if (typingIndicator) {
        typingIndicator.remove();
        typingIndicator = null;
      }
      
      // Add bot response with RAW TEXT (not HTML)
      addMessage(data.response, false);
      
      elements.attachBtn.disabled = totalFilesInChat >= CONFIG.TOTAL_FILE_LIMIT;
      
      disableUserInput(false);
      isBotTyping = false;
    })
    .catch(error => {
      console.error("Chat error:", error);
      if (typingIndicator) {
        typingIndicator.remove();
        typingIndicator = null;
      }
      
      // Show sanitized error with more detail
      let errorMessage = error.message;
      
      // Special handling for common errors
      if (error.message.includes("pattern")) {
        errorMessage = "Server communication error. Please try again.";
      }
      
      addMessage(`⚠️ ${sanitizeHTML(errorMessage)}`, false);
      
      disableUserInput(false);
      isBotTyping = false;
    });
  }

  function clearAttachedFiles() {
    attachedFiles = [];
    document.querySelectorAll(".attached-file:not(.message-file)").forEach(el => el.remove());
  }

  /** Add message with proper sanitization */
  function addMessage(content, isUser, timestamp = null, skipSave = false, files = []) {
    timestamp = timestamp || new Date().toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
    
    // Build HTML content from RAW TEXT (this is where HTML structure is created)
    let htmlContent = '';
    
    // Add file attachments
    if (files && files.length > 0) {
      files.forEach(file => {
        const safeName = sanitizeHTML(file.name);
        htmlContent += `
          <div class="attached-file message-file">
            <i class="fa-solid ${getFileIcon(file.name)}"></i>
            <span class="file-name">${safeName}</span>
          </div>
        `;
      });
    }
    
    // Add text message (SANITIZE ONLY THE RAW TEXT)
    if (content) {
      htmlContent += `<div class="message-text">${renderMarkdown(sanitizeHTML(content))}</div>`;
    }

    const messageHTML = document.createElement("div");
    messageHTML.className = `message ${isUser ? "user-message" : "bot-message"}`;
    messageHTML.innerHTML = `
      <div class="message-content">${htmlContent}</div>
      <div class="message-timestamp">${sanitizeHTML(timestamp)}</div>
    `;

    elements.chatMessages.appendChild(messageHTML);

    // Maintain message limit
    while (elements.chatMessages.children.length > CONFIG.MAX_MESSAGES) {
      elements.chatMessages.firstChild.remove();
    }

    scrollToBottom();
    if (!skipSave) saveMessageToHistory(content, isUser, timestamp, files);
  }

  /** Scroll helper */
  function scrollToBottom() {
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
  }

  /** Typing indicator */
  function showTypingIndicator() {
    const typingHTML = document.createElement("div");
    typingHTML.className = "typing-indicator";
    typingHTML.innerHTML = `<i class="fa-solid fa-coin-front"></i><span class="text">Thinking...</span>`;
    elements.chatMessages.appendChild(typingHTML);
    scrollToBottom();
    return typingHTML;
  }

  /** Enhanced Markdown parser with sanitization */
  function renderMarkdown(text) {
    if (!text) return "";

    // Special tool call formatting
    text = text
      .replace(/Action: ([^\n]+)/g, '<span class="tool-call">🛠️ <b>Action:</b> $1</span>')
      .replace(/Action Input: ([^\n]+)/g, '<span class="tool-input">🔤 <b>Action Input:</b> $1</span>')
      .replace(/Observation: ([^\n]+)/g, '<span class="tool-result">🔍 <b>Observation:</b> $1</span>')
      .replace(/Final Answer:/g, '<span class="final-answer">✅ <b>Final Answer:</b></span>');

    // Basic markdown
    return text
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>")
      .replace(/\*([^*]+)\*/g, "<i>$1</i>")
      .replace(/\n/g, "<br>")
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, 
        (match, p1, p2) => `<a href="${sanitizeHTML(p2)}" target="_blank" rel="noopener">${sanitizeHTML(p1)}</a>`);
  }
  
  /** History handling */
  function loadChatHistory() {
    const history = JSON.parse(localStorage.getItem(CONFIG.HISTORY_KEY) || "[]");
    history.forEach(msg => 
      addMessage(msg.content, msg.isUser, msg.timestamp, true, msg.files || [])
    );
  }
  
  function saveMessageToHistory(content, isUser, timestamp, files) {
    const history = JSON.parse(localStorage.getItem(CONFIG.HISTORY_KEY) || "[]");
    history.push({ 
      content, 
      isUser, 
      timestamp, 
      files: files.map(file => ({
        name: file.name,
        size: file.size
      })) 
    });
    localStorage.setItem(CONFIG.HISTORY_KEY, JSON.stringify(history));
  }
  
  function clearChatHistory() {
    localStorage.removeItem(CONFIG.HISTORY_KEY);
    localStorage.setItem(CONFIG.FILE_COUNT_KEY, "0");
  }

  /** Enable/Disable input */
  function disableUserInput(disabled) {
    elements.userInput.disabled = disabled;
    elements.sendBtn.disabled = disabled;
    elements.attachBtn.disabled = disabled || totalFilesInChat >= CONFIG.TOTAL_FILE_LIMIT;
    elements.messageInputContainer.classList.toggle("disabled", disabled);
  }

  /** Event Listeners */
  elements.userInput.addEventListener("input", handleTextareaResize);
  elements.userInput.addEventListener("keydown", handleKeyPress);
  elements.sendBtn.addEventListener("click", sendMessage);
  elements.attachBtn.addEventListener("click", handleFileAttachment);
  elements.modelSelect.addEventListener("change", e => 
    console.log(`Switched to model: ${e.target.value}`)
  );

  // CLEAR CHAT BUTTON - FIXED IMPLEMENTATION
  elements.clearChatBtn.addEventListener("click", () => {
    if (!confirm("Clear all chat history?")) return;
    
    const sessionId = localStorage.getItem(CONFIG.SESSION_KEY);
    
    // Clear server session first
    if (sessionId) {
      fetch("/api/clear", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `session_id=${encodeURIComponent(sessionId)}`
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`Server error: ${response.status} ${response.statusText}`);
        }
        return response.json();
      })
      .then(() => {
        // Only clear client state after server success
        performLocalClear();
      })
      .catch(error => {
        console.error("Clear error:", error);
        // Still clear locally even if server fails
        performLocalClear();
        alert(`Chat cleared locally. Server cleanup may be delayed: ${error.message}`);
      });
    } else {
      performLocalClear();
    }
  });

  function performLocalClear() {
    clearChatHistory();
    elements.chatMessages.innerHTML = "";
    totalFilesInChat = 0;
    elements.attachBtn.disabled = false;
    localStorage.removeItem(CONFIG.SESSION_KEY);
    
    // Show welcome message
    addMessage(CONFIG.WELCOME_MESSAGE, false);
  }

  elements.downloadChatBtn.addEventListener("click", () => {
    const history = JSON.parse(localStorage.getItem(CONFIG.HISTORY_KEY) || "[]");
    const text = history
      .map(msg => 
        (msg.isUser ? "You: " : "Fenny: ") + 
        msg.content.replace(/<[^>]+>/g, "")
      )
      .join("\n\n");
      
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `fenny_chat_${new Date().toISOString().slice(0,10)}.txt`;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 100);
  });

  /** Init */
  initializeFileCounter();
  loadChatHistory();
  
  // Add welcome message if new chat
  if (elements.chatMessages.children.length === 0) {
    addMessage(CONFIG.WELCOME_MESSAGE, false);
  }
});