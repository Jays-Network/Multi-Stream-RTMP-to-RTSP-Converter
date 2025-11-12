Development Notes
Testing in Non-Windows Environments
This application is designed for Windows and requires MediaMTX RTSP server to function. When running in development environments (like Replit) where MediaMTX is not available, you will see the following warning:

WARNING: RTSP server failed to start. Streams will not work!
Download MediaMTX from: https://github.com/bluenviron/mediamtx/releases
Extract mediamtx.exe to a 'mediamtx' folder next to this application

This is expected behavior! The application will still launch and you can interact with the UI, but stream conversion will not function without MediaMTX.

Full Testing Requirements
To fully test the application's stream conversion functionality, you need:

Windows 10/11 environment
MediaMTX RTSP server
Download from: https://github.com/bluenviron/mediamtx/releases
Extract mediamtx.exe to a mediamtx/ folder in the project root
FFmpeg (optional for development)
The app will search for FFmpeg in system PATH
Or place ffmpeg.exe in an ffmpeg/ folder
Development on Linux/macOS
While the application is primarily designed for Windows, MediaMTX is available for Linux and macOS:

Download the appropriate MediaMTX version for your OS
Place the binary in a mediamtx/ folder
Update the get_mediamtx_path() function in app.py to look for the correct binary name (no .exe extension)
The application should work for testing stream functionality
UI Testing
The web UI can be tested without MediaMTX:

Navigate to http://localhost:5000
The interface will load and be fully functional
You can enter RTMP URLs and click "Start Conversion"
However, streams will immediately fail without MediaMTX
This allows testing of the UI/UX without full backend functionality
Production Build Testing
To test the PyInstaller build and full functionality:

Must be done on Windows 10/11
Download MediaMTX and FFmpeg
Follow instructions in BUILD_INSTRUCTIONS.md
Test with real RTMP streams or test stream generators
Mock Testing Without Real Streams
For development purposes without access to real RTMP streams, you can:

Use FFmpeg to create a test RTMP stream:

ffmpeg -re -f lavfi -i testsrc=size=1280x720:rate=30 -f lavfi -i sine=frequency=1000 \
 -c:v libx264 -preset ultrafast -c:a aac -f flv rtmp://localhost:1935/live/test

(Requires an RTMP server like nginx-rtmp or MediaMTX in RTMP mode)

Or test the UI functionality with dummy URLs and expect failures (which is acceptable for UI testing)

Key Points
MediaMTX is mandatory for stream conversion to work
The application gracefully degrades without MediaMTX
Clear error messages guide users to download required components
Windows Registry features only work on Windows (safely ignored on other platforms)
The web UI works independently of the streaming backend
