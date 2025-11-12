Multi-Stream RTMP to RTSP Converter
A lightweight Windows application that converts multiple RTMP (Real-Time Messaging Protocol) streams to RTSP (Real-Time Streaming Protocol) streams in real-time using FFmpeg.

Features
Multi-Stream Support: Convert multiple RTMP streams simultaneously
Real-Time Monitoring: Live status updates for each stream
Modern Web UI: Clean, dark-themed responsive interface
Process Management: Individual control over each stream conversion
Auto-Startup: Automatically launches on Windows login
FFmpeg Integration: Leverages FFmpeg for reliable stream conversion
Error Logging: Comprehensive logging console for troubleshooting
System Requirements
Windows 10/11
FFmpeg (bundled with executable)
MediaMTX RTSP server (bundled with executable)
Network access to RTMP sources
Quick Start
For End Users (Executable)
Download the RTMP_to_RTSP_Converter folder
Ensure ffmpeg.exe is in the ffmpeg/ subfolder
Ensure mediamtx.exe is in the mediamtx/ subfolder
Run RTMP_to_RTSP_Converter.exe
Your browser will automatically open to http://127.0.0.1:5000
For Developers (Source Code)
Install Python 3.11+
Download MediaMTX from https://github.com/bluenviron/mediamtx/releases
Extract and place mediamtx.exe in a mediamtx folder
Install dependencies:
pip install flask flask-socketio psutil pyinstaller

Run the application:
python app.py

Open http://127.0.0.1:5000 in your browser
Usage
Enter RTMP URLs: In the input area, enter one RTMP URL per line

rtmp://source.example.com/live/stream1
rtmp://source.example.com/live/stream2

Start Conversion: Click "Start Conversion & Serve"

Monitor Streams: Each stream will appear in the "Active RTSP Streams" section with:

Status indicator (🟢 Active, 🟡 Starting, 🔴 Stopped)
Source RTMP URL
Output RTSP URL (e.g., rtsp://127.0.0.1:8554/stream-id)
Copy and Stop buttons
Use RTSP Streams: Copy the RTSP URLs and use them in:

VLC Media Player
OBS Studio
Any RTSP-compatible player/software
Stop Streams: Click individual "Stop" buttons or "Stop All"

Architecture
Technology Stack
Backend: Python + Flask + Flask-SocketIO
Frontend: HTML5 + CSS3 + JavaScript + Bootstrap 5
Streaming Engine: FFmpeg
RTSP Server: MediaMTX (formerly rtsp-simple-server)
Process Management: psutil
Packaging: PyInstaller
How It Works
Application starts MediaMTX RTSP server on port 8554
User provides RTMP stream URLs
Application spawns separate FFmpeg process for each stream
FFmpeg pulls from RTMP source and pushes to MediaMTX RTSP server
MediaMTX serves RTSP streams to clients on localhost:8554
WebSocket provides real-time status updates
Process monitoring ensures failed streams are detected
FFmpeg Command Pattern
ffmpeg -i rtmp://source/stream -c:v copy -c:a copy -f rtsp rtsp://127.0.0.1:8554/stream-id

Configuration
Ports
Web Interface: 5000 (configurable in app.py)
RTSP Server: 8554 (configurable in app.py)
Windows Startup
The application automatically registers itself to run on Windows startup by adding an entry to:

HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run

Building from Source
See BUILD_INSTRUCTIONS.md for detailed build instructions.

Summary:

Download FFmpeg for Windows
Install Python dependencies
Run pyinstaller build_windows.spec
Copy ffmpeg.exe to distribution folder
Distribute the entire folder
Troubleshooting
FFmpeg Not Found
Ensure ffmpeg.exe is in the ffmpeg/ folder next to the executable
For development, ensure FFmpeg is in your system PATH
MediaMTX Not Found / Streams Won't Start
Ensure mediamtx.exe is in the mediamtx/ folder next to the executable
Download from https://github.com/bluenviron/mediamtx/releases
MediaMTX is required for the RTSP server - streams will fail without it
Stream Won't Start
Verify the RTMP URL is valid and accessible
Check firewall settings
Review the Error/Log Console for FFmpeg errors
Port Already in Use
Close applications using port 5000 or 8554
Or modify the ports in app.py before building
Browser Doesn't Open
Manually navigate to http://127.0.0.1:5000
Check if another application is using port 5000
Project Structure
project/
├── app.py # Main Flask application
├── templates/
│ └── index.html # Web UI template
├── static/
│ ├── style.css # Styling
│ └── app.js # Frontend logic
├── build_windows.spec # PyInstaller configuration
├── BUILD_INSTRUCTIONS.md # Build guide
├── README.md # This file
└── ffmpeg/ # FFmpeg executable (for distribution)
└── ffmpeg.exe

License
This project is provided as-is for educational and commercial use.

Acknowledgments
FFmpeg for the powerful streaming engine
Flask and Socket.IO for the web framework
Bootstrap for the UI components
