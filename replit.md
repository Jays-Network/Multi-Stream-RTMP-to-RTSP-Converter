RTMP to RTSP Converter - Replit Project
Project Overview
Multi-Stream RTMP to RTSP Converter is a Windows desktop application designed to convert multiple Real-Time Messaging Protocol (RTMP) input streams into Real-Time Streaming Protocol (RTSP) output streams simultaneously. The application uses FFmpeg as the streaming engine and provides a modern web-based user interface accessible via localhost.

Target Platform: Windows 10/11
Primary Use Case: Stream conversion for video broadcasting, surveillance systems, and media servers
Deployment: Single executable file (.exe) with bundled dependencies

Technology Stack
Backend: Python 3.11 with Flask web framework
Real-time Communication: Flask-SocketIO for WebSocket support
Process Management: psutil for FFmpeg process handling
Frontend: HTML5, CSS3, JavaScript with Bootstrap 5
Streaming Engine: FFmpeg (external binary)
Packaging: PyInstaller for Windows executable creation
Project Architecture
Core Components
Flask Application (app.py)

HTTP server for web UI
REST API endpoints for stream management
WebSocket server for real-time updates
FFmpeg subprocess management
Windows Registry integration for auto-startup
Web Interface (templates/index.html, static/)

Dark-themed responsive UI
Multi-line RTMP input textarea
Real-time stream status display
Individual stream controls (stop, copy URL)
Error/log console
Stream Management

Unique stream ID generation (UUID-based)
Background FFmpeg process spawning
Process monitoring with automatic failure detection
Graceful process termination with psutil
Key Features
Multi-Stream Processing: Handles multiple concurrent RTMP→RTSP conversions
Real-Time Monitoring: WebSocket-based status updates
Process Isolation: Each stream runs in separate FFmpeg process
Auto-Recovery Awareness: Detects and reports stream failures
Windows Integration: Registry-based auto-startup
Browser Auto-Launch: Opens web UI automatically on startup
Current State (November 12, 2025)
Completed Implementation ✅
✅ Flask backend with full stream management API
✅ FFmpeg subprocess handling with process monitoring
✅ MediaMTX RTSP server integration with automatic recovery
✅ Server status checking and gating to prevent invalid stream starts
✅ Responsive dark-themed web UI with warning banners
✅ Real-time WebSocket communication
✅ Windows Registry auto-startup functionality
✅ PyInstaller build configuration
✅ Comprehensive documentation (README, BUILD_INSTRUCTIONS, DEVELOPMENT_NOTES)
✅ Automatic MediaMTX restart when executable is present
✅ Clear error messaging for missing dependencies

Workflow Configuration
Workflow Name: web-server
Command: python app.py
Output Type: webview (accessible at http://0.0.0.0:5000)
Port: 5000
Production Readiness
The application is ready for production deployment on Windows 10/11 with the following requirements:

Required Binaries (not included in repository):

FFmpeg Windows executable → https://www.gyan.dev/ffmpeg/builds/
MediaMTX Windows executable → https://github.com/bluenviron/mediamtx/releases
Next Steps for Deployment:

Download FFmpeg and MediaMTX binaries
Follow BUILD_INSTRUCTIONS.md to create Windows executable
Test with real RTMP sources
Distribute to end users
Development Notes
Important Considerations
FFmpeg Dependency: Application requires FFmpeg binary

Development: FFmpeg must be in system PATH
Production: ffmpeg.exe bundled in ffmpeg/ subfolder
Port Configuration:

Web UI: Port 5000
RTSP Server: Port 8554
Both configurable in app.py
Process Management:

Uses subprocess.Popen with CREATE_NO_WINDOW flag on Windows
Process monitoring via background threads
Clean termination with psutil (terminates child processes)
Windows-Specific Code:

Registry access via winreg module
Auto-startup only activates when running as compiled .exe
Browser auto-launch on first run
Known Limitations
Requires MediaMTX RTSP server (not included in repository due to size)
FFmpeg binary not included in repository (size/licensing)
Windows-only auto-startup feature (cross-platform conversion works)
MediaMTX must be downloaded separately from https://github.com/bluenviron/mediamtx/releases
File Structure
project/
├── app.py # Main Flask application
├── templates/
│ └── index.html # Web UI template
├── static/
│ ├── style.css # Dark theme styling
│ └── app.js # Frontend JavaScript logic
├── build_windows.spec # PyInstaller build configuration
├── BUILD_INSTRUCTIONS.md # Windows build guide
├── README.md # User-facing documentation
├── replit.md # This file - project documentation
├── pyproject.toml # Python dependencies (uv)
└── .replit # Replit configuration

User Preferences
No specific user preferences documented yet. Default configuration:

Dark theme UI
Automatic browser launch
WebSocket-based real-time updates
Console logging enabled
Recent Changes (November 12, 2025)
Initial project setup and structure creation
Complete Flask backend implementation
Web UI with Bootstrap 5 and dark theme
FFmpeg process management system
Windows Registry auto-startup integration
PyInstaller configuration for Windows builds
Comprehensive documentation suite
Deployment Instructions
See BUILD_INSTRUCTIONS.md for complete Windows build process.

Quick Summary:

Download FFmpeg static build for Windows
Install Python dependencies: pip install flask flask-socketio psutil pyinstaller
Build executable: pyinstaller build_windows.spec
Copy ffmpeg.exe to dist/RTMP_to_RTSP_Converter/ffmpeg/
Distribute entire folder
Future Enhancements (Not in MVP)
Stream health monitoring with auto-reconnection
Persistent configuration (save/load RTMP URLs)
Advanced FFmpeg options (bitrate, codec, resolution)
System tray integration
Stream recording capability
Multi-language support
RTSP server bundling (MediaMTX or similar)
