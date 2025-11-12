const socket = io();

const rtmpInput = document.getElementById("rtmpInput");
const startBtn = document.getElementById("startBtn");
const stopAllBtn = document.getElementById("stopAllBtn");
const streamsContainer = document.getElementById("streamsContainer");
const logConsole = document.getElementById("logConsole");
const clearLogsBtn = document.getElementById("clearLogsBtn");
const serverWarning = document.getElementById("serverWarning");

let streams = {};
let rtspServerRunning = false;

function formatTime() {
  const now = new Date();
  return now.toLocaleTimeString();
}

function addLog(message, type = "info") {
  const logEntry = document.createElement("div");
  logEntry.className = `log-entry ${type}`;

  const timeSpan = document.createElement("span");
  timeSpan.className = "log-time";
  timeSpan.textContent = `[${formatTime()}]`;

  const messageSpan = document.createElement("span");
  messageSpan.className = "log-message";
  messageSpan.textContent = message;

  logEntry.appendChild(timeSpan);
  logEntry.appendChild(messageSpan);

  logConsole.appendChild(logEntry);
  logConsole.scrollTop = logConsole.scrollHeight;
}

function copyToClipboard(text) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard
      .writeText(text)
      .then(() => {
        addLog(`Copied to clipboard: ${text}`, "success");
      })
      .catch((err) => {
        fallbackCopyToClipboard(text);
      });
  } else {
    fallbackCopyToClipboard(text);
  }
}

function fallbackCopyToClipboard(text) {
  const textArea = document.createElement("textarea");
  textArea.value = text;
  textArea.style.position = "fixed";
  textArea.style.left = "-999999px";
  document.body.appendChild(textArea);
  textArea.select();

  try {
    document.execCommand("copy");
    addLog(`Copied to clipboard: ${text}`, "success");
  } catch (err) {
    addLog("Failed to copy to clipboard", "error");
  }

  document.body.removeChild(textArea);
}

function getStatusIcon(status) {
  switch (status) {
    case "active":
      return "🟢";
    case "starting":
      return "🟡";
    case "stopped":
      return "🔴";
    default:
      return "⚪";
  }
}

function createStreamElement(stream) {
  const streamDiv = document.createElement("div");
  streamDiv.className = "stream-item";
  streamDiv.id = `stream-${stream.id}`;

  const statusClass = stream.status || "stopped";

  streamDiv.innerHTML = `
        <div class="stream-header">
            <div class="stream-status ${statusClass}">
                <span class="status-indicator">${getStatusIcon(
                  stream.status
                )}</span>
                <span>${stream.status.toUpperCase()}</span>
            </div>
            <div class="stream-actions">
                <button class="btn btn-sm btn-outline-secondary btn-icon copy-btn" data-url="${
                  stream.rtsp_url
                }">
                    <i class="fas fa-copy"></i> Copy Link
                </button>
                <button class="btn btn-sm btn-danger btn-icon stop-btn" data-id="${
                  stream.id
                }">
                    <i class="fas fa-stop"></i> Stop
                </button>
            </div>
        </div>
        <div class="stream-info">
            <div class="stream-label">RTMP Source</div>
            <div class="stream-value">${stream.rtmp_url}</div>
        </div>
        <div class="stream-info">
            <div class="stream-label">RTSP Output</div>
            <div class="stream-value">${stream.rtsp_url}</div>
        </div>
        ${
          stream.error
            ? `<div class="stream-error"><i class="fas fa-exclamation-triangle"></i> ${stream.error}</div>`
            : ""
        }
    `;

  const copyBtn = streamDiv.querySelector(".copy-btn");
  copyBtn.addEventListener("click", () => {
    copyToClipboard(stream.rtsp_url);
  });

  const stopBtn = streamDiv.querySelector(".stop-btn");
  stopBtn.addEventListener("click", () => {
    stopStream(stream.id);
  });

  return streamDiv;
}

function updateStreamElement(streamId, updates) {
  const streamDiv = document.getElementById(`stream-${streamId}`);
  if (!streamDiv) return;

  if (updates.status) {
    const statusDiv = streamDiv.querySelector(".stream-status");
    statusDiv.className = `stream-status ${updates.status}`;
    statusDiv.innerHTML = `
            <span class="status-indicator">${getStatusIcon(
              updates.status
            )}</span>
            <span>${updates.status.toUpperCase()}</span>
        `;
  }

  if (updates.error) {
    let errorDiv = streamDiv.querySelector(".stream-error");
    if (!errorDiv) {
      errorDiv = document.createElement("div");
      errorDiv.className = "stream-error";
      streamDiv.appendChild(errorDiv);
    }
    errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${updates.error}`;
  } else {
    const errorDiv = streamDiv.querySelector(".stream-error");
    if (errorDiv) {
      errorDiv.remove();
    }
  }
}

function renderStreams() {
  const streamsList = Object.values(streams);

  if (streamsList.length === 0) {
    streamsContainer.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-info-circle"></i>
                <p>No active streams. Start conversion to see streams here.</p>
            </div>
        `;
    return;
  }

  streamsContainer.innerHTML = "";
  streamsList.forEach((stream) => {
    streamsContainer.appendChild(createStreamElement(stream));
  });
}

function startStreams() {
  const rtmpUrls = rtmpInput.value
    .split("\n")
    .map((url) => url.trim())
    .filter((url) => url.length > 0);

  if (rtmpUrls.length === 0) {
    addLog("No RTMP URLs provided", "error");
    return;
  }

  startBtn.disabled = true;
  startBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Starting...';

  fetch("/api/start", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ rtmp_urls: rtmpUrls }),
  })
    .then((response) => response.json())
    .then((data) => {
      startBtn.disabled = false;
      startBtn.innerHTML =
        '<i class="fas fa-play"></i> Start Conversion & Serve';

      if (data.streams) {
        addLog(`Started ${data.streams.length} stream(s)`, "success");
      }
    })
    .catch((error) => {
      addLog(`Error starting streams: ${error.message}`, "error");
      startBtn.disabled = false;
      startBtn.innerHTML =
        '<i class="fas fa-play"></i> Start Conversion & Serve';
    });
}

function stopStream(streamId) {
  fetch(`/api/stop/${streamId}`, {
    method: "POST",
  })
    .then((response) => response.json())
    .then((data) => {
      addLog(`Stream ${streamId} stopped`, "info");
    })
    .catch((error) => {
      addLog(`Error stopping stream: ${error.message}`, "error");
    });
}

function stopAllStreams() {
  if (Object.keys(streams).length === 0) {
    addLog("No active streams to stop", "info");
    return;
  }

  stopAllBtn.disabled = true;
  stopAllBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Stopping...';

  fetch("/api/stop_all", {
    method: "POST",
  })
    .then((response) => response.json())
    .then((data) => {
      addLog("All streams stopped", "info");
      stopAllBtn.disabled = false;
      stopAllBtn.innerHTML = '<i class="fas fa-stop"></i> Stop All';
    })
    .catch((error) => {
      addLog(`Error stopping streams: ${error.message}`, "error");
      stopAllBtn.disabled = false;
      stopAllBtn.innerHTML = '<i class="fas fa-stop"></i> Stop All';
    });
}

function checkServerStatus() {
  fetch("/api/status")
    .then((response) => response.json())
    .then((data) => {
      const wasRunning = rtspServerRunning;
      rtspServerRunning = data.rtsp_server_running;

      if (!rtspServerRunning) {
        serverWarning.style.display = "block";
        startBtn.disabled = true;
        startBtn.title = "RTSP server is not running";
      } else {
        serverWarning.style.display = "none";
        startBtn.disabled = false;
        startBtn.title = "";

        if (!wasRunning && rtspServerRunning) {
          addLog("RTSP server is now available and ready", "success");
        }
      }
    })
    .catch((error) => {
      console.error("Error checking server status:", error);
    });
}

function loadStreams() {
  fetch("/api/streams")
    .then((response) => response.json())
    .then((data) => {
      data.forEach((stream) => {
        streams[stream.id] = stream;
      });
      renderStreams();
    })
    .catch((error) => {
      addLog(`Error loading streams: ${error.message}`, "error");
    });
}

startBtn.addEventListener("click", startStreams);
stopAllBtn.addEventListener("click", stopAllStreams);
clearLogsBtn.addEventListener("click", () => {
  logConsole.innerHTML = "";
  addLog("Logs cleared", "info");
});

socket.on("connect", () => {
  addLog("Connected to server", "info");
});

socket.on("disconnect", () => {
  addLog("Disconnected from server", "error");
});

socket.on("log", (data) => {
  addLog(data.message, data.type);
});

socket.on("stream_update", (data) => {
  if (data.stream_id) {
    if (streams[data.stream_id]) {
      streams[data.stream_id].status = data.status;
      if (data.error !== undefined) {
        streams[data.stream_id].error = data.error;
      }
      updateStreamElement(data.stream_id, data);
    } else {
      streams[data.stream_id] = {
        id: data.stream_id,
        rtmp_url: data.rtmp_url,
        rtsp_url: data.rtsp_url,
        status: data.status,
        error: data.error || "",
      };
      renderStreams();
    }
  }
});

checkServerStatus();
loadStreams();

setInterval(checkServerStatus, 10000);
