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

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
socketio = SocketIO(app, cors_allowed_origins="*")

streams = {}
mediamtx_process = None

RTSP_SERVER_PORT = 8554
RTSP_SERVER_HOST = "127.0.0.1"


def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        base_path = getattr(sys, '_MEIPASS', '')
        ffmpeg_path = os.path.join(base_path, 'ffmpeg', 'ffmpeg.exe')
        if os.path.exists(ffmpeg_path):
            return ffmpeg_path
    
    ffmpeg_candidates = ['ffmpeg.exe', 'ffmpeg']
    for candidate in ffmpeg_candidates:
        try:
            result = subprocess.run([candidate, '-version'], 
                                   capture_output=True, 
                                   timeout=5)
            if result.returncode == 0:
                return candidate
        except Exception:
            continue
    
    return 'ffmpeg'


def get_mediamtx_path():
    if getattr(sys, 'frozen', False):
        base_path = getattr(sys, '_MEIPASS', '')
        mediamtx_path = os.path.join(base_path, 'mediamtx', 'mediamtx.exe')
        if os.path.exists(mediamtx_path):
            return mediamtx_path
    
    mediamtx_candidates = ['mediamtx.exe', 'mediamtx', './mediamtx/mediamtx.exe', './mediamtx']
    for candidate in mediamtx_candidates:
        if os.path.exists(candidate):
            return candidate
    
    return 'mediamtx.exe'


def generate_stream_id():
    return str(uuid.uuid4())[:8]


def is_port_open(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def start_rtsp_server():
    global mediamtx_process
    
    if is_port_open(RTSP_SERVER_HOST, RTSP_SERVER_PORT):
        print(f"RTSP server already running on {RTSP_SERVER_HOST}:{RTSP_SERVER_PORT}")
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
                print(f"MediaMTX RTSP server started successfully on port {RTSP_SERVER_PORT}")
                return True
        
        print("MediaMTX started but port not available")
        return False
        
    except FileNotFoundError:
        print(f"MediaMTX not found at {mediamtx_path}. Please download MediaMTX from https://github.com/bluenviron/mediamtx/releases")
        print("Place mediamtx.exe in a 'mediamtx' folder next to this application.")
        return False
    except Exception as e:
        print(f"Failed to start MediaMTX: {str(e)}")
        return False


def stop_rtsp_server():
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
                if mediamtx_process:
                    mediamtx_process.kill()
            except Exception:
                pass
        mediamtx_process = None


def monitor_process(stream_id, process):
    try:
        while True:
            if stream_id not in streams:
                break
            
            if process.poll() is not None:
                stderr_output = process.stderr.read() if process.stderr else ""
                
                if streams[stream_id]['status'] == 'active':
                    streams[stream_id]['status'] = 'stopped'
                    streams[stream_id]['error'] = f"Process terminated unexpectedly. Exit code: {process.returncode}"
                    
                    log_message = f"Stream {stream_id} stopped unexpectedly. Exit code: {process.returncode}"
                    if stderr_output:
                        log_message += f"\nFFmpeg output: {stderr_output[:500]}"
                    
                    socketio.emit('log', {'message': log_message, 'type': 'error'})
                    socketio.emit('stream_update', {
                        'stream_id': stream_id,
                        'status': 'stopped',
                        'error': streams[stream_id]['error']
                    })
                break
            
            time.sleep(2)
    except Exception as e:
        print(f"Monitor thread error for {stream_id}: {str(e)}")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/status', methods=['GET'])
def get_status():
    rtsp_server_running = is_port_open(RTSP_SERVER_HOST, RTSP_SERVER_PORT)
    
    if not rtsp_server_running:
        mediamtx_path = get_mediamtx_path()
        if os.path.exists(mediamtx_path):
            print(f"RTSP server not running, attempting to start MediaMTX...")
            if start_rtsp_server():
                rtsp_server_running = True
                print("MediaMTX started successfully via status check")
            else:
                print("Failed to start MediaMTX via status check")
    
    return jsonify({
        'rtsp_server_running': rtsp_server_running,
        'rtsp_server_port': RTSP_SERVER_PORT,
        'active_streams': len([s for s in streams.values() if s['status'] == 'active'])
    })


@app.route('/api/streams', methods=['GET'])
def get_streams():
    stream_list = []
    for stream_id, stream_data in streams.items():
        stream_list.append({
            'id': stream_id,
            'rtmp_url': stream_data['rtmp_url'],
            'rtsp_url': stream_data['rtsp_url'],
            'status': stream_data['status'],
            'error': stream_data.get('error', '')
        })
    return jsonify(stream_list)


@app.route('/api/start', methods=['POST'])
def start_streams():
    if not is_port_open(RTSP_SERVER_HOST, RTSP_SERVER_PORT):
        mediamtx_path = get_mediamtx_path()
        if os.path.exists(mediamtx_path):
            print("RTSP server not running, attempting to start MediaMTX before processing streams...")
            if not start_rtsp_server():
                error_msg = 'Failed to start MediaMTX RTSP server. Please check that port 8554 is available.'
                socketio.emit('log', {
                    'message': error_msg,
                    'type': 'error'
                })
                return jsonify({'error': error_msg}), 503
            socketio.emit('log', {
                'message': 'MediaMTX RTSP server started successfully',
                'type': 'info'
            })
        else:
            error_msg = f'MediaMTX not found at {mediamtx_path}. Please download MediaMTX from https://github.com/bluenviron/mediamtx/releases and place mediamtx.exe in a mediamtx folder.'
            socketio.emit('log', {
                'message': error_msg,
                'type': 'error'
            })
            return jsonify({'error': error_msg}), 503
    
    data = request.json if request.json else {}
    rtmp_urls = data.get('rtmp_urls', []) if data else []
    
    if not rtmp_urls:
        return jsonify({'error': 'No RTMP URLs provided'}), 400
    
    started_streams = []
    
    for rtmp_url in rtmp_urls:
        rtmp_url = rtmp_url.strip()
        if not rtmp_url:
            continue
        
        if not rtmp_url.startswith('rtmp://'):
            socketio.emit('log', {
                'message': f'Invalid RTMP URL: {rtmp_url}',
                'type': 'error'
            })
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
        
        ffmpeg_path = get_ffmpeg_path()
        
        ffmpeg_cmd = [
            ffmpeg_path,
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
            streams[stream_id]['status'] = 'active'
            
            monitor_thread = threading.Thread(
                target=monitor_process,
                args=(stream_id, process),
                daemon=True
            )
            monitor_thread.start()
            
            started_streams.append({
                'id': stream_id,
                'rtmp_url': rtmp_url,
                'rtsp_url': rtsp_url,
                'status': 'active'
            })
            
            socketio.emit('log', {
                'message': f'Started stream {stream_id}: {rtmp_url} -> {rtsp_url}',
                'type': 'info'
            })
            
            socketio.emit('stream_update', {
                'stream_id': stream_id,
                'rtmp_url': rtmp_url,
                'rtsp_url': rtsp_url,
                'status': 'active',
                'error': ''
            })
            
        except Exception as e:
            streams[stream_id]['status'] = 'stopped'
            streams[stream_id]['error'] = str(e)
            
            socketio.emit('log', {
                'message': f'Failed to start stream {stream_id}: {str(e)}',
                'type': 'error'
            })
            
            socketio.emit('stream_update', {
                'stream_id': stream_id,
                'status': 'stopped',
                'error': str(e)
            })
    
    return jsonify({'streams': started_streams})


@app.route('/api/stop/<stream_id>', methods=['POST'])
def stop_stream(stream_id):
    if stream_id not in streams:
        return jsonify({'error': 'Stream not found'}), 404
    
    stream_data = streams[stream_id]
    process = stream_data.get('process')
    
    if process:
        parent = None
        try:
            parent = psutil.Process(process.pid)
            for child in parent.children(recursive=True):
                child.terminate()
            parent.terminate()
            
            process.wait(timeout=5)
        except psutil.NoSuchProcess:
            pass
        except psutil.TimeoutExpired:
            try:
                if parent:
                    parent.kill()
                    for child in parent.children(recursive=True):
                        child.kill()
            except Exception:
                pass
        except Exception as e:
            print(f"Error stopping process: {str(e)}")
    
    streams[stream_id]['status'] = 'stopped'
    streams[stream_id]['process'] = None
    
    socketio.emit('log', {
        'message': f'Stopped stream {stream_id}',
        'type': 'info'
    })
    
    socketio.emit('stream_update', {
        'stream_id': stream_id,
        'status': 'stopped'
    })
    
    return jsonify({'message': 'Stream stopped'})


@app.route('/api/stop_all', methods=['POST'])
def stop_all_streams():
    for stream_id in list(streams.keys()):
        stream_data = streams[stream_id]
        process = stream_data.get('process')
        
        if process:
            parent = None
            try:
                parent = psutil.Process(process.pid)
                for child in parent.children(recursive=True):
                    child.terminate()
                parent.terminate()
                process.wait(timeout=2)
            except Exception:
                try:
                    if parent:
                        parent.kill()
                except Exception:
                    pass
        
        streams[stream_id]['status'] = 'stopped'
        streams[stream_id]['process'] = None
    
    socketio.emit('log', {
        'message': 'All streams stopped',
        'type': 'info'
    })
    
    return jsonify({'message': 'All streams stopped'})


@socketio.on('connect')
def handle_connect():
    emit('log', {'message': 'Connected to server', 'type': 'info'})


def setup_windows_startup():
    if sys.platform != 'win32':
        return False
    
    if not getattr(sys, 'frozen', False):
        return False
    
    try:
        import winreg
        
        exe_path = sys.executable
        app_name = "RTMPtoRTSPConverter"
        
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
        
        return True
    except Exception as e:
        print(f"Failed to setup Windows startup: {str(e)}")
        return False


def open_browser():
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')


def cleanup():
    print("Shutting down...")
    for stream_id in list(streams.keys()):
        stream_data = streams[stream_id]
        process = stream_data.get('process')
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
    print("Cleanup complete")


if __name__ == '__main__':
    import atexit
    atexit.register(cleanup)
    
    print("Starting RTMP to RTSP Converter...")
    
    if start_rtsp_server():
        print("RTSP server is ready")
    else:
        print("WARNING: RTSP server failed to start. Streams will not work!")
        print("Download MediaMTX from: https://github.com/bluenviron/mediamtx/releases")
        print("Extract mediamtx.exe to a 'mediamtx' folder next to this application")
    
    if getattr(sys, 'frozen', False):
        setup_windows_startup()
        threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False, log_output=True, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        cleanup()
