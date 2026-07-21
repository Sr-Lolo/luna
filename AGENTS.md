# AGENTS.md — Luna Project Knowledge Base

## Goal
Native Android APK companion for Luna remote keyboard with WebSocket + HTTP config, auto-update via GitHub Pages, and offline onboarding. APK is fully independent of PC server for UI rendering (Kotlin/XML). PC server only serves WebSocket commands + HTTP `/api/config`.

## Constraints & Preferences
- All UI text in Spanish
- `fitsSystemWindows` on root FrameLayout + transparent status/nav bar — system bars never overlap header/footer
- Back button never exits app; reveals hidden UI instead
- QR scanner uses zxing (CameraX+ML Kit kept crashing)
- APK works offline on first launch (local onboarding HTML in `assets/`)
- mDNS (`luna.local`) registered via `zeroconf` in server.py
- Luna.exe lock file prevents double instance (stale detection via PID + OpenProcess)
- Mobile APK banner shows 5s on HTTP web page, then persistent tab

## Progress
### Done
- v1.5.2–v1.5.9: Legacy WebView-based UI (CSS/JS injection over PC server), landscape fix, theme toggle, offline onboarding setup
- v1.6.0–v1.6.2: Offline 3-slide onboarding with bridge methods, retry/manual/finish on connection fail, slide 2 replaced with share sheet link
- **v1.7.0**: Complete native UI rewrite (Kotlin/XML). APK no longer loads PC server HTML/JS/CSS. Native header, GridLayout grid, SeekBar sliders + ScrollPadView, profile chips. WebSocket via OkHttp binary 5-byte protocol. Config polling via HTTP `/api/config` every 5s. Auto-update checks in `onConfigLoaded()`. `fitsSystemWindows` on root FrameLayout. `uiToggleBtn` as floating overlay (top|end) hiding headerBar, profileBarScroll, connInfo. Removed size slider row. Removed `connQrBtn`. Removed `showQrModal()`, `qrCodeBitmap()`, `updateButtonSize()`. `onKeyDown(KEYCODE_BACK)` shows hidden UI, never exits.
- **v1.8.0**: Theme editor Fase 2. `themes` section in config (pc + mobile color presets). `GET/POST /api/themes` endpoints. WebSocket `theme_update` broadcast to connected APKs. Theme editor button (🎨 Temas) in dashboard opens modal with two tabs (Tema PC / Tema Móvil). Each tab has grouped color picker fields with hex input. Custom PC theme applied via injected `:root` CSS variables. APK `LunaWebSocket` handles `theme_update`, parses mobile colors into `LunaTheme("custom")`, applies via `applyTheme()`. APK also fetches `/api/themes` on initial connect.
- **v1.7.32**: Complete architecture revert to fully native grid buttons. Removed all `gridWebView`/WebViewClient code, PC-driven theme functions (`fetchAndApplyTheme`, `parseMobileTheme`, `handleThemeUpdateFromWs`, `applyGridCssTheme`), and `onThemeUpdate` callback from `LunaWebSocket`. Added native `buildGrid()`/`rebuildGrid()` that creates Button children in GridLayout with touch press/release/tap via MotionEvent. Theme colors applied natively via GradientDrawable on grid buttons. Theme selection exclusively from app's "Diseños" dialog (8 hardcoded themes). Pro license/handleProStatus code untouched.
- **v1.7.33–v1.7.38**: Multiple attempts to display icons/GIFs in grid cells. Started with Coil `load()` on ImageView inside FrameLayout (FrameLayout + ImageView + TextView). Icon loading worked but touch handling was unreliable — GIF cells were not clickable because GIF consumed touch events. Attempted `isClickable=false` on children, `onInterceptTouchEvent=true` on FrameLayout, Button+foreground drawable — none resolved the GIF click issue. FrameLayout approach discarded.
- **v1.7.39**: Option C — pure Button with Coil coroutine icon loading. `createGridCell` returns a `Button` directly (no FrameLayout wrapper). Icon loaded via `Coil.imageLoader().execute()` in a coroutine, sets `btn.background = drawable` on success. Non-icon buttons use `GradientDrawable` background. Icon buttons skip theme recoloring in `applyTheme()` (checked via `btn.background !is GradientDrawable`). `setGradientBg()` helper replaces `applyCellBackground()`. `scope.launch` with `isAttachedToWindow` guard prevents updating orphaned views. Removed ImageView/TextView/FrameLayout from grid cells entirely.
- **v1.7.40**: Fixed icon/GIF touch issues. `RippleDrawable` foreground on all grid buttons provides visual press feedback regardless of background type. GIFs decoded as static frames via `GifDecoder.Factory(false)` to prevent touch interference. `playSoundEffect(CLICK)` on press restores native button click sound. `applyTheme()` updates ripple foreground color on theme change.
- **v1.7.41**: FrameLayout+ImageView wrapper for all grid cells. `onInterceptTouchEvent=true` prevents GIF animation from consuming touch events. `RippleDrawable` foreground with `GradientDrawable` shape mask ensures ripple visible on all backgrounds. ImageView loads icons/GIFs via Coil (animated GIFs supported). TextView for labels when no icon. Always sends WebSocket command even when `keyCode=0` (sound-only buttons). Removed `setGradientBg()` — FrameLayout background uses inline `GradientDrawable`.
- **v1.7.42**: Hybrid architecture — WebView grid + native shell. New `/mobile-grid` endpoint on PC server serves minimal grid HTML. `gridWebView` replaces `gridLayout`. `LunaBridge` `@JavascriptInterface` routes key events to native WebSocket. Removed all native grid rendering (`ICON_MAP`, `buildGrid`, `rebuildGrid`, `createGridCell`, `setGradientBg`, `resolveIconUrl`). Config polling pushes config JSON to WebView via `updateConfig()`. Profile switching calls `switchProfile()` in WebView. Sliders/scrollpads remain native.
- **v1.7.43**: Fixed /mobile-grid 404. Moved mobile-grid HTML from inline route to static file `web/mobile-grid.html` served by StaticFiles mount. APK loads `/mobile-grid.html`. Removed dedicated route from server.py.

- **v1.7.60**: Update system renovation. `version.json` enriched with `sha256`, `fallback_url`, `force_update`, `changelog`. Custom dialog layout with changelog + progress. SHA-256 verification before install. Retry with backoff (2s/4s/8s) and fallback URL. Force update mode (non-dismissable dialog). "Not now" uses 7-day timestamp cooldown instead of permanent ignore. Periodic check on `onResume()` if >24h. `APK_VERSION` constant extracted in server.py.

### Blocked
- (none)

## Key Decisions
- **Native UI (Kotlin/XML)** replaces WebView-loaded PC server UI: clean separation, no CSS/JS injection, full independence
- **OkHttp WebSocket native**: sends same 5-byte binary protocol, receives `switch_profile` JSON, heartbeat via ping interval
- **Config polling every 5s** via GET `/api/config`: keeps grid/profile layout in sync with PC server
- **GridManager** renders buttons in GridLayout with touch press/release/tap using same binary messages
- **ScrollPadView** custom View: touch tracking with auto-centering on release, values 0–255
- **fitsSystemWindows on root FrameLayout** (not on `nativeUi`): works even when `nativeUi` starts `GONE` during onboarding
- **transparent statusBarColor/navigationBarColor**: system bars float over dark app background
- **uiToggleBtn as floating overlay** (layout_gravity="top|end"): always visible even when header/profile/footer hidden
- **Back button reveals UI**, does not exit app

## Next Steps
1. Build v1.7.39 APK (`gradlew assembleDebug`) ✓
2. Copy APK to `Luna.apk` (project root) + `docs/Luna.apk`
3. Commit and push
4. Upload APK to GitHub Release v1.7.39 ✓
**v1.7.40**: Same process — build, copy, commit, push, release ✓
**v1.7.41**: Same process — build, copy, commit, push, release ✓
**v1.7.42**: Same process — build, copy, commit, push, release ✓
**v1.7.43**: Same process — build, copy, commit, push, release ✓
**v1.7.60**: Update system renovation — SHA-256, retry + fallback, force update, 7-day cooldown, periodic onResume(), custom dialog with changelog ✓

## Critical Context
- APK onboarding loads from `file:///android_asset/onboarding/index.html` when no IP saved
- When IP saved: socket check (800ms) → `fetchConfigAndConnect()` → `onConfigLoaded()`:
  - `checkForUpdate()` (PC server `/api/version`)
  - `checkForUpdateFromWeb()` (GitHub Pages `version.json`)
  - Creates `GridManager`, `LunaWebSocket`, shows native UI
  - Starts config polling every 5s
- `LunaWebSocket` connects to `ws://IP:9120/ws`, sends binary 5-byte commands, receives `switch_profile` JSON
- `GridManager.handleTouch()`: modifier keys → tap; normal keys → press on DOWN, release on UP/CANCEL
- Scroll pads: value 0–255, center 128, auto-reset to center on release
- Theme toggle: `#0D0D0D` (dark) / `#F5F5F5` (light)
- UI toggle hides: headerBar, profileBarScroll, connInfo; contentArea expands
- `onKeyDown(KEYCODE_BACK)`: reveals hidden UI, returns true (never calls super)
- Remote version file: `https://sr-lolo.github.io/luna/version.json`
- Current version: `1.7.60`

## Relevant Files
- `APK LunaDeck Offline (Alpha)/app/src/main/java/com/luna/app/MainActivity.kt`: routing, socket check, `onConfigLoaded()` with update checks, `showNativeUI()`, `WebAppInterface`, `downloadAndInstallApk()`. `setupGridWebView()` configures grid WebView + `LunaBridge` JS interface. `switchGridProfile()` calls `switchProfile()` in WebView. `buildGrid()`/`rebuildGrid()`/`createGridCell()` removed (legacy native grid).
- `APK LunaDeck Offline (Alpha)/app/src/main/java/com/luna/app/LunaWebSocket.kt`: OkHttp WebSocket — connect, sendKeyPress/Release/Tap, sendSlider, auto-reconnect 3s
- `APK LunaDeck Offline (Alpha)/app/src/main/java/com/luna/app/ScrollPadView.kt`: custom View for scroll pads — touch tracking, thumb, value 0–255, auto-center
- `APK LunaDeck Offline (Alpha)/app/src/main/res/layout/activity_main.xml`: FrameLayout root with fitsSystemWindows, WebView (onboarding), nativeUi (headerBar + profileBarScroll + contentArea with grid/sliders + connInfo), spinnerOverlay, uiToggleBtn overlay
- `APK LunaDeck Offline (Alpha)/app/src/main/res/values/themes.xml`: `Theme.Luna` with NoActionBar, transparent statusBarColor/navigationBarColor
- `APK LunaDeck Offline (Alpha)/app/src/main/assets/onboarding/`: 3-slide offline HTML flow (unchanged from v1.6.x)
- `luna/host/src/server.py`: `apk_version` = "1.7.0"
- `luna/host/src/server.py`: mDNS via lifespan, `/api/ip` port 9120, `/api/version` returns apk_version, `/apk` redirects to GitHub Pages, `/api/qr` and `/api/qr-apk` QR endpoints with lazy qrcode/PIL, **`/api/pro-status`** returns `{"pro": true/false}` from `pro_license` in config, **`/web_ad`** mount serves `web_ad/` static files
- `luna/host/src/server.py`: Close dialog uses JS polling + PostMessageW; `_on_closing` has 5s fallback timer for force-close if no JS response
- `luna/host/web/`: Ad banner container (#ad-banner) with iframe (#ad-frame) loading /web_ad/; shown only on desktop when pro_license=false; close button adds `.ad-banner-hidden` (opacity 0 with 0.4s ease transition)
- `luna/host/web/app.js`: `fetch('/api/pro-status')` on load → shows banner if `!data.pro`; dismissible via close button
- `luna/host/web_ad/`: Standalone 300×250 ad page (index.html + style.css) — isolate Adsterra scripts from main UI
- `luna/host/src/config_manager.py`: `_DEFAULT["pro_license"] = False` — default value for Microsoft Store purchase status
- `luna/host/Luna.spec`: datas includes `web_ad/` directory
- `docs/version.json`: `{"latest":"1.7.0",...}`
- `docs/index.html`: download page
- `APK LunaDeck Offline (Alpha)/app/src/main/java/com/luna/app/LunaWebSocket.kt`: handles `{"type":"init","is_pro_version":true/false}` from PC WebSocket → calls `onProStatus()`
- `APK LunaDeck Offline (Alpha)/app/src/main/java/com/luna/app/MainActivity.kt`: `handleProStatus()` receives Pro flag, sets `adsRemoved=true`, hides AdMob banner, persists to SharedPreferences
- **Auto-update v1.7.60+**: SHA-256 verification, retry with fallback URL (3 attempts, backoff 2s/4s/8s), force_update mode, 7-day cooldown on "Not now", periodic check on onResume() (>24h), custom dialog with changelog + progress bar
