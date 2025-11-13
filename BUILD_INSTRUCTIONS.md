# 🏗️ Windows Build Instructions

This document provides step-by-step instructions for building the **Multi-Stream RTMP to RTSP Converter** as a standalone Windows executable.

---

## ⚙️ Prerequisites

Before you begin, ensure you have the following installed:

- 🪟 **Windows 10 / 11**
- 🐍 **Python 3.11+** (from [python.org](https://www.python.org/downloads/))
- 🎞️ **FFmpeg static build** for Windows
- 📡 **MediaMTX RTSP server** for Windows

---

## 📥 Step 1: Download FFmpeg

1. Go to [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)  
2. Download the **`ffmpeg-release-essentials.zip`** version  
3. Extract the ZIP file  
4. Create a folder named `ffmpeg` in your project root directory  
5. Copy **`ffmpeg.exe`** from the extracted `bin` folder into your project’s `ffmpeg/` folder  

---

## 📥 Step 2: Download MediaMTX

1. Visit [https://github.com/bluenviron/mediamtx/releases](https://github.com/bluenviron/mediamtx/releases)  
2. Download the latest **`mediamtx_vX.X.X_windows_amd64.zip`** release  
3. Extract the ZIP file  
4. Create a folder named `mediamtx` in your project root directory  
5. Copy **`mediamtx.exe`** into your project’s `mediamtx/` folder  

Your project structure should now look like this:

```
project/
├── app.py
├── static/
├── templates/
├── ffmpeg/
│   └── ffmpeg.exe
├── mediamtx/
│   └── mediamtx.exe
├── build_windows.spec
└── ...
```

---

## 📦 Step 3: Install Python Dependencies

Open **Command Prompt** or **PowerShell** in your project directory and run:

```bash
pip install -r requirements.txt
```

If you don’t have a `requirements.txt` file, install dependencies manually:

```bash
pip install flask flask-socketio psutil pyinstaller
```

---

## 🏗️ Step 4: Build the Executable

Run **PyInstaller** with the provided spec file:

```bash
pyinstaller build_windows.spec
```

This will:

- Create a temporary `build/` folder  
- Create a final distribution folder:  
  `dist/RTMP_to_RTSP_Converter/` containing your executable  

---

## 🧩 Step 5: Add FFmpeg and MediaMTX to Distribution

After the build completes:

1. Inside `dist/RTMP_to_RTSP_Converter/`, create:
   - a `ffmpeg/` folder  
   - a `mediamtx/` folder  
2. Copy `ffmpeg.exe` into `dist/RTMP_to_RTSP_Converter/ffmpeg/`  
3. Copy `mediamtx.exe` into `dist/RTMP_to_RTSP_Converter/mediamtx/`  

Final structure:

```
dist/RTMP_to_RTSP_Converter/
├── RTMP_to_RTSP_Converter.exe
├── ffmpeg/
│   └── ffmpeg.exe
├── mediamtx/
│   └── mediamtx.exe
└── [other PyInstaller files]
```

---

## 🧪 Step 6: Test the Application

1. Navigate to `dist/RTMP_to_RTSP_Converter/`  
2. Double-click **`RTMP_to_RTSP_Converter.exe`**

The application should:

- ✅ Start the **MediaMTX RTSP server** automatically  
- 🌐 Open your default browser to [http://localhost:5000](http://localhost:5000)  
- ⚙️ Register itself for **Windows startup** (on first run)  

---

## 📦 Step 7: Distribution

You can now distribute the application by sharing the entire folder:

- Zip the `dist/RTMP_to_RTSP_Converter/` directory  
- Move or copy it to any Windows machine  
- The app can be run from any location  

> ⚠️ **Important:** Users must keep all files together —  
> the `.exe` depends on its `ffmpeg` and `mediamtx` subfolders to function correctly.

---

## ⚡ Advanced: Single-File Executable (Optional)

If you prefer a **single `.exe` file** (simpler to distribute, but slower to start):

1. Open `build_windows.spec`  
2. Locate the line:
   ```python
   exe = EXE(...)
   ```
3. Set:
   ```python
   onefile=True
   ```
   instead of `exclude_binaries=True`  
4. Remove the **COLLECT** section  
5. Rebuild:
   ```bash
   pyinstaller build_windows.spec
   ```

> 🕐 Note: Single-file mode extracts temporary files on each run, so startup is slower.

---

## 🛠️ Troubleshooting

### ❌ “FFmpeg not found”
- Ensure `ffmpeg.exe` is inside the `ffmpeg/` subfolder  
- Check your folder structure matches the expected layout  

---

### ❌ “MediaMTX not found” or “RTSP server failed to start”
- Ensure `mediamtx.exe` is inside the `mediamtx/` subfolder  
- Verify port **8554** is not already in use  
- **MediaMTX** is required — streams will fail without it  

---

### ⚠️ Application won’t start
- Run from Command Prompt to view errors:
  ```bash
  RTMP_to_RTSP_Converter.exe
  ```
- Ensure Windows Defender or antivirus isn’t blocking the app  

---

### 🔒 Port 5000 already in use
- Close any other app using port **5000**  
- Or modify the port in `app.py` before building  

---

### 🪟 Windows startup not working
- Ensure you’re running the **.exe**, not the Python script  
- Check registry key:
  ```
  HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
  ```
- On some systems, administrator privileges may be required  

---

### 🧹 Uninstalling Windows Startup

To remove the application from startup:

**Option 1:**  
Press **Win + R**, type `shell:startup`, and delete the shortcut  

**Option 2:**  
Open **Task Manager → Startup tab**, and disable the app  

**Option 3:**  
Manually remove from:
```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
```

---

## 📝 Notes

- The **web interface** uses port `5000`  
- The **RTSP server** uses port `8554` by default  
- Each stream runs as a **separate FFmpeg process**  
- Stopping the application terminates all active FFmpeg streams  

---

✅ **Build complete!**  
You now have a portable, self-contained Windows executable for converting **RTMP → RTSP** streams in real time.
