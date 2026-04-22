import time, random, threading, numpy as np, ctypes, os, win32api, win32con, json
from PIL import ImageGrab
from pynput import mouse, keyboard

# Sembunyikan Jendela
hWnd = ctypes.WinDLL('kernel32').GetConsoleWindow()
if hWnd: ctypes.WinDLL('user32').ShowWindow(hWnd, 0)

# Default Config (Akan dibuat otomatis jika file json tidak ada)
DEFAULT_CONFIG = {
    "SMOOTHING": 0.15,
    "AIM_FOV": 35,
    "TOLERANCE": 35,
    "HEAD_OFFSET": 6,
    "HOLD_KEY": "left"
}

def load_config():
    if not os.path.exists('config.json'):
        with open('config.json', 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG
    with open('config.json', 'r') as f:
        return json.load(f)

CONFIG = load_config()

class FlickBot:
    def __init__(self):
        self.is_holding, self.running = False, True
        self.cx, self.cy = 960, 540 # Center 1920x1080

    def scan_for_head(self):
        f = CONFIG["AIM_FOV"]
        bbox = (self.cx - f, self.cy - f, self.cx + f, self.cy + f)
        img = ImageGrab.grab(bbox=bbox)
        px = np.array(img)
        target, tol = (250, 100, 250), CONFIG["TOLERANCE"]
        
        for y in range(0, len(px), 2):
            for x in range(0, len(px[y]), 2):
                r, g, b = px[y][x]
                if abs(r - target[0]) < tol and abs(g - target[1]) < tol and abs(b - target[2]) < tol:
                    return (x + (self.cx - f), y + (self.cy - f) - CONFIG["HEAD_OFFSET"])
        return None

    def flick(self, tx, ty):
        mx = int((tx - self.cx) * CONFIG["SMOOTHING"])
        my = int((ty - self.cy) * CONFIG["SMOOTHING"])
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, mx, my, 0, 0)

    def main_loop(self):
        while self.running:
            if self.is_holding:
                target = self.scan_for_head()
                if target:
                    self.flick(target[0], target[1])
                    time.sleep(0.01) 
            time.sleep(0.001)

bot = FlickBot()

def on_click(x, y, button, pressed):
    if button == mouse.Button.left: # Tetap klik kiri sesuai permintaan
        bot.is_holding = pressed

def on_press(key):
    if key == keyboard.Key.delete:
        os._exit(0)

threading.Thread(target=bot.main_loop, daemon=True).start()
with mouse.Listener(on_click=on_click) as ml, keyboard.Listener(on_press=on_press) as kl:
    kl.join(); ml.join()
    
