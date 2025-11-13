# 🧠 Development Notes

This document provides notes and tips for developers working on the **Multi-Stream RTMP to RTSP Converter**, including environment setup, testing procedures, and mock testing options across different operating systems.

---

## 🧩 Testing in Non-Windows Environments

This application is primarily designed for **Windows** and requires the **MediaMTX RTSP server** to function properly.  
When running in environments like **Replit**, **Linux**, or **macOS**, where MediaMTX may not be available, you may see the following warning:

```
WARNING: RTSP server failed to start. Streams will not work!
Download MediaMTX from: https://github.com/bluenviron/mediamtx/releases
Extract mediamtx.exe to a 'mediamtx' folder next to this application
```

➡️ **This is expected behavior.**  
The app will still launch, and the **web UI will function normally**, but stream conversion will **not** work without MediaMTX.

---

## 🧪 Full Testing Requirements

To fully test the application's **stream conversion functionality**, ensure you have:

### 🪟 On Windows (Recommended)
- **Windows 10/11**
- **MediaMTX RTSP server**
  - Download from [https://github.com/bluenviron/mediamtx/releases](https://github.com/bluenviron/mediamtx/releases)
  - Extract `mediamtx.exe` into a `mediamtx/` folder in your project root
- **FFmpeg** (optional for development)
  - App checks for FFmpeg in system `PATH`
  - Or place `ffmpeg.exe` in a `ffmpeg/` folder next to the app

---

## 🐧 Development on Linux / macOS

While the project targets Windows, development and limited testing can be done on **Linux** or **macOS**.

### Steps:
1. Download the MediaMTX binary for your OS:  
   [https://github.com/bluenviron/mediamtx/releases](https://github.com/bluenviron/mediamtx/releases)
2. Place the binary inside a `mediamtx/` folder (in the project root)
3. Edit the `get_mediamtx_path()` function in `app.py` to use your platform’s filename:
   - On Linux/macOS: remove `.exe` from the path
4. Run the app with `python app.py`
5. Test basic UI and (optionally) stream functionality if FFmpeg and MediaMTX are available

---

## 🧰 UI Testing (No MediaMTX Required)

You can test the **web UI** independently of MediaMTX and FFmpeg:

1. Run:
   ```bash
   python app.py
   ```
2. Visit [http://localhost:5000](http://localhost:5000)
3. Test:
   - RTMP input field
   - “Start Conversion” button
   - Stream monitoring section

> Streams will fail to start (expected) — this mode is perfect for frontend/UI testing.

---

## 🧱 Production Build Testing

To test the **PyInstaller** build and full conversion process:

1. Use a **Windows 10/11** system  
2. Download **MediaMTX** and **FFmpeg**  
3. Follow the build guide in [`BUILD_INSTRUCTIONS.md`](BUILD_INSTRUCTIONS.md)  
4. Test with:
   - Real RTMP feeds (e.g. IP cameras, OBS output)
   - Or generated test streams (see below)

---

## 🧪 Mock Testing Without Real Streams

If you lack real RTMP sources, use FFmpeg to generate a test pattern stream:

### Create a Test RTMP Stream:
```bash
ffmpeg -re -f lavfi -i testsrc=size=1280x720:rate=30 -f lavfi -i sine=frequency=1000 \
 -c:v libx264 -preset ultrafast -c:a aac -f flv rtmp://localhost:1935/live/test
```

> ⚠️ Requires an **RTMP server** such as:
> - [nginx-rtmp-module](https://github.com/arut/nginx-rtmp-module)
> - **MediaMTX** configured for RTMP input  

Alternatively, use **dummy RTMP URLs** (e.g. `rtmp://test/stream`) to test UI responses.  
These will fail gracefully, which is expected in mock tests.

---

## 🧷 Key Points Summary

| Topic | Summary |
|-------|----------|
| **MediaMTX Requirement** | Mandatory for stream conversion |
| **Degraded Mode** | App still runs without MediaMTX (UI only) |
| **Error Handling** | Clear warnings for missing components |
| **Windows Registry** | Used only on Windows; ignored safely on other OS |
| **Web UI** | Fully functional even if backend streaming is unavailable |

---

## 📁 Recommended Development Folder Layout

Below are reference layouts for both **Windows** and **Linux/macOS** development environments.

### 🪟 Windows Layout
```
project_root/
├── app.py
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── app.js
├── ffmpeg/
│   └── ffmpeg.exe
├── mediamtx/
│   └── mediamtx.exe
├── build_windows.spec
├── BUILD_INSTRUCTIONS.md
├── DEVELOPMENT_NOTES.md
└── requirements.txt
```

### 🐧 Linux / macOS Layout
```
project_root/
├── app.py
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── app.js
├── ffmpeg/
│   └── ffmpeg (binary, no .exe)
├── mediamtx/
│   └── mediamtx (binary, no .exe)
├── BUILD_INSTRUCTIONS.md
├── DEVELOPMENT_NOTES.md
└── requirements.txt
```

> 💡 *Tip:* You can make the code automatically detect the OS using Python’s `platform.system()` and adjust paths accordingly in `app.py`.

---

✅ **In summary:**  
You can fully test the UI and application flow on any system,  
but for **real RTMP → RTSP conversion**, you’ll need **MediaMTX** and **FFmpeg** available in your environment.
