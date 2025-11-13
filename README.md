# 🎬 Multi-Stream RTMP to RTSP Converter

A lightweight **Windows application** that converts multiple **RTMP (Real-Time Messaging Protocol)** streams to **RTSP (Real-Time Streaming Protocol)** streams in real-time using **FFmpeg**.

---

## 🚀 Features

- **Multi-Stream Support:** Convert multiple RTMP streams simultaneously  
- **Real-Time Monitoring:** Live status updates for each stream  
- **Modern Web UI:** Clean, dark-themed, responsive interface  
- **Process Management:** Start/stop control per stream  
- **Auto-Startup:** Automatically launches on Windows login  
- **FFmpeg Integration:** Uses FFmpeg for reliable stream conversion  
- **Error Logging:** Built-in console for detailed troubleshooting  

---

## 🖥️ System Requirements

- Windows 10 / 11  
- FFmpeg (bundled with executable)  
- MediaMTX RTSP server (bundled with executable)  
- Network access to RTMP sources  

---

## ⚡ Quick Start

### For End Users (Executable)

1. **Download** the `RTMP_to_RTSP_Converter` folder  
2. Ensure:
   - `ffmpeg.exe` is in the `ffmpeg/` subfolder  
   - `mediamtx.exe` is in the `mediamtx/` subfolder  
3. Run `RTMP_to_RTSP_Converter.exe`  
4. Your browser will automatically open to:  
   👉 [http://localhost:5000](http://localhost:5000)

---

### For Developers (Source Code)

1. Install **Python 3.11+**  
2. Download **MediaMTX** from [bluenviron/mediamtx](https://github.com/bluenviron/mediamtx/releases)  
3. Extract and place `mediamtx.exe` in a `mediamtx/` folder  
4. Install dependencies:
   ```bash
   pip install flask flask-socketio psutil pyinstaller
   ```
5. Run the application:
   ```bash
   python app.py
   ```
6. Open [http://localhost:5000](http://localhost:5000) in your browser  

---

## 🎛️ Usage

### Enter RTMP URLs
In the input area, enter one RTMP URL per line:
```
rtmp://source.example.com/live/stream1
rtmp://source.example.com/live/stream2
```

### Start Conversion
Click **“Start Conversion & Serve”**.

### Monitor Streams
Each active stream appears under **Active RTSP Streams** with:
- 🟢 / 🟡 / 🔴 **Status Indicator**  
- Source **RTMP URL**  
- Output **RTSP URL** (e.g., `rtsp://localhost:8554/stream-id`)  
- **Copy** and **Stop** buttons  

### Use RTSP Streams
RTSP URLs can be opened in:
- **VLC Media Player**
- **OBS Studio**
- **Any RTSP-compatible software**

### Stop Streams
Click **Stop** per stream or **Stop All** to end all sessions.

---

## 🧩 Architecture

### Technology Stack
| Component | Technology |
|------------|-------------|
| Backend | Python + Flask + Flask-SocketIO |
| Frontend | HTML5 + CSS3 + JavaScript + Bootstrap 5 |
| Streaming Engine | FFmpeg |
| RTSP Server | MediaMTX (formerly *rtsp-simple-server*) |
| Process Management | psutil |
| Packaging | PyInstaller |

---

## ⚙️ How It Works

1. The app starts **MediaMTX** RTSP server on port **8554**  
2. User provides RTMP stream URLs  
3. App spawns a separate **FFmpeg** process for each stream  
4. FFmpeg pulls from RTMP and pushes to MediaMTX  
5. MediaMTX serves RTSP streams to clients  
6. WebSocket provides real-time status updates  
7. Process monitoring detects failed streams  

### FFmpeg Command Pattern
```bash
ffmpeg -i rtmp://source/stream -c:v copy -c:a copy -f rtsp rtsp://localhost:8554/stream-id
```

---

## 🔧 Configuration

### Ports
| Service | Default | Configurable In |
|----------|----------|----------------|
| Web Interface | 5000 | `app.py` |
| RTSP Server | 8554 | `app.py` |

### Windows Auto Startup
The app adds itself to:
```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
```

---

## 🏗️ Building from Source

See [`BUILD_INSTRUCTIONS.md`](BUILD_INSTRUCTIONS.md) for details.

**Summary:**
1. Download FFmpeg for Windows  
2. Install Python dependencies  
3. Run:
   ```bash
   pyinstaller build_windows.spec
   ```
4. Copy `ffmpeg.exe` to the distribution folder  
5. Distribute the full folder  

---

## 🩺 Troubleshooting

### FFmpeg Not Found
- Ensure `ffmpeg.exe` is in the `ffmpeg/` folder next to the executable  
- For development, confirm FFmpeg is in your system `PATH`

### MediaMTX Not Found / Streams Won’t Start
- Ensure `mediamtx.exe` is in the `mediamtx/` folder  
- Download from [bluenviron/mediamtx](https://github.com/bluenviron/mediamtx/releases)  
- **MediaMTX** is required — streams won’t start without it  

### Stream Won’t Start
- Verify RTMP URL validity and accessibility  
- Check firewall settings  
- Review the **Error/Log Console** for FFmpeg messages  

### Port Already in Use
- Close apps using ports **5000** or **8554**  
- Or modify ports in `app.py` before building  

### Browser Doesn’t Open
- Manually go to [http://localhost:5000](http://localhost:5000)  
- Check if another service occupies port 5000  

---

## 📁 Project Structure
```
project/
├── app.py                  # Main Flask application
├── templates/
│   └── index.html          # Web UI template
├── static/
│   ├── style.css           # Styling
│   └── app.js              # Frontend logic
├── build_windows.spec      # PyInstaller build config
├── BUILD_INSTRUCTIONS.md   # Build guide
├── README.md               # This file
└── ffmpeg/
    └── ffmpeg.exe          # FFmpeg binary (for distribution)
```

---

## 📜 License
This project is provided **as-is**, for **educational and commercial use**.

---

## 🙌 Acknowledgments

- [FFmpeg](https://ffmpeg.org) — The powerful streaming engine  
- [Flask](https://flask.palletsprojects.com/) + [Socket.IO](https://socket.io) — Web framework and real-time updates  
- [Bootstrap](https://getbootstrap.com) — Frontend UI framework  
- [MediaMTX](https://github.com/bluenviron/mediamtx) — RTSP server backend  

---
