import serial
import socket
import subprocess
import sys
import time
import threading

# --- CẤU HÌNH ---
RENODE_IP = '127.0.0.1'
RENODE_PORT = 3333      # Cổng UART của Renode
DE1_PORT = 'COM5'       # Cổng DE1 thật
DE1_BAUD = 115200

def run_game(script_name, ser_port):
    """Đóng cổng Serial, chạy game, sau đó mở lại cổng"""
    print(f"\n[SYSTEM] >>> LAUNCHING {script_name.upper()} <<<")
    
    # 1. Đóng kết nối Serial ở đây để Game con có thể chiếm quyền sử dụng
    if ser_port and ser_port.is_open:
        ser_port.close()
        print("[CONTROLLER] Released DE1 Serial Port.")

    # 2. Gọi file game
    try:
        process = subprocess.Popen([sys.executable, script_name])
        process.wait() # Chờ game chơi xong mới chạy tiếp code bên dưới
    except Exception as e:
        print(f"Error launching game: {e}")

    # 3. Mở lại Serial để chọn game tiếp
    print("[CONTROLLER] Game Closed. Reconnecting to DE1...")
    time.sleep(1)
    try:
        ser_port.open()
        print("[CONTROLLER] DE1 Ready. Select Game: [KEY 0] CyberSnake | [KEY 1] CyberBeat")
    except:
        print("[ERROR] Cannot reconnect to DE1. Please restart script.")

def main():
    # Kết nối DE1
    ser = None
    try:
        ser = serial.Serial(DE1_PORT, DE1_BAUD, timeout=0.1)
        print(f"✅ DE1-SoC Connected on {DE1_PORT}")
    except:
        print(f"❌ Warning: Cannot connect to {DE1_PORT}. You can only use keyboard.")

    print("\n" + "="*40)
    print("      CYBER CONSOLE MASTER CONTROL      ")
    print("="*40)
    print(" [KEY 0] or 'S' -> Play CYBER SNAKE")
    print(" [KEY 1] or 'B' -> Play CYBER BEAT")
    print(" [Ctrl+C]       -> EXIT")
    print("="*40)

    while True:
        try:
            cmd = ""
            
            # 1. Đọc từ DE1 (Nếu có)
            if ser and ser.in_waiting > 0:
                try:
                    cmd = ser.read().decode('utf-8', errors='ignore').strip()
                except: pass

            # 2. (Tùy chọn) Đọc bàn phím máy tính để test nhanh (dùng input non-blocking khó hơn nên ta giả lập)
            # Ở đây ta ưu tiên DE1.
            
            # 3. Xử lý lệnh
            if cmd == '0': # KEY 0 trên DE1
                run_game("cyber_snake_game.py", ser)
            elif cmd == '1': # KEY 1 trên DE1
                run_game("cyber_beat_game.py", ser)
            
            # Giảm tải CPU
            time.sleep(0.05)

        except KeyboardInterrupt:
            print("\nExiting Console.")
            break
        except Exception as e:
            pass

if __name__ == "__main__":
    main()