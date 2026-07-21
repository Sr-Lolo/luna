from dataclasses import dataclass

MSG_TYPE_KEY_ACTION = 0x01
MSG_TYPE_SLIDER = 0x02

ACTION_TAP = 0x03
ACTION_PRESS = 0x01
ACTION_RELEASE = 0x02

MOD_NONE = 0x00
MOD_CTRL = 0x01
MOD_SHIFT = 0x02
MOD_ALT = 0x04
MOD_WIN = 0x08

MODIFIER_MAP = {
    MOD_NONE: "",
    MOD_CTRL: "ctrl",
    MOD_SHIFT: "shift",
    MOD_ALT: "alt",
    MOD_WIN: "win",
    MOD_CTRL | MOD_SHIFT: "ctrl+shift",
    MOD_CTRL | MOD_ALT: "ctrl+alt",
    MOD_CTRL | MOD_SHIFT | MOD_ALT: "ctrl+shift+alt",
}

SPECIAL_KEY_NAMES = {
    0x08: "backspace",
    0x09: "tab",
    0x0D: "enter",
    0x1B: "escape",
    0x10: "shift",
    0x13: "pause",
    0x14: "caps lock",
    0x20: "space",
    0x21: "page up",
    0x22: "page down",
    0x23: "end",
    0x24: "home",
    0x25: "left",
    0x26: "up",
    0x27: "right",
    0x28: "down",
    0x2C: "print screen",
    0x2D: "insert",
    0x2E: "delete",
    0x5B: "left windows",
    0x5C: "right windows",
    0x60: "num 0",  0x61: "num 1",  0x62: "num 2",  0x63: "num 3",
    0x64: "num 4",  0x65: "num 5",  0x66: "num 6",  0x67: "num 7",
    0x68: "num 8",  0x69: "num 9",
    0x6A: "num multiply",
    0x6B: "num add",
    0x6D: "subtract",
    0x6E: "decimal",
    0x6F: "num divide",
    0x70: "f1",   0x71: "f2",   0x72: "f3",   0x73: "f4",
    0x74: "f5",   0x75: "f6",   0x76: "f7",   0x77: "f8",
    0x78: "f9",   0x79: "f10",  0x7A: "f11",  0x7B: "f12",
    0x7C: "f13",  0x7D: "f14",  0x7E: "f15",  0x7F: "f16",
    0x80: "f17",  0x81: "f18",  0x82: "f19",  0x83: "f20",
    0x84: "f21",  0x85: "f22",  0x86: "f23",  0x87: "f24",
    0x90: "num lock",
    0x91: "scroll lock",
    0xAD: "volume mute",
    0xAE: "volume down",
    0xAF: "volume up",
    0xB0: "next track",
    0xB1: "previous track",
    0xB2: "stop media",
    0xB3: "play/pause media",
}

SLIDER_VOLUME = 0x01
SLIDER_BRIGHTNESS = 0x02
SLIDER_SCROLL_V = 0x03
SLIDER_SCROLL_H = 0x04

SLIDER_NAMES = {
    SLIDER_VOLUME: "volumen",
    SLIDER_BRIGHTNESS: "brillo",
    SLIDER_SCROLL_V: "scroll V",
    SLIDER_SCROLL_H: "scroll H",
}


@dataclass
class KeyCommand:
    action: int
    modifiers: int
    key: str
    key_code: int = 0


@dataclass
class SliderCommand:
    slider_id: int
    value: int


def _checksum(*args: int) -> int:
    result = 0
    for a in args:
        result ^= a
    return result


def pack_key_command(action: int, modifiers: int, key: str) -> bytes:
    key_code = ord(key.upper())
    cksum = _checksum(MSG_TYPE_KEY_ACTION, action, modifiers, key_code)
    return bytes([MSG_TYPE_KEY_ACTION, action, modifiers, key_code, cksum])


def pack_slider(slider_id: int, value: int) -> bytes:
    cksum = _checksum(MSG_TYPE_SLIDER, slider_id, value, 0x00)
    return bytes([MSG_TYPE_SLIDER, slider_id, value, 0x00, cksum])


def _unpack_key(data: bytes) -> KeyCommand | None:
    _, action, modifiers, key_code, cksum = data
    if cksum != _checksum(MSG_TYPE_KEY_ACTION, action, modifiers, key_code):
        return None
    key_name = SPECIAL_KEY_NAMES.get(key_code, chr(key_code).lower())
    return KeyCommand(action=action, modifiers=modifiers, key=key_name, key_code=key_code)


def _unpack_slider(data: bytes) -> SliderCommand | None:
    _, slider_id, value, _, cksum = data
    if cksum != _checksum(MSG_TYPE_SLIDER, slider_id, value, 0x00):
        return None
    return SliderCommand(slider_id=slider_id, value=value)


def unpack(data: bytes) -> KeyCommand | SliderCommand | None:
    if len(data) != 5:
        return None
    msg_type = data[0]
    if msg_type == MSG_TYPE_KEY_ACTION:
        return _unpack_key(data)
    elif msg_type == MSG_TYPE_SLIDER:
        return _unpack_slider(data)
    return None
