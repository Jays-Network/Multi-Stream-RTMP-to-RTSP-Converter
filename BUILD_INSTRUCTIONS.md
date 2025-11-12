Windows Build Instructions
This document provides step-by-step instructions for building the RTMP to RTSP Converter as a standalone Windows executable.

Prerequisites
Before building, you need:

Windows 10/11 machine
Python 3.11 installed from python.org
FFmpeg static build for Windows
MediaMTX RTSP server for Windows
Step 1: Download FFmpeg
Download FFmpeg static build for Windows from: https://www.gyan.dev/ffmpeg/builds/
Choose the "ffmpeg-release-essentials.zip" version
Extract the ZIP file
Create a folder named ffmpeg in your project root directory
Copy ffmpeg.exe from the extracted bin folder to your project's ffmpeg folder
Step 2: Download MediaMTX
Download MediaMTX for Windows from: https://github.com/bluenviron/mediamtx/releases
Download mediamtx_vX.X.X_windows_amd64.zip (latest version)
Extract the ZIP file
Create a folder named mediamtx in your project root directory
Copy mediamtx.exe from the extracted folder to your project's mediamtx folder
Your project structure should now include:

project/
├── app.py
├── static/
├── templates/
├── ffmpeg/
│ └── ffmpeg.exe
├── mediamtx/
│ └── mediamtx.exe
├── build_windows.spec
└── ...

Step 3: Install Python Dependencies
Open Command Prompt or PowerShell in your project directory and run:

pip install -r requirements.txt

If you don't have a requirements.txt, install manually:

pip install flask flask-socketio psutil pyinstaller

Step 4: Build the Executable
Run PyInstaller with the provided spec file:

pyinstaller build_windows.spec

This process will:

Create a build/ folder (temporary build files)
Create a dist/RTMP_to_RTSP_Converter/ folder with your executable
Step 5: Add FFmpeg and MediaMTX to Distribution
After PyInstaller finishes:

Create a ffmpeg folder inside dist/RTMP_to_RTSP_Converter/
Copy your ffmpeg.exe into this new folder
Create a mediamtx folder inside dist/RTMP_to_RTSP_Converter/
Copy your mediamtx.exe into this new folder
Final structure:

dist/RTMP_to_RTSP_Converter/
├── RTMP_to_RTSP_Converter.exe
├── ffmpeg/
│ └── ffmpeg.exe
├── mediamtx/
│ └── mediamtx.exe
└── [other PyInstaller files]

Step 6: Test the Application
Navigate to dist/RTMP_to_RTSP_Converter/
Double-click RTMP_to_RTSP_Converter.exe
The application should:
Start the MediaMTX RTSP server automatically
Open your default web browser to http://127.0.0.1:5000
Register itself for Windows startup (when run for the first time)
Step 7: Distribution
The entire dist/RTMP_to_RTSP_Converter/ folder can be:

Zipped and distributed
Moved to any Windows machine
Installed anywhere on the user's system
IMPORTANT: Users MUST keep all files in the folder together. The .exe needs the supporting files to run.

Advanced: Creating a Single-File Executable
If you prefer a single .exe file (larger file, but simpler):

Modify build_windows.spec:

Change exe = EXE(...) section
Set onefile=True instead of exclude_binaries=True
Remove the COLLECT section
Rebuild with pyinstaller build_windows.spec

Note: Single-file mode will be slower to start as it extracts files on each run.

Troubleshooting
"FFmpeg not found" Error
Ensure ffmpeg.exe is in the ffmpeg/ subfolder next to the executable
Check the FFmpeg path in the code matches your structure
"MediaMTX not found" or "RTSP server failed to start" Error
Ensure mediamtx.exe is in the mediamtx/ subfolder next to the executable
Check that port 8554 is not already in use by another application
MediaMTX is required for the application to function - streams will fail without it
Application Won't Start
Run from Command Prompt to see error messages: RTMP_to_RTSP_Converter.exe
Check Windows Defender/Antivirus isn't blocking it
Port 5000 Already in Use
Close any other applications using port 5000
Or modify the port in app.py before building
Windows Startup Not Working
The app must be run as an .exe (not Python script) for startup registration
Check Windows Registry: HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
May need administrator privileges on some systems
Uninstalling Windows Startup
To remove the application from Windows startup:

Press Win + R
Type shell:startup and press Enter
Or go to Task Manager > Startup tab
Or manually remove from Registry (as mentioned above)
Notes
The application uses port 5000 for the web interface
The RTSP server uses port 8554 by default
All stream conversions run as separate FFmpeg processes
Stopping the application will terminate all active streams
