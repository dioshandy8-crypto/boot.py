import time, random, threading, numpy as np, ctypes, os, win32api, win32con
from PIL import ImageGrab
from pynput import mouse, keyboard

# Sembunyikan Jendela CMD (Invisible)
hWnd = ctypes.WinDLL('kernel32').GetConsoleWindow()
if hWnd: ctypes.WinDLL('user32').ShowWindow(hWnd, 0)

CONFIG = {
    "TARGET_COLOR": (250, 100, 250), # Purple Tritanopia
    "TOLERANCE": 30,
    "AIM_FOV": 40,
    "SMOOTHING": 0.4,
    "HOLD_KEY": mouse.Button.x1, # Tombol Mouse 4
    "QUIT_KEY": keyboard.Key.delete,
    "RECOIL_PULL": 2
}

class ZenswareClone:
    def __init__(self):
        self.is_holding, self.running = False, True
        self.cx = win32api.GetSystemMetrics(0) // 2
        self.cy = win32api.GetSystemMetrics(1) // 2

    def scan(self):
        f = CONFIG["AIM_FOV"]
        bbox = (self.cx - f, self.cy - f, self.cx + f, self.cy + f)
        img = ImageGrab.grab(bbox=bbox)
        px = np.array(img)
        target, tol = CONFIG["TARGET_COLOR"], CONFIG["TOLERANCE"]
        for y in range(0, len(px), 2):
            for x in range(0, len(px[y]), 2):
                r, g, b = px[y][x]
                if abs(r - target[0]) < tol and abs(g - target[1]) < tol and abs(b - target[2]) < tol:
                    return (x + (self.cx - f), y + (self.cy - f))
        return None

    def action(self, tx, ty):
        mx = int((tx - self.cx) * CONFIG["SMOOTHING"])
        my = int((ty - self.cy) * CONFIG["SMOOTHING"])
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, mx, my + CONFIG["RECOIL_PULL"], 0, 0)
        dist = np.sqrt((tx - self.cx)**2 + (ty - self.cy)**2)
        if dist < 12:
            time.sleep(random.uniform(0.05, 0.1))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    def main_loop(self):
        while self.running:
            if self.is_holding:
                target = self.scan()
                if target: self.action(target[0], target[1])
            time.sleep(0.001)

bot = ZenswareClone()
def on_click(x, y, button, pressed):
    if button == CONFIG["HOLD_KEY"]: bot.is_holding = pressed
def on_press(key):
    if key == CONFIG["QUIT_KEY"]: os._exit(0)

threading.Thread(target=bot.main_loop, daemon=True).start()
with mouse.Listener(on_click=on_click) as ml, keyboard.Listener(on_press=on_press) as kl:
    kl.join(); ml.join()
                           
