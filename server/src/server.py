import os
import sys
import uuid
import socket
import time
import threading
import asyncio
import json
import random
import struct
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse, Response, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .protocol import unpack, KeyCommand, SliderCommand, ACTION_RELEASE
from .keyboard_engine import execute as execute_key
from .slider_engine import execute as execute_slider
from .config_manager import load as load_config, save as save_config, merge_save as merge_config, delete_profile as delete_config, get_default as default_config
from .window_tracker import WindowTracker
from . import license as license_module

APK_VERSION = "1.8.0"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_UI_DIR = os.path.join(BASE_DIR, "web")
AD_UI_DIR = os.path.join(BASE_DIR, "web_ad")

if getattr(sys, "frozen", False):
    DATA_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "SrLolo", "LunaDeck")
    PROJECT_ROOT = DATA_DIR
else:
    DATA_DIR = BASE_DIR
    PROJECT_ROOT = os.path.join(BASE_DIR, "..", "..")

if getattr(sys, "frozen", False):
    APK_PATH = os.path.join(BASE_DIR, "apk", "Luna.apk")
else:
    APK_PATH = os.path.join(os.path.dirname(BASE_DIR), "docs", "Luna.apk")

CUSTOM_ICONS_DIR = os.path.join(DATA_DIR, "custom_icons")
SOUNDS_DIR = os.path.join(DATA_DIR, "custom_sounds")
EXES_DIR = os.path.join(DATA_DIR, "custom_exes")
ICONS_ALL_DIR = os.path.join(PROJECT_ROOT, "Icons_All")

ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/gif"}
ALLOWED_AUDIO_TYPES = {"audio/wav", "audio/mpeg", "audio/x-wav", "audio/x-mpeg"}
MAX_FILE_SIZE = 5 * 1024 * 1024

os.makedirs(CUSTOM_ICONS_DIR, exist_ok=True)
os.makedirs(SOUNDS_DIR, exist_ok=True)
os.makedirs(EXES_DIR, exist_ok=True)

_NO_WINDOW = 0x08000000  # subprocess.CREATE_NO_WINDOW

def _try_add_rule(description: str, args: list):
    import subprocess
    try:
        r = subprocess.run(
            ["netsh", "advfirewall", "firewall", "add", "rule"] + args,
            capture_output=True, text=True, timeout=10,
            creationflags=_NO_WINDOW
        )
        out = (r.stderr + r.stdout).lower()
        if r.returncode == 0:
            print(f"[firewall] {description}: ok")
            return True
        if "already exists" in out:
            print(f"[firewall] {description}: ya existe")
            return True
        if "access denied" in out or "denied" in out:
            return False
        print(f"[firewall] {description}: {r.stderr.strip() or r.stdout.strip()}")
        return True
    except Exception as e:
        print(f"[firewall] {description}: {e}")
        return False


UDP_DISCOVERY_PORT = 53210

def _remove_legacy_rules():
    import subprocess
    for old in ["LunaDeck Port", "LunaDeck App", "LunaDeck Discovery UDP", "Block9120"]:
        try:
            subprocess.run(["netsh", "advfirewall", "firewall", "delete", "rule", f"name={old}"],
                         capture_output=True, timeout=5,
                         creationflags=_NO_WINDOW)
        except Exception:
            pass

def _add_firewall_rules():
    import subprocess, os, tempfile
    exe = sys.executable
    _remove_legacy_rules()
    rules = [
        ("TCP 9120", ["name=LunaDeck_Port", "dir=in", "action=allow", "protocol=TCP", "localport=9120", "profile=any"]),
        ("App EXE", ["name=LunaDeck_App", "dir=in", "action=allow", f"program={exe}", "profile=any"]),
        ("UDP Discovery", ["name=LunaDeck_Discovery_UDP", "dir=in", "action=allow", "protocol=UDP", f"localport={UDP_DISCOVERY_PORT}", "profile=any"]),
    ]
    need_elevation = False
    for desc, args in rules:
        if not _try_add_rule(desc, args):
            need_elevation = True
    if need_elevation:
        print("[firewall] algunas reglas requieren elevación, intentando...")
        _elevate_firewall_rules(rules)


def _elevate_firewall_rules(rules: list):
    import subprocess, os, tempfile
    try:
        lines = []
        for desc, args in rules:
            arg_str = " ".join(args)
            lines.append(f'netsh advfirewall firewall add rule {arg_str}')
        ps1 = '\n'.join(lines)
        script_path = os.path.join(tempfile.gettempdir(), "luna_fw.ps1")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(ps1)
        elevated_cmd = (
            f'Start-Process powershell -Verb RunAs '
            f'-ArgumentList \'-NoProfile -ExecutionPolicy Bypass -File "{script_path}"\' '
            f'-WindowStyle Hidden -Wait'
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", elevated_cmd],
            timeout=30,
            creationflags=_NO_WINDOW
        )
        print("[firewall] solicitud de elevación enviada")
    except Exception as e:
        print(f"[firewall] elevación falló: {e}")


def _set_network_private():
    """Cambia la red activa a Privada para evitar que Windows bloquee conexiones entrantes."""
    import subprocess
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-NetConnectionProfile | Set-NetConnectionProfile -NetworkCategory Private"],
            capture_output=True, text=True, timeout=15,
            creationflags=_NO_WINDOW
        )
        if r.returncode == 0:
            print("[firewall] Red cambiada a Privada")
        else:
            err = (r.stderr + r.stdout).strip()
            if err:
                print(f"[firewall] No se pudo cambiar red a Privada: {err}")
    except Exception as e:
        print(f"[firewall] Error al cambiar red: {e}")


_add_firewall_rules()
_set_network_private()

_zeroconf_registered = False
_zc_service_info = None
_zc_instance = None

_udp_server_running = False
_udp_thread: threading.Thread | None = None

# ── Pairing ──
_pairing_code: str | None = None
_pairing_code_expires: float = 0
_pairing_code_lock = threading.Lock()
PAIRING_CODE_TTL = 120  # 2 minutos
_paired_tokens: dict[str, dict] = {}  # token -> {"name": str, "ip": str, "since": float}
PC_UUID = uuid.uuid4().hex[:12]  # identificador unico del PC (persiste mientras el proceso viva)

# ── UDP Discovery ──

def _start_udp_discovery():
    """Hilo daemon: escucha broadcasts UDP en discovery_port, responde con info del servidor."""
    global _udp_server_running, _udp_thread
    if _udp_server_running:
        return
    _udp_server_running = True
    _udp_thread = threading.Thread(target=_udp_discovery_loop, daemon=True)
    _udp_thread.start()


def _udp_discovery_loop():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        sock.bind(("0.0.0.0", UDP_DISCOVERY_PORT))
        sock.settimeout(3.0)
    except Exception as e:
        log(f"[udp] No se pudo abrir puerto {UDP_DISCOVERY_PORT}: {e}")
        _udp_server_running = False
        return
    log(f"[udp] Discovery activo en puerto {UDP_DISCOVERY_PORT}")
    while _udp_server_running:
        try:
            data, addr = sock.recvfrom(1024)
            msg = data.decode("utf-8", errors="replace").strip()
            if msg == "LUNA_DISCOVER":
                ips = get_local_ips()
                name = socket.gethostname()
                needs_pairing = _get_pairing_code() is not None
                resp = json.dumps({
                    "type": "luna_server",
                    "ips": ips,
                    "port": 9120,
                    "name": name,
                    "needs_pairing": needs_pairing,
                })
                sock.sendto(resp.encode("utf-8"), addr)
        except socket.timeout:
            continue
        except Exception:
            continue
    try:
        sock.close()
    except Exception:
        pass


def _stop_udp_discovery():
    global _udp_server_running
    _udp_server_running = False


# ── Pairing ──

def _generate_pairing_code() -> str:
    global _pairing_code, _pairing_code_expires
    with _pairing_code_lock:
        _pairing_code = f"{random.randint(0, 999999):06d}"
        _pairing_code_expires = time.time() + PAIRING_CODE_TTL
        return _pairing_code


def _get_pairing_code() -> str | None:
    global _pairing_code, _pairing_code_expires
    with _pairing_code_lock:
        if _pairing_code is None or time.time() > _pairing_code_expires:
            _pairing_code = None
            return None
        return _pairing_code


def _verify_pairing_code(code: str) -> bool:
    actual = _get_pairing_code()
    if actual is None:
        return False
    return code.strip() == actual


def _generate_token() -> str:
    return uuid.uuid4().hex[:24]


@asynccontextmanager
async def lifespan(application: FastAPI):

    _start_udp_discovery()
    asyncio.create_task(_init_mdns_background(application))
    asyncio.create_task(_init_license_background())
    yield
    _stop_udp_discovery()
    global _zc_instance, _zeroconf_registered, _zc_service_info
    if _zeroconf_registered and _zc_instance is not None:
        try:
            _zc_instance.unregister_service(_zc_service_info)
            _zc_instance.close()
        except Exception:
            pass


async def _init_mdns_background(application):
    """Corre _register_mdns en un thread, recoge el resultado"""
    global _zc_instance, _zeroconf_registered, _zc_service_info
    try:
        zc, info = await asyncio.to_thread(_register_mdns)
        _zc_instance = zc
        _zc_service_info = info
        _zeroconf_registered = True
        log(f"\U0001F3E0 mDNS activo: http://luna.local:9120")
    except Exception as e:
        log(f"\u26A0\uFE0F mDNS no disponible: {e}")


def _register_mdns():
    """Sincrónica - corre ENTERA en un thread. Retorna (Zeroconf, ServiceInfo)"""
    from zeroconf import Zeroconf, ServiceInfo
    ips = get_local_ips()
    zc_service_info = ServiceInfo(
        "_luna._tcp.local.",
        "Luna._luna._tcp.local.",
        addresses=[socket.inet_aton(ip) for ip in ips],
        port=9120,
        properties={"path": "/"},
        server="luna.local.",
    )
    zc = Zeroconf()
    zc.register_service(zc_service_info)
    return zc, zc_service_info


async def _init_license_background():
    try:
        await asyncio.to_thread(license_module.refresh_license, load_config, save_config)
        pro = license_module.check_license(load_config, save_config)
        log(f"Licencia: {'Pro' if pro else 'Gratuita'}")
    except Exception as e:
        log(f"Licencia no disponible: {e}")


async def _notify_pro_clients():
    pro = license_module.check_license(load_config, save_config)
    for ws in list(CONNECTED_CLIENTS):
        try:
            await ws.send_text(json.dumps({
                "type": "pro_update",
                "is_pro_version": pro
            }))
        except Exception:
            pass


async def _broadcast_config_updated():
    for ws in list(CONNECTED_CLIENTS):
        try:
            await ws.send_text(json.dumps({"type": "config_updated"}))
        except Exception:
            pass


app = FastAPI(title="Luna Host v0.1", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)
CONNECTED_CLIENTS: set = set()

FREE_PROFILE_LIMIT = 3

_config_cache = None
_config_cache_time = 0
CONFIG_CACHE_TTL = 1.5


def _get_config_cached():
    global _config_cache, _config_cache_time
    now = time.time()
    if _config_cache is not None and now - _config_cache_time < CONFIG_CACHE_TTL:
        return _config_cache
    _config_cache = load_config()
    _config_cache_time = now
    return _config_cache


_tracker = WindowTracker(load_config)
_tracker.start()


def log(msg: str):
    try:
        print(msg, flush=True)
    except Exception:
        pass


_mci_counter = 0
_mci_lock = threading.Lock()

def _play_sound_on_pc(filename: str):
    path = os.path.join(SOUNDS_DIR, filename)
    if not os.path.isfile(path):
        return
    threading.Thread(target=_play_async, args=(path,), daemon=True).start()

def _play_async(path):
    global _mci_counter
    import ctypes
    try:
        with _mci_lock:
            alias = f"luna_{_mci_counter % 16}"
            _mci_counter += 1
        mci = ctypes.windll.winmm.mciSendStringW
        mci(f"close {alias}", None, 0, 0)
        mci(f'open "{path}" alias {alias}', None, 0, 0)
        mci(f"play {alias} from 0", None, 0, 0)
    except Exception:
        pass


def _play_sound_for_key(cmd):
    try:
        cfg = _get_config_cached()
        pname = _tracker.active_profile or cfg.get("perfil_activo", "default")
        profile = cfg.get("perfiles", {}).get(pname, {})
        for k in profile.get("keys", []):
            if k.get("keyCode") == cmd.key_code and k.get("mods", 0) == cmd.modifiers:
                sound = k.get("sound")
                if sound:
                    _play_sound_on_pc(sound)
                break
    except Exception:
        pass




def get_local_ips() -> list[str]:
    ips: list[str] = []
    try:
        import subprocess, re
        out = subprocess.check_output("ipconfig", encoding="oem", stderr=subprocess.DEVNULL)
        for line in out.splitlines():
            line = line.strip()
            if re.search(r"IPv4[^:]*:", line, re.IGNORECASE):
                ip = line.split(":")[-1].strip()
                if _is_private_ip(ip):
                    ips.append(ip)
    except Exception:
        pass
    if not ips:
        ips.append("127.0.0.1")
    return ips

def _is_private_ip(ip: str) -> bool:
    if ip.startswith("192.168.") or ip.startswith("10."):
        return True
    if ip.startswith("172."):
        parts = ip.split(".")
        if len(parts) >= 2:
            try:
                second = int(parts[1])
                return 16 <= second <= 31
            except ValueError:
                pass
    return False


@app.get("/")
async def root():
    return FileResponse(
        os.path.join(WEB_UI_DIR, "index.html"),
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
    )


@app.get("/manifest.json")
async def manifest():
    return FileResponse(
        os.path.join(WEB_UI_DIR, "manifest.json"),
        media_type="application/manifest+json",
    )


@app.get("/icon-192.png")
async def icon_192():
    return FileResponse(os.path.join(WEB_UI_DIR, "icon-192.png"), media_type="image/png")


@app.get("/icon-512.png")
async def icon_512():
    return FileResponse(os.path.join(WEB_UI_DIR, "icon-512.png"), media_type="image/png")


@app.get("/api/config")
async def get_config():
    data = load_config()
    return JSONResponse(data)


@app.post("/api/config")
async def post_config(request: Request):
    body = await request.json()
    if body.get("restore"):
        body = default_config()
        ok = save_config(body)
    else:
        cfg = load_config()
        is_pro = cfg.get("pro_license", False)
        perfiles = body.get("perfiles", {})
        if not is_pro:
            for pdata in perfiles.values():
                pdata["cols"] = 4
        cfg["perfiles"] = perfiles
        if "perfil_activo" in body:
            cfg["perfil_activo"] = body["perfil_activo"]
        elif "activeProfile" in body:
            cfg["perfil_activo"] = body["activeProfile"]
        for key in body:
            if key not in ("perfiles", "perfil_activo", "activeProfile"):
                cfg[key] = body[key]
        ok = save_config(cfg)
    if ok:
        log("Configuracion guardada")
        asyncio.create_task(_broadcast_config_updated())
        return JSONResponse({"ok": True})
    log("Error al guardar configuracion")
    import traceback
    log(traceback.format_exc())
    return JSONResponse({"ok": False, "error": "No se pudo guardar. Revisa que la config no tenga rutas invalidas."}, status_code=500)


@app.post("/api/config/restore-profile")
async def restore_profile(request: Request):
    body = await request.json()
    profile_name = body.get("profile")
    if not profile_name:
        return JSONResponse({"ok": False, "error": "Falta nombre de perfil"}, status_code=400)
    defaults = default_config()
    if profile_name in defaults.get("perfiles", {}):
        restored = dict(defaults["perfiles"][profile_name])
    else:
        restored = {"cols": 4, "keys": [{"label": "---", "keyCode": 0, "mods": 0} for _ in range(16)]}
    ok = merge_config(profile_name, restored)
    return JSONResponse({"ok": ok})


@app.post("/api/config/delete-profile")
async def delete_profile(request: Request):
    body = await request.json()
    profile_name = body.get("profile")
    if not profile_name:
        return JSONResponse({"ok": False, "error": "Falta nombre de perfil"}, status_code=400)
    if profile_name == "default":
        return JSONResponse({"ok": False, "error": "No se puede borrar el perfil default"}, status_code=400)
    ok = delete_config(profile_name)
    return JSONResponse({"ok": ok})


@app.get("/api/ip")
async def api_ip():
    ips = await asyncio.to_thread(get_local_ips)
    return JSONResponse({"ips": ips, "port": 9120})


@app.get("/api/pairing-code")
async def api_pairing_code():
    code = _get_pairing_code()
    if code is None:
        code = await asyncio.to_thread(_generate_pairing_code)
    expires_in = int(_pairing_code_expires - time.time()) if _pairing_code_expires > time.time() else 0
    return JSONResponse({"code": code, "expires_in": max(expires_in, 0)})


@app.post("/api/pair")
async def api_pair(request: Request):
    body = await request.json()
    code = body.get("code", "")
    if not _verify_pairing_code(code):
        return JSONResponse({"paired": False, "error": "Código incorrecto o expirado"}, status_code=400)
    token = _generate_token()
    ip = request.client.host if request.client else "unknown"
    name = body.get("device_name", socket.gethostname())
    _paired_tokens[token] = {"name": name, "ip": ip, "since": time.time()}
    _pairing_code = None  # invalidar código después de emparejar
    log(f"[pair] Dispositivo emparejado: {name} ({ip}) token={token[:8]}...")
    return JSONResponse({"paired": True, "token": token, "device_name": socket.gethostname(), "uuid": PC_UUID})


@app.post("/api/unpair")
async def api_unpair(request: Request):
    body = await request.json()
    token = body.get("token", "")
    if token in _paired_tokens:
        del _paired_tokens[token]
        log(f"[pair] Token revocado: {token[:8]}...")
        return JSONResponse({"unpaired": True})
    return JSONResponse({"unpaired": False, "error": "Token no encontrado"}, status_code=404)


@app.get("/api/uuid")
async def api_uuid():
    ips = await asyncio.to_thread(get_local_ips)
    return JSONResponse({"uuid": PC_UUID, "name": socket.gethostname(), "ips": ips})


@app.get("/api/firewall-status")
async def api_firewall_status():
    """Verifica si las reglas de firewall existen y el puerto 9120 es accesible."""
    import subprocess
    rules_ok = {"LunaDeck_Port": False, "LunaDeck_App": False, "LunaDeck_Discovery_UDP": False}
    for name in rules_ok:
        try:
            r = subprocess.run(
                ["netsh", "advfirewall", "firewall", "show", "rule", f"name={name}"],
                capture_output=True, text=True, timeout=5,
                creationflags=_NO_WINDOW
            )
            rules_ok[name] = r.returncode == 0
        except Exception:
            pass
    # Verificar si el puerto 9120 escucha en 0.0.0.0
    port_open = False
    try:
        import socket as sock_mod
        s = sock_mod.socket(sock_mod.AF_INET, sock_mod.SOCK_STREAM)
        s.settimeout(2)
        if s.connect_ex(("127.0.0.1", 9120)) == 0:
            port_open = True
        s.close()
    except Exception:
        pass
    # Perfil de red
    net_profile = "Desconocido"
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-NetConnectionProfile).NetworkCategory"],
            capture_output=True, text=True, timeout=5,
            creationflags=_NO_WINDOW
        )
        if r.returncode == 0:
            net_profile = r.stdout.strip()
    except Exception:
        pass
    ips = await asyncio.to_thread(get_local_ips)
    return JSONResponse({
        "rules": rules_ok,
        "port_9120_listening": port_open,
        "network_profile": net_profile,
        "local_ips": ips,
        "server_running": True
    })


@app.get("/api/qr")
async def api_qr():
    import qrcode
    from io import BytesIO
    ips = await asyncio.to_thread(get_local_ips)
    primary_ip = ips[0] if ips else "127.0.0.1"
    code = _get_pairing_code()
    if code is None:
        code = await asyncio.to_thread(_generate_pairing_code)
    qr_data = json.dumps({"type": "luna_pair", "uuid": PC_UUID, "ip": primary_ip, "port": 9120, "code": code})
    qr = qrcode.make(qr_data)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)
    return Response(content=buf.read(), media_type="image/png")


@app.get("/api/version")
async def api_version():
    return JSONResponse({"app_version": "2.1.0", "apk_version": APK_VERSION})

@app.get("/api/pro-status")
async def api_pro_status():
    pro = license_module.check_license(load_config, save_config)
    return JSONResponse({"pro": pro})


@app.post("/api/pro-check")
async def api_pro_check(request: Request):
    body = await request.json()
    refresh = body.get("refresh", False)
    pro = license_module.check_license(load_config, save_config, force=refresh)
    return JSONResponse({"pro": pro})


@app.post("/api/pro-purchase")
async def api_pro_purchase():
    cfg = load_config()
    addon_id = cfg.get("store_addon_id", "")
    result = await license_module.purchase_license(addon_id)

    if result.get("redirect_url"):
        return JSONResponse({"pro": False, "purchased": False, "redirect_url": result["redirect_url"]})

    if result["success"]:
        cfg["pro_license"] = True
        save_config(cfg)
        license_module.invalidate_cache()
        asyncio.create_task(_notify_pro_clients())
        return JSONResponse({"pro": True, "purchased": True})

    return JSONResponse({"pro": False, "purchased": False, "error": result.get("error", "unknown")})


@app.post("/api/open-url")
async def api_open_url(request: Request):
    body = await request.json()
    url = body.get("url", "")
    if not url:
        return JSONResponse({"ok": False, "error": "no url"})
    try:
        os.startfile(url)
        return JSONResponse({"ok": True})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)})


@app.post("/api/pro-reset")
async def api_pro_reset():
    cfg = load_config()
    cfg["pro_license"] = False
    save_config(cfg)
    license_module.invalidate_cache()
    asyncio.create_task(_notify_pro_clients())
    return JSONResponse({"pro": False, "reset": True})


@app.get("/api/themes")
async def api_get_themes():
    cfg = load_config()
    return JSONResponse(cfg.get("themes", {}))


@app.post("/api/themes")
async def api_save_themes(request: Request):
    body = await request.json()
    cfg = load_config()
    cfg["themes"] = body
    ok = save_config(cfg)
    if ok:
        asyncio.create_task(_broadcast_theme(cfg["themes"]))
        return JSONResponse({"ok": True})
    return JSONResponse({"ok": False}, status_code=500)


async def _broadcast_theme(themes: dict):
    msg = json.dumps({"type": "theme_update", "themes": themes})
    for ws in list(CONNECTED_CLIENTS):
        try:
            await ws.send_text(msg)
        except Exception:
            pass


@app.post("/api/themes/restore")
async def api_restore_themes():
    from .config_manager import _DEFAULT
    cfg = load_config()
    cfg["themes"] = dict(_DEFAULT["themes"])
    ok = save_config(cfg)
    if ok:
        asyncio.create_task(_broadcast_theme(cfg["themes"]))
        return JSONResponse({"ok": True})
    return JSONResponse({"ok": False}, status_code=500)


@app.get("/apk")
async def apk_download():
    if os.path.isfile(APK_PATH):
        return FileResponse(APK_PATH, media_type="application/vnd.android.package-archive", filename="Luna.apk")
    return RedirectResponse(url="https://sr-lolo.github.io/luna/")


@app.get("/api/qr-apk")
async def api_qr_apk():
    import qrcode
    from io import BytesIO
    url = "https://sr-lolo.github.io/luna/"
    qr = qrcode.make(url)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)
    return Response(content=buf.read(), media_type="image/png")


@app.post("/api/upload-icon")
async def upload_icon(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        return JSONResponse({"ok": False, "error": "Formato no soportado. Usa PNG, JPG o GIF."}, status_code=400)
    if file.content_type == "image/gif":
        cfg = load_config()
        if not cfg.get("pro_license", False):
            return JSONResponse({"ok": False, "error": "Subir GIFs solo disponible en versión Pro."}, status_code=403)
    ext = os.path.splitext(file.filename or "image.png")[1].lower()
    if ext not in (".png", ".jpg", ".jpeg", ".gif"):
        ext = ".png"
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        return JSONResponse({"ok": False, "error": "Archivo demasiado grande. Máximo 5 MB."}, status_code=400)
    name = f"{uuid.uuid4().hex[:8]}_{file.filename or 'icon'}"
    os.makedirs(CUSTOM_ICONS_DIR, exist_ok=True)
    with open(os.path.join(CUSTOM_ICONS_DIR, name), "wb") as f:
        f.write(content)
    log(f"▸ Icono subido: {name}")
    return JSONResponse({"ok": True, "filename": name})


@app.post("/api/upload-sound")
async def upload_sound(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        return JSONResponse({"ok": False, "error": "Formato no soportado. Usa WAV o MP3."}, status_code=400)
    ext = os.path.splitext(file.filename or "sound.wav")[1].lower()
    if ext not in (".wav", ".mp3"):
        ext = ".wav"
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        return JSONResponse({"ok": False, "error": "Archivo demasiado grande. Máximo 5 MB."}, status_code=400)
    name = f"{uuid.uuid4().hex[:8]}_{file.filename or 'sound'}"
    os.makedirs(SOUNDS_DIR, exist_ok=True)
    with open(os.path.join(SOUNDS_DIR, name), "wb") as f:
        f.write(content)
    log(f"▸ Sonido subido: {name}")
    return JSONResponse({"ok": True, "filename": name})


@app.get("/api/icon")
async def api_icon(exe: str = ""):
    from io import BytesIO
    from PIL import Image

    if not exe:
        return Response(status_code=400)
    try:
        import subprocess
        out = subprocess.check_output(
            ["where", exe], stderr=subprocess.DEVNULL, timeout=3
        ).decode("oem", errors="replace").strip().splitlines()
        exe_path = out[0] if out else None
    except Exception:
        exe_path = None

    if not exe_path:
        img = Image.new("RGBA", (32, 32), (80, 80, 80, 255))
        buf = BytesIO()
        img.save(buf, "PNG")
        buf.seek(0)
        return Response(content=buf.read(), media_type="image/png")

    try:
        import win32gui
        import win32ui
        import win32api
        import win32con
        ICON_SIZE = 128
        large, _ = win32gui.ExtractIconEx(exe_path, 0)
        if large:
            hicon = large[0]
            hwnd = 0
            hdc = win32gui.GetDC(hwnd)
            try:
                pyhdc = win32ui.CreateDCFromHandle(hdc)
                hbmp = win32ui.CreateBitmap()
                hbmp.CreateCompatibleBitmap(pyhdc, ICON_SIZE, ICON_SIZE)
                compat = pyhdc.CreateCompatibleDC()
                compat.SelectObject(hbmp)
                win32gui.DrawIconEx(compat.GetSafeHdc(), 0, 0, hicon, ICON_SIZE, ICON_SIZE, 0, None, win32con.DI_NORMAL)
                bmpstr = hbmp.GetBitmapBits(True)
                img = Image.frombuffer("RGBA", (ICON_SIZE, ICON_SIZE), bmpstr, "raw", "BGRA", 0, 1)
                compat.DeleteDC()
                pyhdc.DeleteDC()
            finally:
                win32gui.ReleaseDC(hwnd, hdc)
            win32gui.DestroyIcon(hicon)
            buf = BytesIO()
            img.save(buf, "PNG")
            buf.seek(0)
            return Response(content=buf.read(), media_type="image/png")
    except Exception:
        pass

    img = Image.new("RGBA", (32, 32), (60, 60, 60, 255))
    buf = BytesIO()
    img.save(buf, "PNG")
    buf.seek(0)
    return Response(content=buf.read(), media_type="image/png")


@app.get("/api/search-exe")
async def api_search_exe(q: str = ""):
    if not q or len(q) < 3:
        return JSONResponse([])
    try:
        import subprocess
        out = subprocess.check_output(
            ["where", q + "*"], stderr=subprocess.DEVNULL, timeout=5
        ).decode("oem", errors="replace").strip().splitlines()
        results = [{"name": os.path.basename(p), "path": p} for p in out[:10]]
        return JSONResponse(results)
    except Exception:
        return JSONResponse([])


def _extract_exe_icon(exe_path: str) -> str | None:
    import win32gui, win32ui, win32api, win32con
    from PIL import Image
    from io import BytesIO
    exe_name = os.path.splitext(os.path.basename(exe_path))[0]
    try:
        ICON_SIZE = 128
        large, _ = win32gui.ExtractIconEx(exe_path, 0)
        if large:
            hicon = large[0]
            hwnd = 0
            hdc = win32gui.GetDC(hwnd)
            try:
                pyhdc = win32ui.CreateDCFromHandle(hdc)
                hbmp = win32ui.CreateBitmap()
                hbmp.CreateCompatibleBitmap(pyhdc, ICON_SIZE, ICON_SIZE)
                compat = pyhdc.CreateCompatibleDC()
                compat.SelectObject(hbmp)
                win32gui.DrawIconEx(compat.GetSafeHdc(), 0, 0, hicon, ICON_SIZE, ICON_SIZE, 0, None, win32con.DI_NORMAL)
                bmpstr = hbmp.GetBitmapBits(True)
                img = Image.frombuffer("RGBA", (ICON_SIZE, ICON_SIZE), bmpstr, "raw", "BGRA", 0, 1)
                compat.DeleteDC()
                pyhdc.DeleteDC()
            finally:
                win32gui.ReleaseDC(hwnd, hdc)
            win32gui.DestroyIcon(hicon)
            filename = f"{uuid.uuid4().hex[:12]}_{exe_name}.png"
            os.makedirs(CUSTOM_ICONS_DIR, exist_ok=True)
            img.save(os.path.join(CUSTOM_ICONS_DIR, filename), "PNG")
            return filename
    except Exception as e:
        log(f"Error extrayendo icono de {exe_path}: {e}")
    return None


@app.post("/api/exe-icon")
async def api_exe_icon(request: Request):
    body = await request.json()
    exe_path = body.get("path", "")
    if not exe_path or not os.path.isfile(exe_path):
        return JSONResponse({"ok": False, "error": "Archivo no encontrado"}, status_code=400)
    icon_filename = _extract_exe_icon(exe_path)
    if not icon_filename:
        return JSONResponse({"ok": False, "error": "No se pudo extraer el icono"}, status_code=500)
    exe_name = os.path.splitext(os.path.basename(exe_path))[0]
    return JSONResponse({"ok": True, "icon": icon_filename, "exeName": exe_name})


@app.post("/api/resolve-lnk")
async def api_resolve_lnk(request: Request):
    body = await request.json()
    lnk_path = body.get("path", "")
    if not lnk_path or not os.path.isfile(lnk_path) or not lnk_path.lower().endswith(".lnk"):
        return JSONResponse({"ok": False, "error": "Archivo .lnk no encontrado"}, status_code=400)
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(lnk_path)
        target = shortcut.TargetPath
        if not target or not os.path.isfile(target) or not target.lower().endswith(".exe"):
            return JSONResponse({"ok": False, "error": "El acceso directo no apunta a un .exe v\u00e1lido"}, status_code=400)
        exe_name = os.path.splitext(os.path.basename(target))[0]
        return JSONResponse({"ok": True, "exePath": target, "exeName": exe_name})
    except Exception as e:
        log(f"Error resolviendo .lnk: {e}")
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


EXE_EXTENSIONS = {".exe", ".lnk"}

@app.post("/api/upload-exe")
async def api_upload_exe(file: UploadFile = File(...)):
    if not file.filename or os.path.splitext(file.filename.lower())[1] not in EXE_EXTENSIONS:
        return JSONResponse({"ok": False, "error": "Solo se aceptan archivos .exe o .lnk"}, status_code=400)
    raw_name = os.path.splitext(os.path.basename(file.filename))[0]
    safe_name = os.path.basename(file.filename)
    saved_path = os.path.join(EXES_DIR, safe_name)
    content = await file.read()
    with open(saved_path, "wb") as f:
        f.write(content)
    # Resolve .lnk if uploaded
    if saved_path.lower().endswith(".lnk"):
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortcut(saved_path)
            target = shortcut.TargetPath
            if target and os.path.isfile(target) and target.lower().endswith(".exe"):
                exe_name = os.path.splitext(os.path.basename(target))[0]
                icon_filename = _extract_exe_icon(target)
                try: os.remove(saved_path)
                except: pass
                if not icon_filename:
                    return JSONResponse({"ok": False, "error": "No se pudo extraer el icono"}, status_code=500)
                return JSONResponse({"ok": True, "icon": icon_filename, "exeName": exe_name, "savedPath": target})
        except Exception as e:
            log(f"Error procesando .lnk subido: {e}")
            try: os.remove(saved_path)
            except: pass
            return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
    exe_name = raw_name
    icon_filename = _extract_exe_icon(saved_path)
    if not icon_filename:
        try: os.remove(saved_path)
        except: pass
        return JSONResponse({"ok": False, "error": "No se pudo extraer el icono"}, status_code=500)
    return JSONResponse({"ok": True, "icon": icon_filename, "exeName": exe_name, "savedPath": saved_path})


@app.get("/dashboard")
async def dashboard():
    return FileResponse(
        os.path.join(WEB_UI_DIR, "dashboard.html"),
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
    )


@app.get("/ayuda")
async def ayuda():
    return FileResponse(
        os.path.join(WEB_UI_DIR, "ayuda.html"),
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
    )


LAUNCH_KEYCODE_MIN = 200

def _is_launch_key(cmd):
    if cmd.key_code < LAUNCH_KEYCODE_MIN:
        return False
    cfg = load_config()
    profile = cfg.get("perfiles", {}).get(cfg.get("perfil_activo", ""), {})
    for k in profile.get("keys", []):
        if k.get("keyCode") == cmd.key_code and k.get("launch"):
            return True
    return False

def _launch_app(cmd):
    cfg = load_config()
    profile = cfg.get("perfiles", {}).get(cfg.get("perfil_activo", ""), {})
    for k in profile.get("keys", []):
        if k.get("keyCode") == cmd.key_code and k.get("launch"):
            path = k["launch"]
            try:
                os.startfile(path)
                log(f"Lanzando: {path}")
            except Exception:
                try:
                    cwd = os.path.dirname(path)
                    subprocess.Popen([path], cwd=cwd)
                    log(f"Lanzando (fallback): {path}")
                except Exception as e:
                    log(f"Error al lanzar {path}: {e}")
            break


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    CONNECTED_CLIENTS.add(ws)
    if len(CONNECTED_CLIENTS) == 1:
        _tracker.resume()
    sent_profile = None
    log("▸ Móvil conectado")

    try:
        cfg = load_config()
        pro = cfg.get("pro_license", False)
        await ws.send_text(json.dumps({
            "type": "init",
            "is_pro_version": pro
        }))
    except Exception:
        pass
    try:
        while True:
            try:
                data = await asyncio.wait_for(ws.receive_bytes(), timeout=0.1)
                cmd = unpack(data)
                if cmd is None:
                    log("⚠️ Paquete inválido recibido")
                    continue
                if isinstance(cmd, KeyCommand):
                    try:
                        if cmd.action != ACTION_RELEASE:
                            _play_sound_for_key(cmd)
                        if _is_launch_key(cmd):
                            _launch_app(cmd)
                        elif cmd.key_code != 0:
                            execute_key(cmd)
                    except Exception:
                        log(f"⚠️ Error al ejecutar tecla '{cmd.key}'")
                elif isinstance(cmd, SliderCommand):
                    ok = execute_slider(cmd)
                    if ok:
                        log(f"▸ Slider {cmd.slider_id} = {cmd.value}")
                    else:
                        log(f"⚠️ Slider {cmd.slider_id} no disponible")
            except asyncio.TimeoutError:
                pass

            ap = _tracker.active_profile
            if ap is not None and ap != sent_profile:
                try:
                    msg = {"type":"switch_profile","profile":ap}
                    if _tracker.last_exe:
                        msg["window"] = _tracker.last_exe
                    await ws.send_text(json.dumps(msg))
                    sent_profile = ap
                    log(f"\u25B8 Auto-switch a perfil '{ap}' ({_tracker.last_exe})")
                except Exception:
                    pass
    except WebSocketDisconnect:
        pass
    finally:
        CONNECTED_CLIENTS.discard(ws)
        if not CONNECTED_CLIENTS:
            _tracker.pause()
        from .keyboard_engine import release_all
        release_all()
        log("▸ Móvil desconectado")


@app.get("/icons/{filename:path}")
async def serve_icon(filename: str):
    if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
        return Response(status_code=400)
    path = os.path.join(WEB_UI_DIR, "icons", filename)
    if os.path.isfile(path):
        return FileResponse(path)
    if os.path.isdir(ICONS_ALL_DIR):
        for root, dirs, files in os.walk(ICONS_ALL_DIR):
            if filename in files:
                return FileResponse(os.path.join(root, filename))
    return Response(status_code=404)


app.mount("/custom-icons", StaticFiles(directory=CUSTOM_ICONS_DIR), name="custom_icons")
app.mount("/custom-sounds", StaticFiles(directory=SOUNDS_DIR), name="custom_sounds")
app.mount("/web_ad", StaticFiles(directory=AD_UI_DIR), name="web_ad")
app.mount("/", StaticFiles(directory=WEB_UI_DIR), name="mobile_ui")
