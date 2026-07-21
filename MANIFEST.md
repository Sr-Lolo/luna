# MANIFIESTO — LunaDeck v1.7.60 (Build 2026-07-20)

> **Propósito**: Documentar la arquitectura, protocolo, dependencias, compatibilidad y procesos de build de LunaDeck para que cualquier programador pueda entender, mantener y heredar el proyecto sin pérdida de conocimiento.

---

## 1. VISIÓN GENERAL

LunaDeck convierte un teléfono Android o navegador web en un control remoto inalámbrico para Windows. Sirve como teclado macro, control de volumen/brillo, scrollpad y lanzador de aplicaciones.

### Componentes

| Componente | Rol | Tecnología |
|---|---|---|
| **PC Server** | Servidor HTTP + WebSocket en Windows | Python 3.10+, FastAPI, pywebview |
| **Android APK** | App nativa que se conecta al servidor | Kotlin, Android SDK 26+, OkHttp |
| **Web UI** | Interfaz web (dashboard + control remoto) | HTML, CSS, JavaScript vanilla |
| **Web Ad (PC)** | Mini sitio para banner publicitario en web UI | HTML + CSS aislado (Adsterra) |
| **GitHub Pages** | Distribución del APK + version.json | GitHub Pages desde raíz del repo |

### Arquitectura general

```
[Android APK] ←→ WebSocket (binario 5 bytes) ←→ [PC Server :9120] → teclado/volumen/brillo Windows
                                    ↕ HTTP REST (/api/*)
                              [Web UI / Dashboard]
                                    ↕ pywebview
                              [Ventana nativa Windows]

[GitHub Pages: sr-lolo.github.io/luna/]
  ├── version.json      → APK detecta actualización
  ├── Luna.apk          → Descarga directa
  ├── index.html        → Página de descarga
  ├── ad_pc.html        → Anuncio para web UI (PC)
  └── ad_banner.html    → Anuncio para WebView de APK
```

---

## 2. COMPATIBILIDAD

### PC Server

| Requisito | Detalle |
|---|---|
| **Sistema operativo** | Windows 10 (build 19041+) y Windows 11 |
| **WebView2 Runtime** | Preinstalado en Win 11; requiere descarga manual en Win 10 |
| **Python** | 3.10+ (si se ejecuta desde código fuente) |
| **Arquitectura** | x64 |
| **Red** | Wi-Fi o Ethernet; mismo segmento de red que el móvil |
| **Firewall** | Puerto 9120 debe estar abierto; se recomienda ejecutar como Admin |
| **Microsoft Store** | Opcional; solo para verificación de licencia Pro |
| **ADB** | Opcional; solo para conexión USB |

### Android APK

| Requisito | Detalle |
|---|---|
| **Sistema operativo** | Android 8.0+ (API 26) |
| **Arquitectura** | ARM, ARM64, x86, x86_64 (multilib) |
| **Tamaño** | ~7.8 MB |
| **Permisos** | Internet, CAMARA (QR), ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, CHANGE_WIFI_MULTICAST_STATE, ACCESS_FINE_LOCATION (Wi-Fi discovery), REQUEST_INSTALL_PACKAGES (auto-update) |
| **Red** | Wi-Fi (misma red que PC) o USB (ADB reverse) |
| **QR** | Opcional; requiere cámara |
| **Auto-update** | Requiere acceso a GitHub Pages (https) |

### Limitaciones conocidas

- **mDNS** (zeroconf) puede fallar en redes corporativas con políticas restrictivas — se mantienen QR + IP manual como fallback
- **Control de brillo** usa `screen-brightness-control` que puede no funcionar en todos los monitores
- **Keyboard library** requiere permisos de administrador en algunas configuraciones de Windows
- **WebView2** no está disponible en Windows 10 sin instalación manual
- **APK no firmado para Play Store** — solo distribución directa (sideload)

---

## 3. PC SERVER (`server/`)

### 3.1 Entry Point

**Desarrollo**: `server/main.py` → `import src.gui; gui.run()`
**Build (EXE)**: `server/src/gui.py` directamente (tiene `if __name__ == "__main__": run()`)`

### 3.2 Archivos fuente (`server/src/`)

| Archivo | Líneas | Propósito |
|---|---|---|
| `gui.py` | ~415 | Ventana WebView, bandeja del sistema, ciclo de vida del servidor, `__main__` entry point |
| `server.py` | ~1224 | App FastAPI, todas las rutas REST, WebSocket, mDNS, ad serving |
| `config_manager.py` | ~303 | Carga/guarda/migra config.json |
| `protocol.py` | ~142 | Protocolo binario de 5 bytes (codificación/decodificación) |
| `keyboard_engine.py` | ~51 | Ejecuta pulsaciones de teclas (librería `keyboard`) |
| `slider_engine.py` | ~181 | Controla volumen (COM), brillo (SBC), scroll (SendInput) |
| `window_tracker.py` | ~74 | Monitorea ventana activa y cambia perfiles automáticamente |
| `license.py` | ~84 | Licencia Pro vía Microsoft Store (`winrt`) o config fallback |
| `__init__.py` | 0 | Vacío |

### 3.3 Inicio y ciclo de vida (`gui.py`)

1. **Lock de instancia única**: archivo `%TEMP%/luna.lock` con PID; detecta procesos zombies vía `OpenProcess`
2. **Inicio del servidor**: `_start_server()` lanza uvicorn en `0.0.0.0:9120`
3. **Ventana pywebview**: apunta a `http://127.0.0.1:9120/` con tamaño 730x640, no redimensionable
4. **Icono**: se carga `app.ico` (16x16 + 32x32) en barra de título y taskbar
5. **Bandeja del sistema**: minimiza al cerrar ventana; click izquierdo abre, click derecho menú
6. **Cierre**: diálogo JS de confirmación; si no responde en 5s, fuerza cierre vía `PostMessageW`
7. **Cierre completo**: solo desde menú contextual "Salir"

### 3.4 Frontend web (`server/web/`)

| Archivo | Propósito |
|---|---|
| `index.html` | UI principal de control remoto (teclas, sliders, scrollpads) |
| `dashboard.html` | Editor de perfiles, teclas, temas, sonidos, iconos, exes |
| `ayuda.html` | Manual de usuario completo |
| `mobile-grid.html` | Grid HTML mínimo para WebView del APK (renderizado en móvil) |
| `welcome_template.html` | Plantilla de onboarding (insertada vía pywebview) |
| `app.js` | Lógica JS: WebSocket, REST, renderizado, perfilado, temas, Pro |
| `style.css` | Estilos oscuros responsivos con variables CSS para temas |
| `manifest.json` | PWA manifest (básico, sin service worker) |
| `lang/` | Traducciones EN/ES/PT + `i18n.js` |
| `icons/` | 56 PNGs para botones |

### 3.5 API REST (HTTP en puerto 9120)

#### Configuración

| Método | Ruta | Propósito |
|---|---|---|
| GET | `/api/config` | Obtener configuración completa |
| POST | `/api/config` | Guardar configuración |
| POST | `/api/config/restore-profile` | Restaurar perfil por defecto |
| POST | `/api/config/delete-profile` | Eliminar un perfil |
| GET | `/api/themes` | Obtener temas (PC + Mobile) |
| POST | `/api/themes` | Guardar temas personalizados |
| POST | `/api/themes/restore` | Restaurar temas por defecto |

#### Red y descubrimiento

| Método | Ruta | Propósito |
|---|---|---|
| GET | `/api/ip` | IP y puerto del servidor |
| GET | `/api/qr` | QR con JSON de conexión (IP + UUID + pairing code) |
| GET | `/api/qr-apk` | QR que apunta a la descarga del APK |
| GET | `/api/version` | Versiones del servidor (`app_version`) y APK recomendada (`apk_version`) |

#### Licencia Pro

| Método | Ruta | Propósito |
|---|---|---|
| GET | `/api/pro-status` | Estado de licencia (cached) |
| POST | `/api/pro-check` | Forzar verificación contra Microsoft Store |
| POST | `/api/pro-purchase` | Iniciar compra en MS Store |
| POST | `/api/pro-reset` | Resetear licencia (testing) |

#### Utilidades

| Método | Ruta | Propósito |
|---|---|---|
| POST | `/api/upload-icon` | Subir icono PNG/JPG/GIF (GIF solo Pro) |
| POST | `/api/upload-sound` | Subir sonido WAV/MP3 |
| POST | `/api/upload-exe` | Subir ejecutable para lanzar |
| POST | `/api/exe-icon` | Extraer icono de un .exe |
| POST | `/api/open-url` | Abrir URL en navegador del PC |

#### WebSocket

| Protocolo | Ruta | Propósito |
|---|---|---|
| WS | `/ws` | Recibir comandos binarios del APK; enviar notificaciones JSON |

---

## 4. SISTEMA DE ANUNCIOS

### 4.1 Anuncio en Web UI (PC)

- Las páginas `index.html`, `dashboard.html`, `ayuda.html` tienen un `#ad-banner` con un `#ad-frame` (iframe)
- El iframe carga `https://sr-lolo.github.io/luna/ad_pc.html` (alojado en GitHub Pages)
- `ad_pc.html` contiene el script de Adsterra (`highperformanceformat.com`)
- El banner se muestra SOLO en desktop (clase `.desktop` en `<html>`) y SOLO si `pro_license=false`
- Al cerrar el banner o si Pro=true, se añade clase `.ad-banner-hidden` (opacity 0 + pointer-events none)
- Banner mide 468x60 píxeles, fijo al fondo de la pantalla

### 4.2 Anuncio en APK (Mobile)

- El APK tiene un `adWebView` de 50dp de alto (visible cuando `adsRemoved=false`)
- Carga `https://sr-lolo.github.io/luna/ad_banner.html` (alojado en GitHub Pages)
- `ad_banner.html` contiene otro script de Adsterra (key diferente al de PC)
- `adsRemoved` se guarda en SharedPreferences y se actualiza via WebSocket (`"is_pro_version"`)
- Si el PC server reporta Pro, el APK oculta el `adWebView`

### 4.3 Licencia Pro

- Verificación primaria: Microsoft Store add-on `9PNCV2XSK9K8` vía `winrt`
- Fallback: campo `pro_license` en `config.json`
- Beneficios Pro: sin anuncios, GIFs en iconos, perfiles sin límite de columnas
- El servidor envía `is_pro_version` al APK al conectar WebSocket (`{"type":"init"}`)
- APK oculta anuncios y persiste estado en SharedPreferences

---

## 5. PROTOCOLO BINARIO (WebSocket)

Cada mensaje WebSocket del APK al servidor son **exactamente 5 bytes**:

```
Byte 0: Tipo de mensaje
Byte 1: Acción / ID de slider
Byte 2: Modificadores / Valor
Byte 3: Código de tecla / 0x00
Byte 4: Checksum XOR (bytes 0-3)
```

### 5.1 Mensajes de teclado (Type = 0x01)

| Byte 1 (Acción) | Significado |
|---|---|
| `0x01` | Presionar (PRESS) |
| `0x02` | Soltar (RELEASE) |
| `0x03` | Tocar (TAP) |

| Byte 2 (Modificadores) | Bit | Significado |
|---|---|---|
| `0x01` | 0 | CTRL |
| `0x02` | 1 | SHIFT |
| `0x04` | 2 | ALT |
| `0x08` | 3 | WIN |

### 5.2 Mensajes de slider (Type = 0x02)

| Byte 1 (Slider ID) | Control |
|---|---|
| `0x01` | Volumen del sistema |
| `0x02` | Brillo de pantalla |
| `0x03` | Scroll vertical |
| `0x04` | Scroll horizontal |

Byte 2 = valor 0-255. Checksum = XOR(byte0, byte1, byte2, byte3).

### 5.3 Mensajes del servidor al APK (JSON)

```json
{"type":"init","is_pro_version":true}
{"type":"switch_profile","profile":"default","window":"chrome.exe"}
{"type":"config_updated"}
{"type":"theme_update","themes":{...}}
{"type":"pro_update","is_pro_version":true}
```

---

## 6. CONFIGURACIÓN (`config.json`)

El archivo `config.json` se guarda en `%LOCALAPPDATA%/SrLolo/LunaDeck/` (EXE) o junto a `server/` (desarrollo).

### Estructura resumida

```json
{
  "version": 2,
  "perfil_activo": "default",
  "perfiles": {
    "default": {
      "cols": 4,
      "keys": [{"label": "L", "keyCode": 76, "mods": 0}]
    }
  },
  "appSwitch": {
    "enabled": true,
    "rules": [{"exe": "chrome.exe", "profile": "navigation", "label": "Chrome"}]
  },
  "pro_license": false,
  "store_addon_id": "9PNCV2XSK9K8",
  "themes": {
    "pc": { ... },
    "mobile": { ... }
  }
}
```

### Límites en versión gratuita

| Recurso | Límite |
|---|---|
| Perfiles | 3 máximo |
| Columnas en grid | 4 máximo (forzado en `/api/config`) |
| Iconos GIF | Bloqueados en `/api/upload-icon` (código 403) |
| Anuncios | Visibles en web UI y APK |

---

## 7. APLICACIÓN ANDROID (`android/`)

### 7.1 Código fuente

| Archivo | Propósito |
|---|---|
| `MainActivity.kt` | Actividad principal (~3129 líneas): conexión, UI nativa, WebView grid, ciclo de vida, auto-update |
| `LunaWebSocket.kt` | WebSocket OkHttp: envía binario 5 bytes, reconexión automática cada 3s |
| `ScrollPadView.kt` | View táctil personalizada para scroll (0-255, auto-centrado en release) |
| `ConfigParser.kt` | Data classes para el JSON de configuración (`LunaConfig`, `LunaProfile`, `LunaTheme`) |
| `ThemeManager.kt` | 8 temas predefinidos con 20+ colores cada uno |
| `QrScannerActivity.kt` | Escáner QR vía ZXing (CameraX + ML Kit descartados por crashes) |

### 7.2 Build

```bash
cd android
./gradlew assembleDebug
# APK generado en: app/build/outputs/apk/debug/app-debug.apk
# Firmado automáticamente con luna.keystore
```

Dependencias clave: OkHttp 4.12, ZXing 4.3, Coil 2.6, Kotlin Coroutines, AndroidX Core KTX 1.12.

### 7.3 Flujo de conexión

```
App inicia
  ├── ¿IP guardada? -> No -> Onboarding (WebView local en assets/)
  └── Si
        ├── Socket probe (800ms timeout) a IP:9120
        ├── Si falla -> Onboarding con error
        ├── Si ok
        │     ├── GET /api/config -> perfiles, reglas auto-switch
        │     ├── GET /api/themes -> colores mobile
        │     ├── checkForUpdate() -> PC server /api/version (3s timeout)
        │     ├── checkForUpdateFromWeb() -> GitHub Pages version.json (5s timeout)
        │     ├── Crea LunaWebSocket (ws://IP:9120/ws)
        │     ├── Muestra UI nativa (header + profiles + grid/sliders + connInfo)
        │     └── Polling cada 5s: GET /api/config -> push a WebView grid
        └── (en onResume) checkForUpdateFromWeb() si pasaron >24h
```

### 7.4 UI Nativa (Kotlin/XML)

- **Header**: status dot, mode toggle (grid/sliders), disconnect, QR scan, menu
- **Profile bar**: chips horizontales scrolleables, cambian perfil activo
- **Content area**: GridLayout (teclas macro) o sliders (volumen/brillo/scroll), toggle con boton
- **ScrollPads**: custom View con thumb, valor 0-255, auto-centrado al soltar
- **uiToggleBtn**: floating overlay top|end, oculta header + profiles + connInfo
- **Back button**: siempre revela UI oculta, nunca cierra la app
- **fitsSystemWindows**: en root FrameLayout, system bars flotan sobre el fondo oscuro
- **Idiomas**: EN/ES/PT en onboarding; UI nativa en espanol

### 7.5 Grid WebView (Hybrid)

- Desde v1.7.42, los botones del grid se renderizan en un WebView que carga `/mobile-grid.html` del PC server
- `LunaBridge` (@JavascriptInterface) recibe taps/presiones y los envia al WebSocket nativo
- Config polling envia JSON al WebView via `updateConfig()`
- Sliders y scrollpads permanecen nativos (no en WebView)

### 7.6 Temas (8 predefinidos)

Oscuro, Claro, Azul Nocturno, Neon Verde, Magenta, Ambar, Rojo Gaming, Purpura.

- Cada tema tiene 20+ colores (fondos, textos, acentos, botones, sliders, scrollpads)
- Tema personalizado via editor en dashboard del PC server (se envia por WebSocket al APK)
- APK aplica colores nativamente (GradientDrawable, RippleDrawable)

### 7.7 Auto-update (Sistema Renovado v1.7.60)

**Dos fuentes de verificacion:**

1. **PC Server** (`/api/version`): detecta actualizacion cuando el servidor local reporta version superior
2. **GitHub Pages** (`version.json`): fuente principal, formato enriquecido

**Formato de version.json:**
```json
{
  "latest": "1.7.60",
  "url": "https://sr-lolo.github.io/luna/Luna.apk",
  "fallback_url": "https://github.com/Sr-Lolo/luna/releases/latest/download/Luna.apk",
  "sha256": "",
  "min_version": "1.0.0",
  "force_update": false,
  "changelog": "• Novedades..."
}
```

**Comportamiento:**
- Boton "Ahora no" -> silencia la notificacion por **7 dias** (timestamp `last_update_dismiss`)
- Boton "Actualizar" -> descarga con barra de progreso, verifica SHA-256, instala
- Si SHA-256 no coincide o falla descarga -> reintenta con `fallback_url` (hasta 3 intentos con backoff)
- `force_update: true` -> dialogo sin boton "Ahora no", solo "Actualizar"
- `onResume()` -> check automatico si pasaron >24h desde el ultimo
- Dialogo renovado con layout personalizado: icono app, version, changelog, progreso

### 7.8 Onboarding (offline)

- 3 slides HTML en `assets/onboarding/` con selector de idioma (EN/ES/PT)
- Slide 1: elegir metodo (Wi-Fi / USB)
- Slide 2: descargar PC server (link compartible)
- Slide 3: escanear QR o conexion manual
- Panel de troubleshooting con causas comunes (firewall, ADB, RSA, etc.)
- Funciona sin conexion a internet (primera vez que se abre la app)

---

## 8. GITHUB PAGES (`docs/`)

Repo: `github.com/Sr-Lolo/luna` (solo archivos de distribucion en `main`)

```
sr-lolo.github.io/luna/
  ├── version.json      <- Manifiesto de actualizacion del APK
  ├── Luna.apk          <- APK compilado para descarga
  ├── index.html        <- Pagina de descarga
  ├── ad_pc.html        <- Anuncio Adsterra para web UI PC (468x60)
  └── ad_banner.html    <- Anuncio Adsterra para APK (320x50)
```

- `version.json` se actualiza en cada release
- `index.html` muestra la version actual y enlace de descarga
- Los anuncios se cargan desde `highperformanceformat.com` (red Adsterra)

---

## 9. EMPAQUETADO DEL EXE (PyInstaller)

### 9.1 Build

```bash
cd server
pip install -r requirements.txt
pyinstaller Luna.spec
# EXE generado en: server/dist/Luna.exe
```

### 9.2 `Luna.spec` — parametros clave

- Entry: `src/gui.py`
- Data: `web/`, `web_ad/`, `bin/adb/`, `app.ico`
- Hidden imports: `zeroconf`, `zeroconf._utils.ipaddress`, `zeroconf._handlers.answers`, `queue`, `ctypes`, `winreg`, `urllib.request`
- UPX: habilitado (excepto DLLs con CFG - normal, no es error)
- Console: deshabilitado (GUI)
- Onefile: si

### 9.3 MSIX (Windows Store)

```bash
cd scripts
.\build-msix.ps1
# Genera: LunaDeck_{version}_x64.msix
```

---

## 10. mDNS (descubrimiento en red)

El servidor se registra como `luna.local:9120` via `zeroconf`. El APK puede descubrir el servidor sin necesidad de IP manual (aunque actualmente usa IP directa guardada en SharedPreferences). En redes corporativas, mDNS puede fallar - se mantienen QR + IP manual como fallback.

---

## 11. SINGLE INSTANCE

- Archivo lock en `%TEMP%/luna.lock`
- Detecta procesos zombies via `OpenProcess` + `QueryFullProcessImageNameW`
- Previene ejecucion de multiples instancias
- Variable de entorno `LUNA_PARENT_INSTANCE` para instancias hijas (desde MSIX)

---

## 12. PAIRING Y SEGURIDAD

- El APK se conecta por IP directa (guardada en SharedPreferences)
- El servidor genera un pairing code de 6 digitos
- El QR contiene: `{"type":"luna_pair","uuid":"...","ip":"...","port":9120,"code":"..."}`
- El APK envia el codigo al conectar WebSocket, el servidor valida
- No hay cifrado en WebSocket (HTTP plano) - asume red local confiable

---

## 13. CIERRE Y BANDEJA (PC Server)

- `gui.py` muestra una ventana pywebview apuntando a `http://127.0.0.1:9120/`
- Cerrar la ventana -> minimiza a la bandeja (icono en system tray)
- Click izquierdo en bandeja -> muestra ventana
- Click derecho -> menu: "Mostrar" / "Salir"
- Al hacer clic en "Cerrar" en la UI -> dialogo de confirmacion (minimizar/cerrar/cancelar)
- Si el JS no responde en 5s, se forza el cierre via `PostMessageW`

---

## 14. DEPENDENCIAS

### Python (PC Server)

```
fastapi==0.115.0
websockets==12.0
uvicorn[standard]==0.30.0
keyboard==0.13.5
qrcode==7.4.2
Pillow==10.4.0
screen-brightness-control==0.18.0
pywebview==6.2.1
psutil==6.1.0
zeroconf==0.149.16
pywin32==308
winrt==2.2.0
wmi==1.5.1
ifaddr==0.2.0
```

### Android (Gradle)

- Kotlin 1.9+
- Android SDK 26+ / compileSdk 36
- OkHttp 4.12
- ZXing 4.3 (embarcado via `com.journeyapps:zxing-android-embedded`)
- Coil 2.6
- Kotlin Coroutines
- AndroidX Core KTX 1.12, AppCompat 1.6.1

---

## 15. HISTORIAL DE CAMBIOS CRITICOS

| Fecha | Version | Cambio | Razon |
|---|---|---|---|
| 2026-07-14 | v1.7.55 | Fix `BASE_DIR` con `sys._MEIPASS` en `gui.py` | EXE compilado no encontraba `web/welcome_template.html` |
| 2026-07-14 | v1.7.55 | `if __name__ == "__main__": run()` en `gui.py` | PyInstaller necesita `__main__` para ejecutar |
| 2026-07-14 | v1.7.55 | Icono EXE personalizado | Reemplazado `app.ico` por version propia |
| 2026-07-14 | v1.7.55 | Limpieza de duplicados (~240 MB) | `__pycache__/`, `build/`, `dist_backup/`, `Programa funcionable/` |
| 2026-07-20 | **v1.7.60** | **Sistema de auto-update renovado** | SHA-256, retry con fallback, force update, cooldown 7 dias |
| 2026-07-20 | v1.7.60 | Dialogo de actualizacion renovado | Layout personalizado con changelog, barra de progreso, icono |
| 2026-07-20 | v1.7.60 | `version.json` enriquecido | Nuevos campos: sha256, fallback_url, force_update, changelog |
| 2026-07-20 | v1.7.60 | Check periodico en `onResume()` | 24h entre chequeos automaticos |
| 2026-07-20 | v1.7.60 | `APK_VERSION` como constante en server.py | Reemplazado hardcoding inline |

---

## 16. READY FOR DISTRIBUTION — ANALISIS

### Listo

- PC Server (EXE) funcional en Windows 10/11 x64
- APK funcional en Android 8.0+ (API 26+)
- WebSocket binario estable con reconexion automatica
- Config polling mantiene grid sincronizado
- Auto-update del APK desde GitHub Pages
- Onboarding offline completo con 3 idiomas
- Temas nativos (8 predefinidos + personalizados via PC)
- Anuncios Adsterra integrados (web UI + APK WebView)
- Licencia Pro via Microsoft Store
- Single instance con deteccion de procesos zombies
- mDNS para descubrimiento automatico

### Consideraciones antes de distribucion masiva

| Aspecto | Estado | Recomendacion |
|---|---|---|
| **Firma del APK** | Firmado con keystore local (debug) | Generar keystore de release con clave segura antes de distribuir |
| **Play Store** | No publicado | No es necesario para distribucion directa |
| **Windows Store** | MSIX empaquetado, no publicado | Publicar en Store para usuarios que prefieren instalacion oficial |
| **WebView2 en Win10** | Requiere descarga manual | Incluir enlace en la pagina de descarga |
| **Permisos Android** | Todos justificados | `ACCESS_FINE_LOCATION` solo para Wi-Fi discovery; se puede hacer opcional |
| **Adsterra** | Scripts de terceros | Pueden ralentizar carga inicial; considerar self-hosted ads |
| **Error handling** | Manejo basico (try/catch silencioso en mayoria) | Mejorar logging y reporte de errores |
| **Actualizacion del EXE** | No implementada | Solo el APK tiene auto-update; el EXE requiere descarga manual |
| **Seguridad WebSocket** | Sin cifrado (ws://) | Aceptable para red local; no usar en redes no confiables |
| **Documentacion** | MANIFEST.md + AGENTS.md | Suficiente para desarrolladores |

### Veredicto

**Si, esta listo para distribucion** en el estado actual para usuarios que:
1. Tengan Windows 10/11 y Android 8.0+
2. Esten dispuestos a instalar el APK por sideload
3. Usen el producto en su red local (Wi-Fi domestico)

**No esta listo** para:
- Distribucion en Play Store (falta firma de release, politicas de permisos)
- Usuarios que requieran actualizacion automatica del EXE de PC
- Redes corporativas con politicas restrictivas (mDNS, firewall)

---

## 17. ESTRUCTURA DEL PROYECTO

```
LunaDeck v1.7.55/
├── MANIFEST.md                    <- Este archivo
├── AGENTS.md                      <- Knowledge base del proyecto
├── .gitignore
├── assets/
│   └── brand/                     <- Iconos y logotipos fuente (PNG, PSD)
├── android/                       <- App Android (Kotlin + Gradle)
│   ├── app/
│   │   ├── build.gradle.kts       <- versionName = "1.7.60"
│   │   └── src/main/
│   │       ├── AndroidManifest.xml <- Permisos, FileProvider, activities
│   │       ├── java/com/luna/app/ <- Codigo Kotlin (6 clases)
│   │       ├── res/               <- Layouts, strings (3 idiomas), temas, colores
│   │       └── assets/onboarding/ <- 3-slide HTML flow offline
│   └── build/                     <- APK generado aqui
├── docs/                          <- GitHub Pages (version.json, Luna.apk, index.html, ad_*.html)
├── msix-package/                  <- Empaquetado MSIX (Windows Store)
├── scripts/                       <- Scripts de build (bat, ps1)
└── server/
    ├── main.py                    <- Entry point
    ├── app.ico                    <- Icono del EXE
    ├── Luna.spec                  <- Config PyInstaller
    ├── requirements.txt           <- Dependencias Python (14 paquetes)
    ├── src/                       <- Codigo fuente Python (8 modulos)
    ├── web/                       <- Frontend web (index, dashboard, ayuda, mobile-grid)
    ├── web_ad/                    <- Anuncio Adsterra (index.html + style.css)
    └── dist/                      <- EXE compilado (Luna.exe)
```

---

## 18. NOTAS PARA PROGRAMADORES FUTUROS

1. **El APK Android es el cliente principal**, no el navegador web. La UI web es secundaria.
2. **El protocolo binario (5 bytes) es critico** - cualquier cambio debe mantener compatibilidad hacia atras o versionar el WebSocket.
3. **pywebview** es delicado con versiones de Python y WebView2 - probar en Windows 10/11 antes de distribuir.
4. **mDNS** (zeroconf) a veces falla en redes corporativas - mantener el QR code + entrada manual como fallback.
5. **Los temas se definen en dos lugares**: PC (CSS variables en web) y Mobile (ThemeManager.kt + config.json).
6. **Auto-update del APK** verifica dos fuentes: el servidor PC conectado y GitHub Pages (con SHA-256, retry y fallback).
7. **La tecla `LAUNCH_KEYCODE_MIN = 200`** en `server.py` distingue entre teclas normales y lanzadores de apps.
8. **No hay service worker** - la PWA web no es instalable offline.
9. **Gradle wrapper** esta incluido - no es necesario tener Gradle instalado globalmente.
10. **UPX** comprime el EXE ~40% pero algunos DLLs no son compresibles (es normal, no es error).
11. **CRITICO - Modo frozen**: Cada vez que se lea un archivo o ruta en `gui.py`, usar `getattr(sys, 'frozen', False)` para elegir entre `sys._MEIPASS` (frozen) y `os.path.dirname(...)` (desarrollo). Ejemplos: `_build_welcome_html()`, `_get_icon_path()`, `BASE_DIR`.
12. **CRITICO - Entry point**: `gui.py` necesita `if __name__ == "__main__": run()` al final. Sin esto, PyInstaller compila el EXE pero no ejecuta la app.
13. **SharedPreferences del APK**: las claves `server_ip`, `theme`, `keep_screen_on`, `notifications`, `ads_removed`, `luna_lang`, `last_update_check_time`, `last_update_dismiss` son persistentes.
14. **version.json** debe actualizarse manualmente en cada release junto con `build.gradle.kts` y `server.py`.

---

## 19. DEBUG Y SOLUCION DE PROBLEMAS COMUNES

### 19.1 El EXE no abre (sale silenciosamente)

**Verificacion**: Reconstruir con `console=True` en `Luna.spec` y ejecutar desde terminal.

**Causa probable**: `gui.py` no tiene `if __name__ == "__main__": run()`.

### 19.2 El servidor responde pero la ventana no se ve

- pywebview requiere **WebView2 Runtime**
- Verificar que `http://127.0.0.1:9120/` responda en el navegador

### 19.3 El APK no conecta

- Verificar que el PC este en la misma red Wi-Fi
- Probar firewall: `netsh advfirewall firewall add rule name="LunaDeck" dir=in action=allow protocol=TCP localport=9120`
- Probar conexion USB con `adb reverse tcp:9120 tcp:9120`

### 19.4 El APK no detecta actualizacion

- Verificar que `https://sr-lolo.github.io/luna/version.json` sea accesible
- Verificar que `latest` sea mayor que el `versionName` del APK actual
- La APK guarda `last_update_dismiss` - esperar 7 dias o borrar datos de la app

### 19.5 WebView2Loader.dll no compresible (UPX warning)

Es normal. UPX deshabilita compresion para DLLs con CFG (Control Flow Guard). No afecta el funcionamiento.

---

*Fin del manifiesto - Documento generado el 20/07/2026. Version mantenida manualmente. Actualizar este archivo cada vez que se haga un cambio critico en la arquitectura o proceso de build.*
