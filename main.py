import time, random, threading, numpy as np, ctypes, os, json
from PIL import ImageGrab
from pynput import mouse, keyboard

# --- AUTO ADMIN PRIVILEGE ---
def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", os.sys.executable, " ".join(os.sys.argv), None, 1)
    os._exit(0)

# --- CONFIGURATION ---
# Kamu bisa ubah angka di sini sebelum di-build
CFG = {
    "SMOOTHING": 0.45,     # Kecepatan flick (0.1 - 1.0)
    "FOV": 50,             # Area deteksi (pixel)
    "TOLERANCE": 45,       # Toleransi kemiripan warna
    "HEAD_OFFSET": 6,      # Agar bidikan lebih ke atas kepala
    "RECOIL_AMOUNT": 16,   # Kekuatan tarikan recoil ke bawah
}

class FlickBot:
    def __init__(self):
        self.is_holding = False
        self.has_flicked = False
        # Resolusi layar otomatis
        self.cx = ctypes.windll.user32.GetSystemMetrics(0) // 2
        self.cy = ctypes.windll.user32.GetSystemMetrics(1) // 2

    def force_move(self, x, y):
        # Menggunakan MOUSEEVENTF_MOVE (0x0001) lewat ctypes agar lebih tembus
        ctypes.windll.user32.mouse_event(0x0001, int(x), int(y), 0, 0)

    def scan_and_flick(self):
        f = CFG["FOV"]
        bbox = (self.cx - f, self.cy - f, self.cx + f, self.cy + f)
        
        # Grab screen
        img = ImageGrab.grab(bbox=bbox)
        px = np.array(img)
        
        # Cari warna Ungu/Pink (RGB: 250, 100, 250)
        # Scan tiap 2 pixel agar lebih ringan/cepat
        for y in range(0, len(px), 2):
            for x in range(0, len(px[y]), 2):
                r, g, b = px[y][x]
                if abs(r - 250) < CFG["TOLERANCE"] and abs(g - 100) < CFG["TOLERANCE"] and abs(b - 250) < CFG["TOLERANCE"]:
                    # Hitung jarak dari tengah
                    mx = (x + (self.cx - f) - self.cx) * CFG["SMOOTHING"]
                    my = (y + (self.cy - f) - CFG["HEAD_OFFSET"] - self.cy) * CFG["SMOOTHING"]
                    
                    # 1. Flick ke target
                    self.force_move(mx, my)
                    
                    # 2. Delay peluru pertama & Recoil
                    time.sleep(random.uniform(0.02, 0.04))
                    recoil = CFG["RECOIL_AMOUNT"] + random.randint(-2, 3)
                    self.force_move(0, recoil)
                    
                    return True
        return False

    def loop(self):
        while True:
            if self.is_holding and not self.has_flicked:
                if self.scan_and_flick():
                    self.has_flicked = True
            elif not self.is_holding:
                self.has_flicked = False
            time.sleep(0.001)

bot = FlickBot()

def on_click(x, y, button, pressed):
    if button == mouse.Button.left:
        bot.is_holding = pressed

def on_press(key):
    if key == keyboard.Key.delete: # Tekan tombol DELETE untuk tutup
        os._exit(0)

# Jalankan Background Threads
threading.Thread(target=bot.loop, daemon=True).start()

# Mouse & Keyboard Listener
with mouse.Listener(on_click=on_click) as ml, keyboard.Listener(on_press=on_press) as kl:
    kl.join(); ml.join()
