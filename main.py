import time, random, threading, numpy as np, win32api, win32con, os, json
from PIL import ImageGrab
from pynput import mouse, keyboard

# Konfigurasi Default (Langsung di dalam kode agar aman tanpa CMD)
CONFIG = {
    "SMOOTHING": 0.4,
    "FOV": 40,
    "TOLERANCE": 40,
    "HEAD_OFFSET": 5,
    "RECOIL_AMOUNT": 15
}

class FlickBot:
    def __init__(self):
        self.is_holding = False
        self.has_flicked = False
        # Ambil resolusi layar otomatis
        self.cx = win32api.GetSystemMetrics(0) // 2
        self.cy = win32api.GetSystemMetrics(1) // 2

    def scan_and_flick(self):
        f = CONFIG["FOV"]
        bbox = (self.cx - f, self.cy - f, self.cx + f, self.cy + f)
        # Ambil gambar di tengah layar
        img = ImageGrab.grab(bbox=bbox)
        px = np.array(img)
        
        # Cari warna ungu (target default game FPS)
        for y in range(0, len(px), 2):
            for x in range(0, len(px[y]), 2):
                r, g, b = px[y][x]
                if abs(r - 250) < CONFIG["TOLERANCE"] and abs(g - 100) < CONFIG["TOLERANCE"] and abs(b - 250) < CONFIG["TOLERANCE"]:
                    # Hitung posisi target
                    tx = x + (self.cx - f)
                    ty = y + (self.cy - f) - CONFIG["HEAD_OFFSET"]
                    
                    # Eksekusi Flick
                    mx = int((tx - self.cx) * CONFIG["SMOOTHING"])
                    my = int((ty - self.cy) * CONFIG["SMOOTHING"])
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, mx, my, 0, 0)
                    
                    # Recoil Control (Tarik kebawah sedikit)
                    time.sleep(0.02)
                    recoil = CONFIG["RECOIL_AMOUNT"] + random.randint(-2, 2)
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, recoil, 0, 0)
                    return True
        return False

    def main_loop(self):
        while True:
            if self.is_holding and not self.has_flicked:
                if self.scan_and_flick():
                    self.has_flicked = True # Kunci agar cuma flick 1x
            elif not self.is_holding:
                self.has_flicked = False # Reset saat lepas klik
            time.sleep(0.001)

bot = FlickBot()

def on_click(x, y, button, pressed):
    if button == mouse.Button.left:
        bot.is_holding = pressed

def on_press(key):
    if key == keyboard.Key.delete: # Tekan tombol DELETE untuk mematikan
        os._exit(0)

# Jalankan Bot
threading.Thread(target=bot.main_loop, daemon=True).start()
with mouse.Listener(on_click=on_click) as ml, keyboard.Listener(on_press=on_press) as kl:
    kl.join(); ml.join()
