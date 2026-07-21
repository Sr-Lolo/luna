import ctypes
import time
import uuid as _uuid
from ctypes import wintypes
from .protocol import SliderCommand, SLIDER_VOLUME, SLIDER_BRIGHTNESS, SLIDER_SCROLL_V, SLIDER_SCROLL_H

PUL = ctypes.POINTER(ctypes.c_ulong)


class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", wintypes.BYTE * 8),
    ]


def _guid(s: str) -> GUID:
    parts = _uuid.UUID(s).fields
    arr = (wintypes.BYTE * 8)(*_uuid.UUID(s).bytes[8:16])
    return GUID(parts[0], parts[1], parts[2], arr)


CLSID_MMDeviceEnumerator = _guid("{BCDE0395-E52F-467C-8E3D-C4579291692E}")
IID_IMMDeviceEnumerator = _guid("{A95664D2-9614-4F35-A746-DE8DB63617E6}")
IID_IAudioEndpointVolume = _guid("{5CDF2C82-841E-4546-9722-0CF74078229A}")

_ole32 = ctypes.windll.ole32
_ole32.CoInitializeEx.argtypes = [ctypes.c_void_p, wintypes.DWORD]
_ole32.CoInitializeEx.restype = wintypes.LONG
_ole32.CoCreateInstance.argtypes = [ctypes.POINTER(GUID), ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_void_p)]
_ole32.CoCreateInstance.restype = wintypes.LONG


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", PUL),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("u", INPUT_UNION),
    ]


INPUT_MOUSE = 0
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_HWHEEL = 0x1000

_send_input = ctypes.windll.user32.SendInput
_send_input.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
_send_input.restype = wintypes.UINT


def _send_wheel(delta: int, horizontal: bool = False):
    if delta == 0:
        return
    flag = MOUSEEVENTF_HWHEEL if horizontal else MOUSEEVENTF_WHEEL
    mi = MOUSEINPUT(0, 0, delta, flag, 0, None)
    inp = INPUT(INPUT_MOUSE, INPUT_UNION(mi=mi))
    _send_input(1, ctypes.pointer(inp), ctypes.sizeof(inp))


def _vtable(iface: ctypes.c_void_p, idx: int, restype, *argtypes):
    vtbl = ctypes.c_void_p.from_address(iface.value).value
    addr = ctypes.c_void_p.from_address(vtbl + idx * ctypes.sizeof(ctypes.c_void_p)).value
    fn = ctypes.CFUNCTYPE(restype, ctypes.c_void_p, *argtypes)(addr)
    return fn


_brightness_ready = False
_brightness_set = None
_last_brightness_time = 0
_volume_com_initialized = False


def _ensure_volume_com():
    global _volume_com_initialized
    if not _volume_com_initialized:
        _ole32.CoInitializeEx(None, 0)
        _volume_com_initialized = True


def _init_brightness():
    global _brightness_ready, _brightness_set
    if _brightness_ready:
        return True
    try:
        import screen_brightness_control as sbc
        _brightness_set = sbc.set_brightness
        _brightness_ready = True
        return True
    except Exception:
        return False


def execute(cmd: SliderCommand) -> bool:
    if cmd.slider_id == SLIDER_VOLUME:
        return _set_volume(cmd.value)
    elif cmd.slider_id == SLIDER_BRIGHTNESS:
        return _set_brightness(cmd.value)
    elif cmd.slider_id == SLIDER_SCROLL_V:
        return _scroll_vertical(cmd.value)
    elif cmd.slider_id == SLIDER_SCROLL_H:
        return _scroll_horizontal(cmd.value)
    return False


def _set_volume(value: int) -> bool:
    try:
        _ensure_volume_com()
        pEnum = ctypes.c_void_p(0)
        hr = _ole32.CoCreateInstance(ctypes.byref(CLSID_MMDeviceEnumerator), None, 1, ctypes.byref(IID_IMMDeviceEnumerator), ctypes.byref(pEnum))
        if hr != 0:
            return False
        pDev = ctypes.c_void_p(0)
        get_def = _vtable(pEnum, 4, wintypes.LONG, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(ctypes.c_void_p))
        hr = get_def(pEnum.value, 0, 0, ctypes.byref(pDev))
        rel = _vtable(pEnum, 2, wintypes.LONG)
        rel(pEnum.value)
        if hr != 0:
            return False
        pVol = ctypes.c_void_p(0)
        act = _vtable(pDev, 3, wintypes.LONG, ctypes.POINTER(GUID), wintypes.DWORD, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))
        hr = act(pDev.value, ctypes.byref(IID_IAudioEndpointVolume), 0, None, ctypes.byref(pVol))
        rel(pDev.value)
        if hr != 0:
            return False
        pct = max(0.0, min(1.0, value / 255.0))
        set_vol = _vtable(pVol, 7, wintypes.LONG, ctypes.c_float, ctypes.c_void_p)
        hr = set_vol(pVol.value, ctypes.c_float(pct), None)
        rel(pVol.value)
        return hr == 0
    except Exception:
        return False


def _set_brightness(value: int) -> bool:
    global _last_brightness_time
    now = time.time()
    if now - _last_brightness_time < 0.2:
        return True
    _last_brightness_time = now
    if not _init_brightness():
        return False
    try:
        pct = max(0, min(100, round(value / 255.0 * 100)))
        _brightness_set(pct)
        return True
    except Exception:
        return False


def _scroll_vertical(value: int) -> bool:
    delta = value - 128
    if delta == 0:
        return True
    amount = delta * 10
    _send_wheel(amount, horizontal=False)
    return True


def _scroll_horizontal(value: int) -> bool:
    delta = value - 128
    if delta == 0:
        return True
    amount = delta * 10
    _send_wheel(amount, horizontal=True)
    return True
