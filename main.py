# Tambahkan ini di CONFIG atau config.json
# "RECOIL_AMOUNT": 15 (berapa pixel mouse turun setelah flick)

class FlickBot:
    def __init__(self):
        self.is_holding, self.running = False, True
        self.has_flicked = False
        self.cx, self.cy = 960, 540 

    def flick(self, tx, ty):
        mx = int((tx - self.cx) * CONFIG["SMOOTHING"])
        my = int((ty - self.cy) * CONFIG["SMOOTHING"])
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, mx, my, 0, 0)

    def main_loop(self):
        while self.running:
            if self.is_holding:
                if not self.has_flicked:
                    target = self.scan_for_head()
                    if target:
                        # 1. Flick ke target
                        self.flick(target[0], target[1])
                        
                        # 2. Delay sangat singkat agar peluru keluar dulu
                        time.sleep(0.02) 
                        
                        # 3. Recoil Control (Mouse ditarik ke bawah)
                        recoil = CONFIG.get("RECOIL_AMOUNT", 15)
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, recoil, 0, 0)
                        
                        self.has_flicked = True 
            else:
                self.has_flicked = False
            
            time.sleep(0.001)
