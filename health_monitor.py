import time
import json
import numpy as np
import socketio
import math
from collections import deque

SERVER_URL = "http://192.168.97.69:5000"
DEVICE_ID = "pi4_001"
SAMPLE_RATE = 100
BUFFER_SIZE = SAMPLE_RATE * 4
SEND_INTERVAL_SECONDS = 3
loops_per_send = int(SEND_INTERVAL_SECONDS * SAMPLE_RATE)

BPM_NORMAL_MIN = 60
BPM_NORMAL_MAX = 100

red_buffer = deque(maxlen=BUFFER_SIZE)
ir_buffer = deque(maxlen=BUFFER_SIZE)
SIO = socketio.Client()
start_time = time.time()
loop_counter = 0

# --- CEK DRIVER ---
try:
    from max30102 import MAX30102
    SENSOR_MODE = "HARDWARE"
    print("Mode: HARDWARE (Sensor MAX30102 Aktif)")
except ImportError as e:
    SENSOR_MODE = "SIMULATION"
    print(f"Mode: SIMULATION (Driver tidak ditemukan: {e})")

def connect_socketio():
    try:
        if not SIO.connected:
            SIO.connect(SERVER_URL)
            print(f"SIO: Koneksi berhasil ke {SERVER_URL}")
        return True
    except Exception as e:
        print(f"SIO: Gagal terhubung ke server. (Cek IP Laptop!)")
        return False

def send_data_via_sio(bpm, spo2, condition):
    if not SIO.connected:
        if not connect_socketio(): return

    data = {
        "device_id": DEVICE_ID,
        "timestamp": time.strftime("%H:%M:%S"),
        "heart_rate": bpm,
        "spo2": spo2,
        "condition": condition
    }
    try:
        SIO.emit('sensor_data_from_pi', data)
    except Exception as e:
        print(f"SIO Error: {e}")

def init_sensor():
    if SENSOR_MODE == "HARDWARE":
        try:
            sensor = MAX30102(i2c_bus=1)
            sensor.setup_sensor()
            print("MAX30102 Berhasil Dikonfigurasi.")
            return sensor
        except Exception as e:
            print(f"Hardware Error: {e}")
            return None
    return None

def read_data(sensor_obj, current_time):
    if SENSOR_MODE == "HARDWARE" and sensor_obj:
        sensor_obj.read_sensor()
        if sensor_obj.buffer_red and sensor_obj.buffer_ir:
            return sensor_obj.buffer_red[-1], sensor_obj.buffer_ir[-1]
        return 0, 0
    else:
        sim_bpm = 75
        frequency_hz = sim_bpm / 60.0
        sin_value = math.sin(2 * math.pi * frequency_hz * current_time)
        sim_red = int(150000 + 8000 * sin_value + np.random.randint(-500, 500))
        sim_ir = int(200000 + 10000 * sin_value + np.random.randint(-500, 500))
        return sim_red, sim_ir

def calculate_bpm_spo2(red_data, ir_data):
    if len(red_data) < BUFFER_SIZE:
        return 0, 0.0, "Wait..."

    red_dc = np.mean(red_data)
    ir_dc = np.mean(ir_data)
    ir_ac = ir_data - ir_dc

    peaks = np.where(ir_ac > 5000)[0]
    if len(peaks) > 1:
        bpm = (SAMPLE_RATE / np.mean(np.diff(peaks))) * 60
    else:
        bpm = 0

    max_red_ac = np.max(np.abs(red_data - red_dc))
    max_ir_ac = np.max(np.abs(ir_data - ir_dc))

    R = (max_red_ac / red_dc) / (max_ir_ac / ir_dc) if ir_dc > 0 else 0
    spo2 = 110 - 25 * R
    spo2 = max(min(spo2, 100.0), 90.0)

    return int(bpm), round(spo2, 1), f"R:{round(R,3)}"

def check_heart_condition(bpm):
    if bpm == 0: return "WAITING"
    if bpm < BPM_NORMAL_MIN: return "BRADYCARDIA"
    if bpm > BPM_NORMAL_MAX: return "TACHYCARDIA"
    return "NORMAL"

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    sensor_handle = init_sensor()
    connect_socketio()

    print("--- Proyek Aktif. Tekan Ctrl+C untuk berhenti ---")

    # Loop ini akan berjalan selamanya sampai dihentikan paksa
    try:
        while True:
            current_time = time.time() - start_time
            r_val, ir_val = read_data(sensor_handle, current_time)

            if r_val > 0:
                red_buffer.append(r_val)
                ir_buffer.append(ir_val)

            if len(red_buffer) == BUFFER_SIZE:
                bpm, spo2, r_stat = calculate_bpm_spo2(np.array(red_buffer), np.array(ir_buffer))
                cond = check_heart_condition(bpm)

                # Gunakan loop_counter global
                loop_counter += 1
                if loop_counter >= loops_per_send:
                    if bpm > 0:
                        send_data_via_sio(bpm, spo2, cond)
                    loop_counter = 0

                print(f"BPM: {bpm:<3} | SpO2: {spo2}% | {cond:<12} | {r_stat}", end='\r')
            else:
                print(f"Filling Buffer: {len(red_buffer)}/{BUFFER_SIZE}", end='\r')

            time.sleep(1 / SAMPLE_RATE)

    except KeyboardInterrupt:
        print("\nProgram dihentikan secara manual.")
    finally:
        if SIO.connected:
            SIO.disconnect()
