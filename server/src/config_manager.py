import os
import json
import sys
import copy

if getattr(sys, "frozen", False):
    HOST_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "SrLolo", "LunaDeck")
else:
    HOST_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(HOST_DIR, exist_ok=True)
CONFIG_PATH = os.path.join(HOST_DIR, "config.json")

_DEFAULT = {
    "version": 2,
    "perfil_activo": "default",
    "perfiles": {
        "default": {
            "cols": 4,
            "keys": [
                {"label": "L", "keyCode": 76, "mods": 0},
                {"label": "Z", "keyCode": 90, "mods": 0},
                {"label": "Ctrl+C", "keyCode": 67, "mods": 1},
                {"label": "Ctrl+V", "keyCode": 86, "mods": 1},
                {"label": "W", "keyCode": 87, "mods": 0},
                {"label": "A", "keyCode": 65, "mods": 0},
                {"label": "S", "keyCode": 83, "mods": 0},
                {"label": "D", "keyCode": 68, "mods": 0},
                {"label": "\u232B", "keyCode": 8, "mods": 0},
                {"label": "\u23CE", "keyCode": 13, "mods": 0},
                {"label": "\u238B", "keyCode": 27, "mods": 0},
                {"label": "\u21E7", "keyCode": 16, "mods": 0},
                {"label": "\u25C1", "keyCode": 37, "mods": 0},
                {"label": "\u25B2", "keyCode": 38, "mods": 0},
                {"label": "\u25BC", "keyCode": 40, "mods": 0},
                {"label": "\u25B7", "keyCode": 39, "mods": 0},
            ]
        },
        "editing": {
            "cols": 4,
            "keys": [
                {"label": "Ctrl+Z", "keyCode": 90, "mods": 1},
                {"label": "Ctrl+X", "keyCode": 88, "mods": 1},
                {"label": "Ctrl+C", "keyCode": 67, "mods": 1},
                {"label": "Ctrl+V", "keyCode": 86, "mods": 1},
                {"label": "Ctrl+S", "keyCode": 83, "mods": 1},
                {"label": "Ctrl+A", "keyCode": 65, "mods": 1},
                {"label": "Ctrl+F", "keyCode": 70, "mods": 1},
                {"label": "Ctrl+D", "keyCode": 68, "mods": 1},
                {"label": "\u232B", "keyCode": 8, "mods": 0},
                {"label": "\u23CE", "keyCode": 13, "mods": 0},
                {"label": "\u238B", "keyCode": 27, "mods": 0},
                {"label": "\u21E7", "keyCode": 16, "mods": 0},
                {"label": "\u25C1", "keyCode": 37, "mods": 0},
                {"label": "\u25B2", "keyCode": 38, "mods": 0},
                {"label": "\u25BC", "keyCode": 40, "mods": 0},
                {"label": "\u25B7", "keyCode": 39, "mods": 0},
            ]
        },
        "streaming": {
            "cols": 4,
            "keys": [
                {"label": "PTT", "keyCode": 124, "mods": 0},
                {"label": "MicSil", "keyCode": 125, "mods": 0},
                {"label": "Vol+", "keyCode": 175, "mods": 0},
                {"label": "Vol-", "keyCode": 174, "mods": 0},
                {"label": "obs1", "keyCode": 126, "mods": 0},
                {"label": "obs2", "keyCode": 127, "mods": 0},
                {"label": "obs3", "keyCode": 128, "mods": 0},
                {"label": "obs4", "keyCode": 129, "mods": 0},
                {"label": "Str On", "keyCode": 130, "mods": 0},
                {"label": "Str Off", "keyCode": 131, "mods": 0},
                {"label": "Rec On", "keyCode": 132, "mods": 0},
                {"label": "Rec Off", "keyCode": 133, "mods": 0},
                {"label": "Silen", "keyCode": 173, "mods": 0},
                {"label": "P/P", "keyCode": 179, "mods": 0},
                {"label": "Next", "keyCode": 176, "mods": 0},
                {"label": "Prev", "keyCode": 177, "mods": 0},
            ]
        },
        "navigation": {
            "cols": 4,
            "keys": [
                {"label": "+Pest", "keyCode": 84, "mods": 1},
                {"label": "Cerrar", "keyCode": 87, "mods": 1},
                {"label": "Sig", "keyCode": 9, "mods": 1},
                {"label": "Ant", "keyCode": 9, "mods": 3},
                {"label": "URL", "keyCode": 76, "mods": 1},
                {"label": "Recarg", "keyCode": 82, "mods": 1},
                {"label": "Atr\u00E1s", "keyCode": 37, "mods": 4},
                {"label": "Adel", "keyCode": 39, "mods": 4},
                {"label": "Reabrir", "keyCode": 84, "mods": 3},
                {"label": "Fav", "keyCode": 68, "mods": 1},
                {"label": "Desc", "keyCode": 74, "mods": 1},
                {"label": "Hist", "keyCode": 72, "mods": 1},
                {"label": "Buscar", "keyCode": 70, "mods": 1},
                {"label": "F5", "keyCode": 116, "mods": 0},
                {"label": "F11", "keyCode": 122, "mods": 0},
                {"label": "Esc", "keyCode": 27, "mods": 0},
            ]
        },
        "media": {
            "cols": 4,
            "keys": [
                {"label": "\u23EF", "keyCode": 32, "mods": 0},
                {"label": "\u23ED", "keyCode": 39, "mods": 1},
                {"label": "\u23EE", "keyCode": 37, "mods": 1},
                {"label": "Vol\u2191", "keyCode": 38, "mods": 0},
                {"label": "Vol\u2193", "keyCode": 40, "mods": 0},
                {"label": "Mute", "keyCode": 77, "mods": 0},
                {"label": "F11", "keyCode": 122, "mods": 0},
                {"label": "Esc", "keyCode": 27, "mods": 0},
                {"label": "S", "keyCode": 83, "mods": 0},
                {"label": "L", "keyCode": 76, "mods": 0},
                {"label": "R", "keyCode": 82, "mods": 0},
                {"label": "T", "keyCode": 84, "mods": 0},
                {"label": "---", "keyCode": 0, "mods": 0},
                {"label": "---", "keyCode": 0, "mods": 0},
                {"label": "---", "keyCode": 0, "mods": 0},
                {"label": "---", "keyCode": 0, "mods": 0},
            ]
        },
        "numpad": {
            "cols": 4,
            "keys": [
                {"label": "7", "keyCode": 103, "mods": 0},
                {"label": "8", "keyCode": 104, "mods": 0},
                {"label": "9", "keyCode": 105, "mods": 0},
                {"label": "\u00F7", "keyCode": 111, "mods": 0},
                {"label": "4", "keyCode": 100, "mods": 0},
                {"label": "5", "keyCode": 101, "mods": 0},
                {"label": "6", "keyCode": 102, "mods": 0},
                {"label": "\u00D7", "keyCode": 106, "mods": 0},
                {"label": "1", "keyCode": 97, "mods": 0},
                {"label": "2", "keyCode": 98, "mods": 0},
                {"label": "3", "keyCode": 99, "mods": 0},
                {"label": "\u2212", "keyCode": 109, "mods": 0},
                {"label": "0", "keyCode": 96, "mods": 0},
                {"label": ".", "keyCode": 110, "mods": 0},
                {"label": "+", "keyCode": 107, "mods": 0},
                {"label": "\u23CE", "keyCode": 13, "mods": 0},
            ]
        }
    },
    "appSwitch": {
        "enabled": True,
        "rules": []
    },
    "pro_license": False,
    "store_addon_id": "9PNCV2XSK9K8",
    "themes": {
        "pc": {
            "bg": "#0D0D0D",
            "bg_surface": "#1A1A1A",
            "bg_elevated": "#1E1E1E",
            "border": "#2A2A2A",
            "border_light": "#333333",
            "text": "#E0E0E0",
            "text_strong": "#FFFFFF",
            "text_muted": "#888888",
            "text_dim": "#666666",
            "accent": "#4FC3F7",
            "danger": "#F44336",
            "success": "#4CAF50"
        },
        "mobile": {
            "bg_primary": "#0D0D0D",
            "bg_surface": "#1A1A1A",
            "text_primary": "#FFFFFF",
            "text_secondary": "#E0E0E0",
            "accent": "#4FC3F7",
            "accent_dark": "#0288D1",
            "chip_bg": "#2A2A2A",
            "chip_bg_active": "#4FC3F7",
            "chip_text": "#FFFFFF",
            "chip_text_active": "#000000",
            "slider_track": "#2A2A2A",
            "slider_thumb": "#4FC3F7",
            "scroll_pad_bg": "#1A1A1A",
            "scroll_pad_thumb": "#4FC3F7",
            "scroll_pad_track": "#2A2A2A",
            "scroll_pad_arrow": "#888888",
            "grid_btn_bg": "#2A2A2A",
            "grid_btn_text": "#FFFFFF",
            "grid_btn_border": "#3A3A3A",
            "grid_btn_active_bg": "#4FC3F7",
            "rgb": {
                "enabled": False,
                "mode": "rainbow",
                "speed": 1.0,
                "accent_only": False,
                "static_color": "#FF0000"
            }
        }
    }
}


def load() -> dict:
    if not os.path.isfile(CONFIG_PATH):
        save(copy.deepcopy(_DEFAULT))
        return copy.deepcopy(_DEFAULT)
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("formato invalido")
        if "perfiles" not in data:
            if "profiles" in data:
                data["perfiles"] = data.pop("profiles")
            else:
                data["perfiles"] = {}
        if not data["perfiles"]:
            data["perfiles"] = dict(_DEFAULT["perfiles"])
        for nombre, teclas in _DEFAULT["perfiles"].items():
            if nombre not in data["perfiles"]:
                data["perfiles"][nombre] = teclas
        for p in data["perfiles"].values():
            if "cols" not in p:
                p["cols"] = 4
            if not isinstance(p.get("keys"), list):
                p["keys"] = []
        if "appSwitch" not in data or not isinstance(data["appSwitch"], dict):
            data["appSwitch"] = dict(_DEFAULT["appSwitch"])
        if "autoSwitch" in data:
            old = data.pop("autoSwitch")
            if "appSwitch" not in data or not data["appSwitch"].get("rules"):
                data["appSwitch"] = {"enabled": True, "rules": []}
        if "perfil_activo" not in data:
            if "activeProfile" in data:
                data["perfil_activo"] = data.pop("activeProfile")
            else:
                data["perfil_activo"] = "default"
        if data["perfil_activo"] not in data["perfiles"]:
            data["perfil_activo"] = list(data["perfiles"].keys())[0] if data["perfiles"] else "default"
        if "version" not in data:
            data["version"] = _DEFAULT["version"]
        if "themes" not in data or not isinstance(data["themes"], dict):
            data["themes"] = dict(_DEFAULT["themes"])
        for theme_key in _DEFAULT["themes"]:
            if theme_key not in data["themes"] or not isinstance(data["themes"][theme_key], dict):
                data["themes"][theme_key] = dict(_DEFAULT["themes"][theme_key])
            for color_key in _DEFAULT["themes"][theme_key]:
                if color_key not in data["themes"][theme_key]:
                    data["themes"][theme_key][color_key] = _DEFAULT["themes"][theme_key][color_key]
        return data
    except Exception:
        save(copy.deepcopy(_DEFAULT))
        return copy.deepcopy(_DEFAULT)


def save(data: dict) -> bool:
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def merge_save(perfil_activo: str, datos_perfil: dict) -> bool:
    try:
        ruta = CONFIG_PATH
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                try:
                    config = json.load(f)
                except json.JSONDecodeError:
                    config = {"perfil_activo": "", "perfiles": {}}
        else:
            config = {"perfil_activo": "", "perfiles": {}}
        if "perfiles" not in config:
            config["perfiles"] = {}
        config["perfiles"][perfil_activo] = datos_perfil
        config["perfil_activo"] = perfil_activo
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[Luna] merge_save error: {e}")
        return False


def delete_profile(perfil: str) -> bool:
    try:
        ruta = CONFIG_PATH
        if not os.path.exists(ruta):
            return False
        with open(ruta, "r", encoding="utf-8") as f:
            config = json.load(f)
        if perfil not in config.get("perfiles", {}):
            return False
        del config["perfiles"][perfil]
        if config.get("perfil_activo") == perfil:
            config["perfil_activo"] = "default"
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False


def get_default() -> dict:
    return copy.deepcopy(_DEFAULT)
