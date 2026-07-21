import sys
import os
import threading
import time
import ctypes
import ctypes.wintypes
import tempfile
import atexit
import json

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── PID lock file con detecci├│n de stale ──
_LOCK_PATH = os.path.join(tempfile.gettempdir(), "luna.lock")
_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
_kernel32.QueryFullProcessImageNameW.argtypes = [
    ctypes.wintypes.HANDLE,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.LPWSTR,
    ctypes.POINTER(ctypes.wintypes.DWORD),
]
_kernel32.QueryFullProcessImageNameW.restype = ctypes.wintypes.BOOL

def _is_luna_process(handle):
    try:
        buf = ctypes.create_unicode_buffer(260)
        size = ctypes.c_uint32(260)
        if _kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size)):
            return "luna" in buf.value.lower()
    except:
        pass
    return False

def _take_lock():
    if os.environ.get("LUNA_PARENT_INSTANCE"):
        return False
    if os.path.exists(_LOCK_PATH):
        try:
            with open(_LOCK_PATH) as f:
                pid = int(f.read().strip())
            handle = _kernel32.OpenProcess(0x1000, False, pid)
            if handle:
                if _is_luna_process(handle):
                    _kernel32.CloseHandle(handle)
                    return True
                _kernel32.CloseHandle(handle)
        except (ValueError, OSError):
            pass
        try:
            os.unlink(_LOCK_PATH)
        except OSError:
            pass
    with open(_LOCK_PATH, "w") as f:
        f.write(str(os.getpid()))
    os.environ["LUNA_PARENT_INSTANCE"] = "1"
    return None

_lock_result = _take_lock()
if _lock_result is True:
    sys.exit(0)

if _lock_result is None:
    @atexit.register
    def _cleanup_lock():
        try:
            os.unlink(_LOCK_PATH)
        except Exception:
            pass


_server_failed = threading.Event()
_server_error_msg = ""
_api_instance = None


def _build_welcome_html():
    lang_dir = os.path.join(BASE_DIR, "web", "lang")
    trans = {}
    for lang in ("en", "es", "pt"):
        path = os.path.join(lang_dir, f"{lang}.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                trans[lang] = json.load(f)
        except Exception:
            trans[lang] = {}
    trans_json = json.dumps(trans, ensure_ascii=False)
    trans_escaped = trans_json.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n').replace('\r', '\\r')

    tmpl_path = os.path.join(BASE_DIR, "web", "welcome_template.html")
    with open(tmpl_path, "r", encoding="utf-8") as f:
        html = f.read()
    html = html.replace("{trans_escaped}", trans_escaped)
    return html


# ── Generate the welcome HTML once at module level ──
WELCOME_HTML = _build_welcome_html()
WELCOME_CLEAN = WELCOME_HTML.replace('__ERROR_MSG__', '') if '__ERROR_MSG__' in WELCOME_HTML else WELCOME_HTML


# ── Tray icon (win32gui) ──
_WM_TRAYICON = 0x0400 + 100  # WM_USER + 100


def _get_icon_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'app.ico')
    return os.path.join(BASE_DIR, 'app.ico')


class LunaApi:
    def __init__(self):
        self._window = None
        self._force_close = False
        self._close_pending = False
        self._tray_hwnd = None
        self._tray_hIcon = None
        self._tray_icon_loaded = False
        self._tray_ready = threading.Event()

    def set_window(self, w):
        self._window = w

    # ── JS API ──

    def is_close_pending(self):
        return self._close_pending

    def clear_close_pending(self):
        self._close_pending = False

    def close_completly(self):
        self._force_close = True
        self._close_pending = False
        self._remove_tray_icon()
        if self._window:
            hwnd = self._window.native.Handle.ToInt32()
            ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)

    def hide_to_tray(self):
        self._close_pending = False
        self._create_tray_icon()
        if self._window:
            self._window.hide()

    def cancel_close(self):
        self._close_pending = False

    def signal_offline(self, msg):
        if self._window:
            escaped = msg.replace("\\", "\\\\").replace("'", "\\'").replace('"', '&quot;')
            try:
                self._window.evaluate_js(f'showServerError("{escaped}")')
            except Exception:
                pass

    def show_window(self):
        self._remove_tray_icon()
        if self._window:
            self._window.show()

    def retry_server(self):
        if self._window:
            self._window.load_url("http://127.0.0.1:9120/?_t=" + str(int(time.time())))

    # ── Tray icon ──

    def _create_tray_icon(self):
        if self._tray_icon_loaded:
            return
        self._tray_icon_loaded = True
        self._tray_ready.clear()
        t = threading.Thread(target=self._tray_loop, daemon=True)
        t.start()
        self._tray_ready.wait(timeout=0.5)

    def _tray_loop(self):
        import win32api
        import win32gui
        import win32con

        hinst = win32api.GetModuleHandle(None)

        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self._tray_wndproc
        wc.hInstance = hinst
        wc.lpszClassName = 'LunaTrayWindow'
        wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        class_atom = win32gui.RegisterClass(wc)

        hwnd = win32gui.CreateWindow(
            class_atom, 'LunaTray',
            win32con.WS_OVERLAPPEDWINDOW,
            0, 0, 0, 0,
            0, 0, hinst, None
        )
        self._tray_hwnd = hwnd

        icon_path = _get_icon_path()
        hIcon = win32gui.LoadImage(
            hinst, icon_path,
            win32con.IMAGE_ICON,
            32, 32,
            win32con.LR_LOADFROMFILE
        )
        self._tray_hIcon = hIcon

        nid = (hwnd, 0,
               win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP,
               _WM_TRAYICON, hIcon, "Luna")

        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
        self._tray_ready.set()
        win32gui.PumpMessages()

    def _tray_wndproc(self, hwnd, msg, wparam, lparam):
        import win32gui
        import win32con

        if msg == _WM_TRAYICON:
            if lparam == win32con.WM_LBUTTONUP:
                self.show_window()
            elif lparam == win32con.WM_RBUTTONUP:
                self._show_tray_menu(hwnd)
        elif msg == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def _show_tray_menu(self, hwnd):
        import win32gui
        import win32con

        menu = win32gui.CreatePopupMenu()
        win32gui.AppendMenu(menu, win32con.MF_STRING, 1, 'Mostrar')
        win32gui.AppendMenu(menu, win32con.MF_STRING, 2, 'Salir')
        pos = win32gui.GetCursorPos()
        cmd = win32gui.TrackPopupMenu(
            menu,
            win32con.TPM_RETURNCMD | win32con.TPM_NONOTIFY,
            pos[0], pos[1], 0, hwnd, None
        )
        win32gui.DestroyMenu(menu)
        if cmd == 1:
            self.show_window()
        elif cmd == 2:
            self.close_completly()

    def _remove_tray_icon(self):
        import win32gui
        import win32con

        if self._tray_hwnd and self._tray_hIcon:
            try:
                nid = (self._tray_hwnd, 0,
                       win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP,
                       _WM_TRAYICON, self._tray_hIcon, "Luna")
                win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
            except Exception:
                pass
        if self._tray_hIcon:
            try:
                win32gui.DestroyIcon(self._tray_hIcon)
            except Exception:
                pass
        if self._tray_hwnd:
            try:
                win32gui.PostMessage(self._tray_hwnd, win32con.WM_CLOSE, 0, 0)
            except Exception:
                pass
        self._tray_hwnd = None
        self._tray_hIcon = None
        self._tray_icon_loaded = False


# ── Run ──

def _get_window_hwnd(window):
    try:
        return window.native.Handle.ToInt32()
    except AttributeError:
        try:
            import System.Windows.Interop as Interop
            helper = Interop.WindowInteropHelper(window.native)
            return helper.Handle.ToInt32()
        except Exception:
            return None


def run():
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)

    global _api_instance
    import webview

    api = LunaApi()
    _api_instance = api

    threading.Thread(target=_start_server, args=(api,), daemon=True).start()

    welcome_file = os.path.join(tempfile.gettempdir(), "luna_welcome.html")
    try:
        with open(welcome_file, "w", encoding="utf-8") as f:
            f.write(WELCOME_CLEAN)
    except Exception:
        welcome_file = "about:blank"



    _window = webview.create_window(
        "\u2726 Luna",
        welcome_file,
        width=730,
        height=640,
        resizable=False,
        min_size=(730, 640),
        js_api=api,
    )
    api.set_window(_window)
    _window.events.closing += lambda: _on_closing(api)

    def on_shown():
        try:
            import win32gui
            import win32con
            import win32api
            import ctypes
            from ctypes import wintypes

            hwnd = _get_window_hwnd(_window)
            if hwnd:
                icon_path = _get_icon_path()
                hinst = win32api.GetModuleHandle(None)

                # Load small (16x16) icon for title bar
                hIconSmall = win32gui.LoadImage(
                    hinst, icon_path,
                    win32con.IMAGE_ICON,
                    16, 16,
                    win32con.LR_LOADFROMFILE
                )
                # Load big (32x32) icon for taskbar / alt-tab
                hIconBig = win32gui.LoadImage(
                    hinst, icon_path,
                    win32con.IMAGE_ICON,
                    32, 32,
                    win32con.LR_LOADFROMFILE
                )

                WM_SETICON = 0x0080
                ICON_SMALL = 0
                ICON_BIG = 1

                SendMessageW = ctypes.windll.user32.SendMessageW
                SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
                SendMessageW.restype = wintypes.LPARAM

                SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hIconSmall)
                SendMessageW(hwnd, WM_SETICON, ICON_BIG, hIconBig)
        except Exception as e:
            pass

    _window.events.shown += on_shown

    webview.start(private_mode=False, gui=None, debug=False, user_agent="LunaDesktop/1.0")


def _on_closing(api):
    if api._force_close:
        return True

    api._close_pending = True

    def _fallback_close():
        time.sleep(5.0)
        if api._close_pending and not api._force_close:
            api._force_close = True
            api._close_pending = False
            hwnd = api._window.native.Handle.ToInt32()
            ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)

    threading.Thread(target=_fallback_close, daemon=True).start()
    return False


def _start_server(api=None):
    global _server_error_msg
    try:
        from src.server import app
        import uvicorn
        from uvicorn import Config, Server
        config = Config(app, host="0.0.0.0", port=9120, log_level="warning")
        Server(config).run()
    except OSError as e:
        _server_error_msg = f"OSError: {e}"
        _server_failed.set()
        if api:
            api.signal_offline(_server_error_msg)
    except Exception as e:
        _server_error_msg = f"{type(e).__name__}: {e}"
        _server_failed.set()
        if api:
            api.signal_offline(_server_error_msg)


if __name__ == "__main__":
    run()
