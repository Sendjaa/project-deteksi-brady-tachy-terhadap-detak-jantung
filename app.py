from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kunci_rahasia_proyek_pi'

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    ping_timeout=60,
    ping_interval=25
)

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/logs')
def logs():
    return render_template('logs.html')

# --- SOCKET.IO EVENTS ---

@socketio.on('connect')
def handle_connect():
    print(">>> Browser/Klien terhubung.")

@socketio.on('disconnect')
def handle_disconnect():
    print(">>> Browser/Klien terputus.")

@socketio.on('sensor_data_from_pi')
def handle_pi_data(data):
    """Menerima data dari Raspberry Pi dan kirim ke Dashboard"""
    data['server_time'] = datetime.now().strftime("%H:%M:%S")

    # Log ke terminal laptop
    bpm = data.get('heart_rate', 0)
    spo2 = data.get('spo2', 0)
    print(f"[{data['server_time']}] DATA MASUK: BPM {bpm} | SpO2 {spo2}%")

    # Broadcast ke semua client (Dashboard)
    emit('update_web_client', data, broadcast=True)

if __name__ == '__main__':
    print("==============================================")
    print("      SERVER MONITORING KESEHATAN AKTIF       ")
    print("==============================================")

    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
