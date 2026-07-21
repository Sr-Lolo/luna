import ctypes
import time
import threading

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


class WindowTracker:
    def __init__(self, get_config_fn):
        self.get_config_fn = get_config_fn
        self.active_profile = None
        self.last_exe = ""
        self._thread = None
        self._running = False
        self._paused = False

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def pause(self):
        self._paused = True
        self.active_profile = None
        self.last_exe = ""

    def resume(self):
        self._paused = False

    def _get_foreground_pid(self):
        hwnd = user32.GetForegroundWindow()
        pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        return pid.value

    def _run(self):
        last_pid = 0
        while self._running:
            time.sleep(0.5)
            if self._paused:
                last_pid = 0
                continue
            config = self.get_config_fn()
            ap = config.get("appSwitch", {})
            if not ap.get("enabled", False):
                self.active_profile = None
                self.last_exe = ""
                last_pid = 0
                continue
            rules = ap.get("rules", [])
            if not rules:
                continue
            pid = self._get_foreground_pid()
            if not pid or pid == last_pid:
                continue
            last_pid = pid
            try:
                import psutil
                proc = psutil.Process(pid)
                exe_name = proc.name().lower()
            except Exception:
                continue
            found = None
            for rule in rules:
                if rule.get("exe", "").lower() == exe_name:
                    found = rule["profile"]
                    break
            if found != self.active_profile:
                self.active_profile = found
                self.last_exe = exe_name
