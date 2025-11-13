import os
import sys
import subprocess
import uuid
import psutil
import webbrowser
import threading
import time
import socket
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit

# ---------------------------------------------------------------
# Flask + Socket.IO Setup
# ---------------------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
socketio = SocketIO(app, cors_allowed_origins="*")

# ---------------------------------------------------------------
# Global Variables
# ---------------------------------------------------------------
streams = {}
mediamtx_process = None

# RTSP Server Configuration
RTSP_SERVER_HOST = "localhost"  # localhost only
RTSP_SERVER_PORT = 8554         # MediaMTX default RTSP port

# ---------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------
def get_ffmpeg_path():
    """Detect or return bundled ffmpeg path."""
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
        ffmpeg_path = os.path.join(base_path, 'ffmpeg', 'ffmpeg.exe')
        if os.path.exists(ffmpeg_path):
            return ffmpeg_path
    
    ffmpeg_candidates = ['ffmpeg.exe', 'ffmpeg']
    for candidate in ffmpeg_candidates:
        try:
            result = subprocess.run([candidate, '-version'], capture_output=True, timeout=5)
            if result.returncode == 0:
                return candidate
        except Exception:
            continue
    
    return 'ffmpeg'


def get_mediamtx_path():
    """Locate MediaMTX executable."""
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
        mediamtx_path = os.path.join(base_path, 'mediamtx', 'mediamtx.exe')
        if os.path.exists(mediamtx_path):
            return mediamtx_path
    
    mediamtx_candidates = ['mediamtx.exe', 'mediamtx', './mediamtx/mediamtx.exe', './mediamtx']
    for candidate in mediamtx_candidates:
        if os.path.exists(candidate):
            return candidate
    
    return 'mediamtx.exe'


def generate_stream_id():
    """Create a unique stream ID."""
    return str(uuid.uuid4())[:8]


def is_port_open(host, port):
    """Check if a port is already in use."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


# ---------------------------------------------------------------
# MediaMTX Management
# ---------------------------------------------------------------
def start_rtsp_server():
    """Start the MediaMTX RTSP server."""
    global mediamtx_process

    if is_port_open(RTSP_SERVER_HOST, RTSP_SERVER_PORT):
        print(f"[INFO] RTSP server already running on {RTSP_SERVER_HOST}:{RTSP_SERVER_PORT}")
        return True
    
    mediamtx_path = get_mediamtx_path()
    
    try:
        mediamtx_process = subprocess.Popen(
            [mediamtx_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        
        for _ in range(10):
            time.sleep(0.5)
            if is_port_open(RTSP_SERVER_HOST, RTSP_SERVER_PORT):
                print(f"[INFO] MediaMTX RTSP server started successfully on port {RTSP_SERVER_PORT}")
                return True
        
        print("[WARN] MediaMTX started but RTSP port not responding.")
        return False
        
    except FileNotFoundError:
        print(f"[ERROR] MediaMTX not found at {mediamtx_path}")
        print("Download from: https://github.com/bluenviron/mediamtx/releases")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to start MediaMTX: {str(e)}")
        return False


def stop_rtsp_server():
    """Stop the MediaMTX server."""
    global mediamtx_process
    if mediamtx_process:
        try:
            parent = psutil.Process(mediamtx_process.pid)
            for child in parent.children(recursive=True):
                child.terminate()
            parent.terminate()
            mediamtx_process.wait(timeout=5)
        except Exception:
            try:
                mediamtx_process.kill()
            except Exception:
                pass
        mediamtx_process = None
        print("[INFO] MediaMTX stopped.")


# ---------------------------------------------------------------
# Stream Process Management
# ---------------------------------------------------------------
def monitor_process(stream_id, process):
    """Monitor FFmpeg subprocess and detect errors."""
    stderr_lines = iter(process.stderr.readline, b'')
    startup_failed = False

    try:
        start_time = time.time()
        startup_timeout = 5

        for line in stderr_lines:
            if stream_id not in streams:
                break

            log_message = line.decode('utf-8', errors='ignore').strip()
            if not log_message:
                continue

            if "could not open" in log_message.lower() or "no such file" in log_message.lower():
                startup_failed = True
                streams[stream_id]['error'] = log_message
                streams[stream_id]['status'] = 'stopped'
                socketio.emit('log', {'message': f"[ERROR] {log_message}", 'type': 'error'})
                socketio.emit('stream_update', {'stream_id': stream_id, 'status': 'stopped', 'error': log_message})
                break

            if time.time() - start_time > startup_timeout and streams[stream_id]['status'] == 'starting':
                streams[stream_id]['status'] = 'active'
                socketio.emit('stream_update', {'stream_id': stream_id, 'status': 'active', 'error': ''})
                socketio.emit('log', {'message': f"[INFO] Stream {stream_id} is now active.", 'type': 'info'})

            if process.poll() is not None:
                break

        if process.poll() is not None and streams[stream_id]['status'] != 'stopped' and not startup_failed:
            streams[stream_id]['status'] = 'stopped'
            streams[stream_id]['error'] = f"Process exited (code {process.returncode})"
            socketio.emit('log', {'message': f"[WARN] Stream {stream_id} stopped unexpectedly.", 'type': 'error'})
            socketio.emit('stream_update', {'stream_id': stream_id, 'status': 'stopped', 'error': streams[stream_id]['error']})
    except Exception as e:
        print(f"[ERROR] Monitor thread for {stream_id}: {e}")


# ---------------------------------------------------------------
# Flask API Routes
# ---------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/status', methods=['GET'])
def get_status():
    rtsp_server_running = is_port_open(RTSP_SERVER_HOST, RTSP_SERVER_PORT)
    
    if not rtsp_server_running:
        mediamtx_path = get_mediamtx_path()
        if os.path.exists(mediamtx_path):
            print("[INFO] RTSP server not running, attempting to start MediaMTX...")
            if start_rtsp_server():
                rtsp_server_running = True
                print("[INFO] MediaMTX started via status check.")
    
    return jsonify({
        'rtsp_server_running': rtsp_server_running,
        'rtsp_server_port': RTSP_SERVER_PORT,
        'active_streams': len([s for s in streams.values() if s['status'] == 'active'])
    })


@app.route('/api/streams', methods=['GET'])
def get_streams():
    return jsonify([
        {
            'id': sid,
            'rtmp_url': s['rtmp_url'],
            'rtsp_url': s['rtsp_url'],
            'status': s['status'],
            'error': s.get('error', '')
        } for sid, s in streams.items()
    ])


@app.route('/api/start', methods=['POST'])
def start_streams():
    """Start one or more FFmpeg RTMP->RTSP relay processes."""
    if not is_port_open(RTSP_SERVER_HOST, RTSP_SERVER_PORT):
        if not start_rtsp_server():
            return jsonify({'error': 'Failed to start MediaMTX RTSP server'}), 503

    data = request.json or {}
    rtmp_urls = data.get('rtmp_urls', [])
    if not rtmp_urls:
        return jsonify({'error': 'No RTMP URLs provided'}), 400

    started_streams = []
    ffmpeg_path = get_ffmpeg_path()

    for rtmp_url in rtmp_urls:
        rtmp_url = rtmp_url.strip()
        if not rtmp_url.startswith('rtmp://'):
            socketio.emit('log', {'message': f"[ERROR] Invalid RTMP URL: {rtmp_url}", 'type': 'error'})
            continue

        stream_id = generate_stream_id()
        rtsp_url = f"rtsp://{RTSP_SERVER_HOST}:{RTSP_SERVER_PORT}/{stream_id}"

        streams[stream_id] = {
            'rtmp_url': rtmp_url,
            'rtsp_url': rtsp_url,
            'status': 'starting',
            'process': None,
            'error': ''
        }

        ffmpeg_cmd = [
            ffmpeg_path,
            '-analyzeduration', '1000000',
            '-probesize', '1000000',
            '-i', rtmp_url,
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-f', 'rtsp',
            '-rtsp_transport', 'tcp',
            rtsp_url
        ]

        try:
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )

            streams[stream_id]['process'] = process
            threading.Thread(target=monitor_process, args=(stream_id, process), daemon=True).start()

            started_streams.append({'id': stream_id, 'rtmp_url': rtmp_url, 'rtsp_url': rtsp_url, 'status': 'starting'})
            socketio.emit('log', {'message': f"[INFO] Starting stream {stream_id}: {rtmp_url} -> {rtsp_url}", 'type': 'info'})
        except Exception as e:
            streams[stream_id]['status'] = 'stopped'
            streams[stream_id]['error'] = str(e)
            socketio.emit('log', {'message': f"[ERROR] Failed to start stream {stream_id}: {e}", 'type': 'error'})

    return jsonify({'streams': started_streams})


@app.route('/api/stop/<stream_id>', methods=['POST'])
def stop_stream(stream_id):
    """Stop a specific FFmpeg stream process."""
    if stream_id not in streams:
        return jsonify({'error': 'Stream not found'}), 404

    stream = streams[stream_id]
    process = stream.get('process')

    if process:
        try:
            parent = psutil.Process(process.pid)
            for child in parent.children(recursive=True):
                child.terminate()
            parent.terminate()
            process.wait(timeout=3)
        except Exception:
            try:
                process.kill()
            except Exception:
                pass

    streams[stream_id]['status'] = 'stopped'
    socketio.emit('log', {'message': f"[INFO] Stopped stream {stream_id}", 'type': 'info'})
    return jsonify({'message': f'Stream {stream_id} stopped'})


@app.route('/api/stop_all', methods=['POST'])
def stop_all_streams():
    """Stop all active streams."""
    for sid, stream in list(streams.items()):
        process = stream.get('process')
        if process:
            try:
                parent = psutil.Process(process.pid)
                for child in parent.children(recursive=True):
                    child.terminate()
                parent.terminate()
            except Exception:
                pass
        streams[sid]['status'] = 'stopped'

    socketio.emit('log', {'message': '[INFO] All streams stopped', 'type': 'info'})
    return jsonify({'message': 'All streams stopped'})


# ---------------------------------------------------------------
# Misc Utilities
# ---------------------------------------------------------------
@socketio.on('connect')
def handle_connect():
    emit('log', {'message': '[INFO] Connected to server', 'type': 'info'})


def setup_windows_startup():
    """Auto-start app on Windows boot if frozen."""
    if sys.platform != 'win32' or not getattr(sys, 'frozen', False):
        return False
    try:
        import winreg
        exe_path = sys.executable
        app_name = "RTMPtoRTSPConverter"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"[WARN] Startup registration failed: {e}")
        return False


def open_browser():
    """Auto-open web UI."""
    time.sleep(1.5)
    webbrowser.open('http://localhost:5000')


def cleanup():
    """Terminate all subprocesses on exit."""
    print("[INFO] Cleaning up...")
    for stream in list(streams.values()):
        process = stream.get('process')
        if process:
            try:
                process.terminate()
                process.wait(timeout=2)
            except Exception:
                try:
                    process.kill()
                except Exception:
                    pass
    stop_rtsp_server()
    print("[INFO] Cleanup complete.")


# ---------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------
if __name__ == '__main__':
    import atexit
    atexit.register(cleanup)

    print("[BOOT] Starting RTMP → RTSP Converter")

    if start_rtsp_server():
        print(f"[READY] RTSP server listening at rtsp://{RTSP_SERVER_HOST}:{RTSP_SERVER_PORT}/<stream_id>")
    else:
        print("[WARN] RTSP server failed to start. Streams will not work!")

    if getattr(sys, 'frozen', False):
        setup_windows_startup()
        threading.Thread(target=open_browser, daemon=True).start()

    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False,
                     log_output=True, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n[EXIT] Interrupted by user.")
    finally:
        cleanup()
