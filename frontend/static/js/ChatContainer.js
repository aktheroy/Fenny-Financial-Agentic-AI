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

  const MAX_MESSAGES = 100;
  const MAX_FILE_SIZE = 5 * 1024 * 1024;
  const TOTAL_FILE_LIMIT = 2; // GLOBAL conversation limit (not per message)
  const MAX_TEXTAREA_HEIGHT = 150;
  const ALLOWED_TYPES = [
    "application/pdf",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/plain",
  ];
  const ALLOWED_EXTENSIONS = [".pdf", ".xls", ".xlsx", ".txt"];

  let attachedFiles = [];
  let isBotTyping = false;
  let totalFilesInChat = 0; // Tracks ALL files in current conversation

  const responses = [
    "I've analyzed your financial query and here's my assessment...",
    "Based on current market data, I recommend considering...",
    "From an investment perspective, this looks interesting...",
    "Here's my analysis of your question with key insights...",
    "Let me break down the financial implications for you...",
    "According to recent market trends, you should know...",
  ];

  /** Initialize file counter from history or localStorage */
  function initializeFileCounter() {
    // Check if we need to recalculate (upgrade from old version)
    if (localStorage.getItem("fenny_total_file_count") === null) {
      const history = JSON.parse(
        localStorage.getItem("fenny_chat_history") || "[]"
      );
      let count = 0;
      history.forEach((msg) => {
        const tempDiv = document.createElement("div");
        tempDiv.innerHTML = msg.content;
        count += tempDiv.querySelectorAll(".attached-file.message-file").length;
      });
      totalFilesInChat = count;
      localStorage.setItem("fenny_total_file_count", count);
    } else {
      totalFilesInChat =
        parseInt(localStorage.getItem("fenny_total_file_count")) || 0;
    }

    // Update UI based on file count
    if (totalFilesInChat >= TOTAL_FILE_LIMIT) {
      elements.attachBtn.disabled = true;
    }
  }

  /** Utility: debounce */
  const debounce = (fn, delay) => {
    let timer;
    return (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), delay);
    };
  };

  /** Auto-resize textarea */
  function handleTextareaResize() {
    this.style.height = "auto";
    const newHeight = Math.min(this.scrollHeight, MAX_TEXTAREA_HEIGHT);
    if (this.style.height !== `${newHeight}px`) {
      this.style.height = `${newHeight}px`;
    }
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
    fileInput.accept = ALLOWED_EXTENSIONS.join(",");
    fileInput.multiple = true;
    fileInput.style.display = "none";

    fileInput.onchange = () => {
      const files = Array.from(fileInput.files);

      // Calculate available slots in ENTIRE conversation
      const currentTotal = totalFilesInChat + attachedFiles.length;
      const availableSlots = TOTAL_FILE_LIMIT - currentTotal;

      if (availableSlots <= 0) {
        alert(
          `You can only attach up to ${TOTAL_FILE_LIMIT} files in the entire conversation.`
        );
        return;
      }

      const validFiles = files.slice(0, availableSlots).filter((file) => {
        const ext = file.name.split(".").pop().toLowerCase();
        const isValidType =
          ALLOWED_TYPES.includes(file.type) ||
          ALLOWED_EXTENSIONS.some((ext) =>
            file.name.toLowerCase().endsWith(ext)
          );

        if (!isValidType) {
          alert(
            `"${file.name}" is not allowed. Only PDF, Excel, and TXT files are permitted.`
          );
          return false;
        }

        if (file.size > MAX_FILE_SIZE) {
          alert(`"${file.name}" exceeds 5MB limit.`);
          return false;
        }

        return true;
      });

      if (validFiles.length > 0) {
        validFiles.forEach(addAttachedFile);
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
    if (attachedFiles.some((f) => f.name === file.name)) return;

    attachedFiles.push(file);
    const fileIndicator = document.createElement("div");
    fileIndicator.className = "attached-file";
    fileIndicator.file = file;
    fileIndicator.innerHTML = `
      <i class="fa-solid ${getFileIcon(file.name)}"></i>
      <span class="file-name">${file.name}</span>
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
    attachedFiles = attachedFiles.filter((f) => f !== fileElement.file);
    fileElement.remove();
  }

  /** Send Message */
  function sendMessage() {
    if (isBotTyping) return;

    const message = elements.userInput.value.trim();
    if (!message && attachedFiles.length === 0) return;

    disableUserInput(true);

    // Add user message to chat (including files)
    let messageContent = "";
    attachedFiles.forEach((file) => {
      messageContent += `
        <div class="attached-file message-file">
          <i class="fa-solid ${getFileIcon(file.name)}"></i>
          <span class="file-name">${file.name}</span>
        </div>
      `;
    });

    if (message) {
      messageContent += `<div class="message-text">${message}</div>`;
    }
    addMessage(messageContent, true);

    // Prepare form data for API request
    const formData = new FormData();
    formData.append("message", message);

    // Add session ID
    let sessionId = localStorage.getItem("fenny_session_id");
    if (!sessionId) {
      sessionId = crypto.randomUUID();
      localStorage.setItem("fenny_session_id", sessionId);
    }
    formData.append("session_id", sessionId);

    // Add files
    attachedFiles.forEach((file) => {
      formData.append("files", file);
    });

    // Clear UI
    elements.userInput.value = "";
    elements.userInput.style.height = "auto";
    clearAttachedFiles();

    // Show typing indicator
    const typingIndicator = showTypingIndicator();

    // SEND TO BACKEND WITH API PREFIX - THIS IS THE KEY CHANGE
    fetch("/api/chat", {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        if (!response.ok) {
          return response.json().then((err) => {
            throw new Error(err.detail || "Request failed");
          });
        }
        return response.json();
      })
      .then((data) => {
        // Remove typing indicator
        typingIndicator.remove();

        // Update file counter
        totalFilesInChat = data.file_count;
        localStorage.setItem("fenny_total_file_count", totalFilesInChat);

        // Add bot response
        addMessage(data.response, false);

        // Update UI based on file count
        if (totalFilesInChat >= TOTAL_FILE_LIMIT) {
          elements.attachBtn.disabled = true;
        }

        // Re-enable input
        disableUserInput(false);
        isBotTyping = false;
      })
      .catch((error) => {
        console.error("Error:", error);
        typingIndicator.remove();
        addMessage(`Error: ${error.message}`, false);
        disableUserInput(false);
        isBotTyping = false;
      });
  }

  function clearAttachedFiles() {
    attachedFiles = [];
    document
      .querySelectorAll(".attached-file:not(.message-file)")
      .forEach((el) => el.remove());
  }

  /** Add message */
  function addMessage(content, isUser, timestamp = null, skipSave = false) {
    timestamp =
      timestamp ||
      new Date().toLocaleTimeString("en-US", {
        hour12: false,
        hour: "2-digit",
        minute: "2-digit",
      });
    const htmlContent = renderMarkdown(content);

    const messageHTML = document.createElement("div");
    messageHTML.className = `message ${
      isUser ? "user-message" : "bot-message"
    }`;
    messageHTML.innerHTML = `
      <div class="message-content">${htmlContent}</div>
      <div class="message-timestamp">${timestamp}</div>
    `;

    elements.chatMessages.appendChild(messageHTML);

    if (elements.chatMessages.children.length > MAX_MESSAGES) {
      elements.chatMessages.firstChild.remove();
    }

    scrollToBottom();

    if (!skipSave) saveMessageToHistory(content, isUser, timestamp);
  }

  /** Scroll helper */
  function scrollToBottom() {
    requestAnimationFrame(() => {
      elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    });
  }

  /** Typing indicator */
  function showTypingIndicator() {
    const typingHTML = document.createElement("div");
    typingHTML.className = "typing-indicator";
    typingHTML.innerHTML = `<i class="fa-solid fa-coin-front"></i><span class="text">Thinking  </span>`;
    elements.chatMessages.appendChild(typingHTML);
    scrollToBottom();
    return typingHTML;
  }

  /** Enhanced Markdown parser */
  function renderMarkdown(text) {
    if (!text) return "";

    // Handle tool call indicators
    text = text
      .replace(
        /Action: ([^\n]+)/g,
        '<span class="tool-call">🛠️ Action: $1</span>'
      )
      .replace(
        /Action Input: ([^\n]+)/g,
        '<span class="tool-input">🔤 Action Input: $1</span>'
      )
      .replace(
        /Observation: ([^\n]+)/g,
        '<span class="tool-result">🔍 Observation: $1</span>'
      )
      .replace(
        /Final Answer:/g,
        '<span class="final-answer">✅ Final Answer:</span>'
      );

    // Standard markdown
    return text
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>")
      .replace(/\*([^*]+)\*/g, "<i>$1</i>")
      .replace(
        /\[([^\]]+)\]\(([^)]+)\)/g,
        '<a href="$2" target="_blank">$1</a>'
      )
      .replace(/\n/g, "<br>");
  }
  /** History handling */
  function loadChatHistory() {
    const history = JSON.parse(
      localStorage.getItem("fenny_chat_history") || "[]"
    );
    history.forEach((msg) =>
      addMessage(msg.content, msg.isUser, msg.timestamp, true)
    );
  }
  function saveMessageToHistory(content, isUser, timestamp) {
    const history = JSON.parse(
      localStorage.getItem("fenny_chat_history") || "[]"
    );
    history.push({ content, isUser, timestamp });
    localStorage.setItem("fenny_chat_history", JSON.stringify(history));
  }
  function clearChatHistory() {
    localStorage.removeItem("fenny_chat_history");
    localStorage.setItem("fenny_total_file_count", "0"); // Reset file counter
  }

  /** Enable/Disable input */
  function disableUserInput(disabled) {
    elements.userInput.disabled = disabled;
    elements.sendBtn.disabled = disabled;
    elements.attachBtn.disabled = disabled;
    elements.messageInputContainer.classList.toggle("disabled", disabled);
  }

  /** Event Listeners */
  elements.userInput.addEventListener(
    "input",
    debounce(handleTextareaResize, 50)
  );
  elements.userInput.addEventListener("keydown", handleKeyPress);
  elements.sendBtn.addEventListener("click", sendMessage);
  elements.attachBtn.addEventListener("click", handleFileAttachment);
  elements.modelSelect.addEventListener("change", (e) =>
    console.log(`Switched to model: ${e.target.value}`)
  );

  // CLEAR CHAT BUTTON - UPDATED WITH API PREFIX
  elements.clearChatBtn.addEventListener("click", () => {
    if (confirm("Clear all chat history?")) {
      // Clear frontend
      clearChatHistory();
      elements.chatMessages.innerHTML = "";
      totalFilesInChat = 0;

      // Clear backend state WITH API PREFIX
      let sessionId = localStorage.getItem("fenny_session_id");
      if (sessionId) {
        fetch("/api/clear", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: `session_id=${sessionId}`,
        })
          .then(() => {
            // Reset UI
            elements.attachBtn.disabled = false;
            localStorage.removeItem("fenny_session_id");
          })
          .catch(console.error);
      } else {
        // Reset UI
        elements.attachBtn.disabled = false;
      }
    }
  });

  elements.downloadChatBtn.addEventListener("click", () => {
    const history = JSON.parse(
      localStorage.getItem("fenny_chat_history") || "[]"
    );
    const text = history
      .map(
        (msg) =>
          (msg.isUser ? "You: " : "Fenny: ") +
          msg.content.replace(/<[^>]+>/g, "")
      )
      .join("\n\n");
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "fenny_chat.txt";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  });

  /** Init */
  initializeFileCounter(); // Initialize file counter FIRST
  loadChatHistory();
});
