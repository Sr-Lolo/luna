const PROTO = {
  MSG_KEY: 0x01, MSG_SLIDER: 0x02,
  ACT_TAP: 0x03,
  MOD_NONE: 0x00, MOD_CTRL: 0x01, MOD_SHIFT: 0x02, MOD_ALT: 0x04,
  SLIDER_VOLUME: 0x01, SLIDER_BRIGHTNESS: 0x02,
  SLIDER_SCROLL_V: 0x03, SLIDER_SCROLL_H: 0x04,
};

const KC = {
  L: 0x4C, Z: 0x5A, X: 0x58, C: 0x43, V: 0x56,
  W: 0x57, A: 0x41, S: 0x53, D: 0x44,
  Q: 0x51, E: 0x45, R: 0x52, F: 0x46,
  K1: 0x31, K2: 0x32, K3: 0x33, K4: 0x34,
  SPACE: 0x20, TAB: 0x09,
  BACKSPACE: 0x08, ENTER: 0x0D, ESCAPE: 0x1B, SHIFT: 0x10,
  LEFT: 0x25, RIGHT: 0x27, UP: 0x26, DOWN: 0x28,
};

let profiles = null;
let appSwitchRules = [];

const HARDCODED_PROFILES = {
  default: { keys: [
    { label: 'L', key: KC.L, mods: PROTO.MOD_NONE, cls: '' },
    { label: 'Z', key: KC.Z, mods: PROTO.MOD_NONE, cls: '' },
    { label: 'Ctrl+C', key: KC.C, mods: PROTO.MOD_CTRL, cls: 'mod' },
    { label: 'Ctrl+V', key: KC.V, mods: PROTO.MOD_CTRL, cls: 'mod' },
    { label: 'W', key: KC.W, mods: PROTO.MOD_NONE, cls: '' },
    { label: 'A', key: KC.A, mods: PROTO.MOD_NONE, cls: '' },
    { label: 'S', key: KC.S, mods: PROTO.MOD_NONE, cls: '' },
    { label: 'D', key: KC.D, mods: PROTO.MOD_NONE, cls: '' },
    { label: '\u232B', key: KC.BACKSPACE, mods: PROTO.MOD_NONE, cls: 'special' },
    { label: '\u23CE', key: KC.ENTER, mods: PROTO.MOD_NONE, cls: 'special' },
    { label: '\u238B', key: KC.ESCAPE, mods: PROTO.MOD_NONE, cls: 'special' },
    { label: '\u21E7', key: KC.SHIFT, mods: PROTO.MOD_NONE, cls: 'special' },
    { label: '\u25C1', key: KC.LEFT, mods: PROTO.MOD_NONE, cls: 'arrow' },
    { label: '\u25B2', key: KC.UP, mods: PROTO.MOD_NONE, cls: 'arrow' },
    { label: '\u25BC', key: KC.DOWN, mods: PROTO.MOD_NONE, cls: 'arrow' },
    { label: '\u25B7', key: KC.RIGHT, mods: PROTO.MOD_NONE, cls: 'arrow' },
  ],
    cols: 4 },
  gaming: { keys: [
    { label: 'W', key: KC.W, mods: PROTO.MOD_NONE, cls: '' },
    { label: 'A', key: KC.A, mods: PROTO.MOD_NONE, cls: '' },
    { label: 'S', key: KC.S, mods: PROTO.MOD_NONE, cls: '' },
    { label: 'D', key: KC.D, mods: PROTO.MOD_NONE, cls: '' },
    { label: 'Q', key: KC.Q, mods: PROTO.MOD_NONE, cls: '' },
    { label: 'E', key: KC.E, mods: PROTO.MOD_NONE, cls: '' },
    { label: 'R', key: KC.R, mods: PROTO.MOD_NONE, cls: '' },
    { label: 'F', key: KC.F, mods: PROTO.MOD_NONE, cls: '' },
    { label: '\u21E7', key: KC.SHIFT, mods: PROTO.MOD_NONE, cls: 'special' },
    { label: '\u238B', key: KC.ESCAPE, mods: PROTO.MOD_NONE, cls: 'special' },
    { label: 'Tab', key: KC.TAB, mods: PROTO.MOD_NONE, cls: 'special' },
    { label: '\u2423', key: KC.SPACE, mods: PROTO.MOD_NONE, cls: 'special' },
    { label: '1', key: KC.K1, mods: PROTO.MOD_NONE, cls: '' },
    { label: '2', key: KC.K2, mods: PROTO.MOD_NONE, cls: '' },
    { label: '3', key: KC.K3, mods: PROTO.MOD_NONE, cls: '' },
    { label: '4', key: KC.K4, mods: PROTO.MOD_NONE, cls: '' },
  ],
    cols: 4 },
  editing: { keys: [
    { label: 'Z', key: KC.Z, mods: PROTO.MOD_CTRL, cls: 'mod' },
    { label: 'X', key: KC.X, mods: PROTO.MOD_CTRL, cls: 'mod' },
    { label: 'C', key: KC.C, mods: PROTO.MOD_CTRL, cls: 'mod' },
    { label: 'V', key: KC.V, mods: PROTO.MOD_CTRL, cls: 'mod' },
    { label: 'S', key: KC.S, mods: PROTO.MOD_CTRL, cls: 'mod' },
    { label: 'A', key: KC.A, mods: PROTO.MOD_CTRL, cls: 'mod' },
    { label: 'F', key: KC.F, mods: PROTO.MOD_CTRL, cls: 'mod' },
    { label: 'D', key: KC.D, mods: PROTO.MOD_CTRL, cls: 'mod' },
    { label: '\u232B', key: KC.BACKSPACE, mods: PROTO.MOD_NONE, cls: 'special' },
    { label: '\u23CE', key: KC.ENTER, mods: PROTO.MOD_NONE, cls: 'special' },
    { label: '\u238B', key: KC.ESCAPE, mods: PROTO.MOD_NONE, cls: 'special' },
    { label: '\u21E7', key: KC.SHIFT, mods: PROTO.MOD_NONE, cls: 'special' },
    { label: '\u25C1', key: KC.LEFT, mods: PROTO.MOD_NONE, cls: 'arrow' },
    { label: '\u25B2', key: KC.UP, mods: PROTO.MOD_NONE, cls: 'arrow' },
    { label: '\u25BC', key: KC.DOWN, mods: PROTO.MOD_NONE, cls: 'arrow' },
    { label: '\u25B7', key: KC.RIGHT, mods: PROTO.MOD_NONE, cls: 'arrow' },
  ],
    cols: 4 },
  streaming: { keys: [
    { label: 'PTT', key: 124, mods: 0, cls: '' },
    { label: 'MicSil', key: 125, mods: 0, cls: '' },
    { label: 'Vol+', key: 175, mods: 0, cls: '' },
    { label: 'Vol-', key: 174, mods: 0, cls: '' },
    { label: 'Esc1', key: 126, mods: 0, cls: '' },
    { label: 'Esc2', key: 127, mods: 0, cls: '' },
    { label: 'Esc3', key: 128, mods: 0, cls: '' },
    { label: 'Esc4', key: 129, mods: 0, cls: '' },
    { label: 'Str On', key: 130, mods: 0, cls: '' },
    { label: 'Str Off', key: 131, mods: 0, cls: '' },
    { label: 'Rec On', key: 132, mods: 0, cls: '' },
    { label: 'Rec Off', key: 133, mods: 0, cls: '' },
    { label: 'Silen', key: 173, mods: 0, cls: '' },
    { label: 'P/P', key: 179, mods: 0, cls: '' },
    { label: 'Next', key: 176, mods: 0, cls: '' },
    { label: 'Prev', key: 177, mods: 0, cls: '' },
  ], cols: 4 },
  navigation: { keys: [
    { label: '+Pest', key: 84, mods: 1, cls: 'mod' },
    { label: 'Cerrar', key: 87, mods: 1, cls: 'mod' },
    { label: 'Sig', key: 9, mods: 1, cls: 'mod' },
    { label: 'Ant', key: 9, mods: 3, cls: 'mod' },
    { label: 'URL', key: 76, mods: 1, cls: 'mod' },
    { label: 'Recarg', key: 82, mods: 1, cls: 'mod' },
    { label: 'Atr\u00E1s', key: 37, mods: 4, cls: 'mod' },
    { label: 'Adel', key: 39, mods: 4, cls: 'mod' },
    { label: 'Reabrir', key: 84, mods: 3, cls: 'mod' },
    { label: 'Fav', key: 68, mods: 1, cls: 'mod' },
    { label: 'Desc', key: 74, mods: 1, cls: 'mod' },
    { label: 'Hist', key: 72, mods: 1, cls: 'mod' },
    { label: 'Buscar', key: 70, mods: 1, cls: 'mod' },
    { label: 'F5', key: 116, mods: 0, cls: '' },
    { label: 'F11', key: 122, mods: 0, cls: '' },
    { label: 'Esc', key: 27, mods: 0, cls: 'special' },
  ], cols: 4 },
  media: { keys: [
    { label: '\u23EF', key: 32, mods: 0, cls: 'special' },
    { label: '\u23ED', key: 39, mods: 1, cls: 'mod' },
    { label: '\u23EE', key: 37, mods: 1, cls: 'mod' },
    { label: 'Vol\u2191', key: 38, mods: 0, cls: '' },
    { label: 'Vol\u2193', key: 40, mods: 0, cls: '' },
    { label: 'Mute', key: 77, mods: 0, cls: '' },
    { label: 'F11', key: 122, mods: 0, cls: '' },
    { label: 'Esc', key: 27, mods: 0, cls: 'special' },
    { label: 'S', key: 83, mods: 0, cls: '' },
    { label: 'L', key: 76, mods: 0, cls: '' },
    { label: 'R', key: 82, mods: 0, cls: '' },
    { label: 'T', key: 84, mods: 0, cls: '' },
    { label: '---', key: 0, mods: 0, cls: '' },
    { label: '---', key: 0, mods: 0, cls: '' },
    { label: '---', key: 0, mods: 0, cls: '' },
    { label: '---', key: 0, mods: 0, cls: '' },
  ], cols: 4 },
  numpad: { keys: [
    { label: '7', key: 103, mods: 0, cls: '' },
    { label: '8', key: 104, mods: 0, cls: '' },
    { label: '9', key: 105, mods: 0, cls: '' },
    { label: '\u00F7', key: 111, mods: 0, cls: '' },
    { label: '4', key: 100, mods: 0, cls: '' },
    { label: '5', key: 101, mods: 0, cls: '' },
    { label: '6', key: 102, mods: 0, cls: '' },
    { label: '\u00D7', key: 106, mods: 0, cls: '' },
    { label: '1', key: 97, mods: 0, cls: '' },
    { label: '2', key: 98, mods: 0, cls: '' },
    { label: '3', key: 99, mods: 0, cls: '' },
    { label: '\u2212', key: 109, mods: 0, cls: '' },
    { label: '0', key: 96, mods: 0, cls: '' },
    { label: '.', key: 110, mods: 0, cls: '' },
    { label: '+', key: 107, mods: 0, cls: '' },
    { label: '\u23CE', key: 13, mods: 0, cls: 'special' },
  ], cols: 4 },
};


const canvas = document.getElementById('canvas');
const slidersCanvas = document.getElementById('sliders-canvas');
const dot = document.getElementById('dot');
const statusText = document.getElementById('status-text');
const profileBar = document.getElementById('profile-bar');
const presetBar = document.getElementById('preset-bar');

let ws = null;
let reconnectTimer = null;
let reconnectAttempt = 0;
let wakeLock = null;
let currentProfile = 'default';
let currentMode = 'grid';
let autoSwitchEnabled = true;

const SLIDER_CONFIG = {
  volume: { el: 'slider-volume', val: 'volume-value', id: PROTO.SLIDER_VOLUME, units: '%', factor: 100/255 },
  brightness: { el: 'slider-brightness', val: 'brightness-value', id: PROTO.SLIDER_BRIGHTNESS, units: '%', factor: 100/255   },
};

function convertKey(k) {
  let cls = '';
  if (k.mods & 1) cls = 'mod';
  else if ([8, 9, 13, 16, 27, 32].includes(k.keyCode)) cls = 'special';
  else if (k.keyCode >= 37 && k.keyCode <= 40) cls = 'arrow';
  return { label: k.label, key: k.keyCode, mods: k.mods, cls };
}

async function loadConfig() {
  try {
    const r = await fetch('/api/config');
    const data = await r.json();
    lastConfigJSON = JSON.stringify(data);
    const p = {};
    Object.keys(data.perfiles).forEach(name => {
      const per = data.perfiles[name];
      p[name] = { keys: (per.keys || []).map(convertKey), cols: per.cols || 4 };
    });
    profiles = p;
    if (data.perfil_activo && profiles[data.perfil_activo]) {
      currentProfile = data.perfil_activo;
    }
    appSwitchRules = (data.appSwitch && data.appSwitch.rules) || [];
  } catch(e) {
    profiles = HARDCODED_PROFILES;
  }
  buildProfileChips();
  buildPresetChips();
  renderButtons();
}

let lastConfigJSON = '';

async function pollConfig() {
  try {
    const r = await fetch('/api/config');
    const data = await r.json();
    const json = JSON.stringify(data);
    if (json === lastConfigJSON) return;
    lastConfigJSON = json;
    const p = {};
    Object.keys(data.perfiles).forEach(name => {
      const per = data.perfiles[name];
      p[name] = { keys: (per.keys || []).map(convertKey), cols: per.cols || 4 };
    });
    profiles = p;
    if (data.perfil_activo && profiles[data.perfil_activo]) {
      currentProfile = data.perfil_activo;
    }
    appSwitchRules = (data.appSwitch && data.appSwitch.rules) || [];
    buildProfileChips();
    buildPresetChips();
    renderButtons();
  } catch(e) {
  }
}

function buildProfileChips() {
  profileBar.innerHTML = '';
  Object.keys(profiles).forEach((name) => {
    const chip = document.createElement('button');
    chip.className = 'profile-chip' + (name === currentProfile ? ' chip-active' : '');
    chip.dataset.profile = name;
    chip.textContent = name.charAt(0).toUpperCase() + name.slice(1);
    chip.addEventListener('click', () => switchProfile(name));
    profileBar.appendChild(chip);
  });
  profileBar.classList.remove('profile-hidden');
}

function buildPresetChips() {
  presetBar.innerHTML = '';
  const labeled = appSwitchRules.filter(r => r.label && r.profile && profiles[r.profile]);
  if (!labeled.length) { presetBar.classList.add('preset-hidden'); return; }
  presetBar.classList.remove('preset-hidden');
  labeled.forEach((rule) => {
    const chip = document.createElement('button');
    chip.className = 'preset-chip';
    const label = document.createElement('span');
    label.className = 'preset-label';
    label.textContent = rule.label;
    chip.appendChild(label);
    const arrow = document.createElement('span');
    arrow.className = 'preset-arrow';
    arrow.textContent = '\u2192 ' + rule.profile.charAt(0).toUpperCase() + rule.profile.slice(1);
    chip.appendChild(arrow);
    chip.addEventListener('click', () => switchProfile(rule.profile));
    presetBar.appendChild(chip);
  });
}

function connect() {
  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
  const url = `${proto}//${location.host}/ws`;
  setStatus('connecting', 'Conectando...');
  ws = new WebSocket(url);
  ws.binaryType = 'arraybuffer';
  ws.onopen = () => {
    reconnectAttempt = 0;
    setStatus('connected', 'Conectado');
    setDisconnected(false);
  };
  ws.onclose = () => {
    setStatus('disconnected', 'Desconectado');
    setDisconnected(true);
    scheduleReconnect();
  };
  ws.onerror = () => {
    if (ws.readyState !== WebSocket.OPEN) {
      setStatus('disconnected', 'Error de conexi\u00F3n');
      setDisconnected(true);
    }
  };
  ws.onmessage = (e) => {
    if (typeof e.data !== 'string') return;
    try {
      const msg = JSON.parse(e.data);
      if (msg.type === 'switch_profile' && autoSwitchEnabled) {
        if (profiles && profiles[msg.profile]) {
          switchProfile(msg.profile);
          if (navigator.vibrate) navigator.vibrate(30);
          showToast(msg.profile, msg.window || '');
        }
      }
    } catch(_) {}
  };
}

function showToast(profile, windowTitle) {
  const el = document.getElementById('toast');
  if (!el) return;
  el.className = '';
  el.innerHTML = '<span class="toast-profile">' + profile.charAt(0).toUpperCase() + profile.slice(1) + '</span><span class="toast-window">' + escapeHtml(windowTitle) + '</span>';
  clearTimeout(el._timer);
  el._timer = setTimeout(() => { el.className = 'toast-hidden'; }, 3000);
}

function escapeHtml(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

function setStatus(state, text) {
  dot.className = 'dot ' + state;
  statusText.textContent = text;
}

function setDisconnected(val) {
  const cls = val ? 'add' : 'remove';
  canvas.classList[cls]('disconnected');
  slidersCanvas.classList[cls]('disconnected');
}

function scheduleReconnect() {
  if (reconnectTimer) return;
  const delay = Math.min(1000 * Math.pow(2, reconnectAttempt), 30000);
  reconnectAttempt++;
  if (reconnectAttempt > 3 && !isAndroidApp) {
    showToast('Conexi\u00F3n perdida — Escanea el QR en tu PC', '');
  }
  reconnectTimer = setTimeout(() => {
    reconnectTimer = null;
    connect();
  }, delay);
}

async function requestWakeLock() {
  try {
    if ('wakeLock' in navigator) {
      wakeLock = await navigator.wakeLock.request('screen');
      wakeLock.addEventListener('release', () => {});
    }
  } catch (err) {}
}

document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') requestWakeLock();
});

function packKeyTap(keyCode, mods) {
  const bytes = [PROTO.MSG_KEY, PROTO.ACT_TAP, mods, keyCode];
  const cksum = bytes.reduce((a, b) => a ^ b, 0);
  return new Uint8Array([...bytes, cksum]);
}

function sendKeyTap(keyCode, mods) {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;
  ws.send(packKeyTap(keyCode, mods));
}

function packSlider(sliderId, value) {
  const bytes = [PROTO.MSG_SLIDER, sliderId, value, 0x00];
  const cksum = bytes.reduce((a, b) => a ^ b, 0);
  return new Uint8Array([...bytes, cksum]);
}

function sendSlider(sliderId, value) {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;
  ws.send(packSlider(sliderId, value));
}

function renderButtons() {
    canvas.innerHTML = '';
  if (!profiles || !profiles[currentProfile]) return;
  const profile = profiles[currentProfile];
  const cols = profile.cols || 4;
  const keys = profile.keys || [];
  const rows = Math.ceil(keys.length / cols);
  canvas.style.gridTemplateColumns = 'repeat(' + cols + ', 1fr)';
  canvas.style.gridTemplateRows = 'repeat(' + rows + ', 1fr)';
  keys.forEach((btn) => {
    const el = document.createElement('button');
    el.textContent = btn.label;
    if (btn.cls) el.className = btn.cls;
    el.addEventListener('pointerdown', (e) => {
      e.preventDefault();
      if (navigator.vibrate) navigator.vibrate(15);
      sendKeyTap(btn.key, btn.mods);
    });
    canvas.appendChild(el);
  });
}

const SCROLL_LIMIT = 40;

function setupScrollPad(padId, thumbId, sliderConst) {
  const pad = document.getElementById(padId);
  const thumb = document.getElementById(thumbId);
  let active = false;

  const onDown = (e) => {
    active = true;
    pad.setPointerCapture(e.pointerId);
    e.preventDefault();
  };

  const onMove = (e) => {
    if (!active) return;
    const rect = pad.getBoundingClientRect();
    const isV = sliderConst === PROTO.SLIDER_SCROLL_V;
    const center = (isV ? rect.height : rect.width) / 2;
    const offset = isV
      ? center - (e.clientY - rect.top)
      : e.clientX - rect.left - center;
    const clamped = Math.max(-SCROLL_LIMIT, Math.min(SCROLL_LIMIT, offset));
    const value = 128 + Math.round((clamped / SCROLL_LIMIT) * 127);
    if (isV) {
      thumb.style.transform = `translateY(${-clamped}px)`;
    } else {
      thumb.style.transform = `translateX(${clamped}px)`;
    }
    sendSlider(sliderConst, value);
  };

  const onUp = () => {
    if (!active) return;
    active = false;
    thumb.style.transform = 'translate(0,0)';
    sendSlider(sliderConst, 128);
  };

  pad.addEventListener('pointerdown', onDown);
  pad.addEventListener('pointermove', onMove);
  pad.addEventListener('pointerup', onUp);
  pad.addEventListener('pointercancel', onUp);
}

function setupRangeSlider(config) {
  const el = document.getElementById(config.el);
  const val = document.getElementById(config.val);
  let lastSent = 0;
  el.addEventListener('input', () => {
    const now = Date.now();
    if (now - lastSent < 40) return;
    lastSent = now;
    const v = parseInt(el.value);
    val.textContent = Math.round(v * config.factor) + config.units;
    sendSlider(config.id, v);
  });
  el.addEventListener('change', () => {
    const v = parseInt(el.value);
    val.textContent = Math.round(v * config.factor) + config.units;
    sendSlider(config.id, v);
  });
}

function switchMode(mode) {
  currentMode = mode;
  document.querySelectorAll('.mode-btn').forEach((b) => {
    b.classList.toggle('mode-active', b.dataset.mode === mode);
  });
  canvas.classList.toggle('hidden', mode !== 'grid');
  slidersCanvas.classList.toggle('hidden', mode !== 'sliders');
  profileBar.classList.toggle('profile-hidden', mode !== 'grid');
}

function switchProfile(name) {
  currentProfile = name;
  document.querySelectorAll('.profile-chip').forEach((c) => {
    c.classList.toggle('chip-active', c.dataset.profile === name);
  });
  localStorage.setItem('luna_profile', name);
  renderButtons();
}

document.querySelectorAll('.mode-btn').forEach((b) => {
  b.addEventListener('click', () => switchMode(b.dataset.mode));
});

document.getElementById('auto-btn').addEventListener('click', () => {
  autoSwitchEnabled = !autoSwitchEnabled;
  document.getElementById('auto-btn').classList.toggle('active', autoSwitchEnabled);
});

function applyButtonSize(val) {
  const gap = 1 + (val / 100) * 13;
  document.getElementById('canvas').style.setProperty('--gap', gap + 'px');
  localStorage.setItem('luna_btn_size', val);
}

const sizeSlider = document.getElementById('size-slider');
if (sizeSlider) {
  const savedSize = localStorage.getItem('luna_btn_size');
  if (savedSize !== null) {
    sizeSlider.value = savedSize;
    applyButtonSize(parseInt(savedSize));
  }
  sizeSlider.addEventListener('input', () => applyButtonSize(parseInt(sizeSlider.value)));
}

const uiToggle = document.getElementById('ui-toggle');
if (uiToggle) {
  const savedUI = localStorage.getItem('luna_ui_hidden');
  if (savedUI === '1') {
    document.getElementById('app').classList.add('ui-hidden');
    uiToggle.classList.add('active');
    uiToggle.textContent = '\u229E';
  }
  uiToggle.addEventListener('click', () => {
    const app = document.getElementById('app');
    app.classList.add('ui-hidden');
    uiToggle.classList.add('active');
    uiToggle.textContent = '\u229E';
    document.getElementById('show-ui-btn').classList.add('visible');
    localStorage.setItem('luna_ui_hidden', '1');
  });
}

const showUiBtn = document.getElementById('show-ui-btn');
if (showUiBtn) {
  let dragState = null;

  showUiBtn.addEventListener('pointerdown', (e) => {
    const r = showUiBtn.getBoundingClientRect();
    dragState = { ox: e.clientX - r.left, oy: e.clientY - r.top, moved: false };
    showUiBtn.setPointerCapture(e.pointerId);
    e.preventDefault();
  });

  showUiBtn.addEventListener('pointermove', (e) => {
    if (!dragState) return;
    const x = e.clientX - dragState.ox;
    const y = e.clientY - dragState.oy;
    showUiBtn.style.left = Math.max(0, x) + 'px';
    showUiBtn.style.top = Math.max(0, y) + 'px';
    showUiBtn.style.right = 'auto';
    if (Math.abs(e.movementX) > 2 || Math.abs(e.movementY) > 2) dragState.moved = true;
    e.preventDefault();
  });

  showUiBtn.addEventListener('pointerup', (e) => {
    if (!dragState) return;
    if (!dragState.moved) {
      document.getElementById('app').classList.remove('ui-hidden');
      uiToggle.classList.remove('active');
      uiToggle.textContent = '\u229F';
      showUiBtn.classList.remove('visible');
      localStorage.setItem('luna_ui_hidden', '0');
    } else {
      const r = showUiBtn.getBoundingClientRect();
      localStorage.setItem('luna_eye_pos', JSON.stringify({ left: r.left, top: r.top }));
    }
    dragState = null;
  });

  const savedUI = localStorage.getItem('luna_ui_hidden');
  if (savedUI === '1') {
    document.getElementById('app').classList.add('ui-hidden');
    if (uiToggle) { uiToggle.classList.add('active'); uiToggle.textContent = '\u229E'; }
    showUiBtn.classList.add('visible');
    const p = localStorage.getItem('luna_eye_pos');
    if (p) { try { const o = JSON.parse(p); showUiBtn.style.left = o.left + 'px'; showUiBtn.style.top = o.top + 'px'; showUiBtn.style.right = 'auto'; } catch(_) {} }
  }
}

// Landscape auto-mode (mobile only)
if (!document.documentElement.classList.contains('desktop')) {
  function applyOrientation() {
    const isLandscape = window.innerWidth > window.innerHeight;
    document.documentElement.classList.toggle('landscape', isLandscape);
    const app = document.getElementById('app');
    if (isLandscape) {
      app.classList.add('ui-hidden');
      if (uiToggle) { uiToggle.classList.add('active'); uiToggle.textContent = '\u229E'; }
      if (showUiBtn) showUiBtn.classList.add('visible');
    } else {
      const savedUI = localStorage.getItem('luna_ui_hidden');
      if (savedUI !== '1') {
        app.classList.remove('ui-hidden');
        if (uiToggle) { uiToggle.classList.remove('active'); uiToggle.textContent = '\u229F'; }
        if (showUiBtn) showUiBtn.classList.remove('visible');
      }
    }
  }
  applyOrientation();
  window.addEventListener('orientationchange', function() { setTimeout(applyOrientation, 250); });
  window.addEventListener('resize', function() {
    if (window.innerWidth > window.innerHeight !== document.documentElement.classList.contains('landscape')) {
      applyOrientation();
    }
  });
}

setupScrollPad('scroll-pad-v', 'scroll-thumb-v', PROTO.SLIDER_SCROLL_V);
setupScrollPad('scroll-pad-h', 'scroll-thumb-h', PROTO.SLIDER_SCROLL_H);
setupRangeSlider(SLIDER_CONFIG.volume);
setupRangeSlider(SLIDER_CONFIG.brightness);

const saved = localStorage.getItem('luna_profile');

// Connection info (desktop only — IP + QR)
const connInfo = document.getElementById('conn-info');
const connIp = document.getElementById('conn-ip');
const connQrBtn = document.getElementById('conn-qr-btn');
const qrModal = document.getElementById('qr-modal');
const qrImg = document.getElementById('qr-img');
const qrIpLabel = document.getElementById('qr-ip-label');
const qrCloseBtn = document.getElementById('qr-close-btn');

if (connInfo && document.documentElement.classList.contains('desktop')) {
  fetch('/api/ip').then(r => r.json()).then(data => {
    const ipText = data.ip + ':' + data.port;
    connIp.innerHTML = 'Conectado en: <strong>' + ipText + '</strong>  <span style="color:#555;font-size:10px">mDNS: luna.local</span>';
    qrImg.src = '/api/qr?' + Date.now();
    qrIpLabel.textContent = 'http://' + ipText;
  }).catch(() => {
    connIp.textContent = 'Sin conexi\u00F3n al servidor';
  });

  connQrBtn.addEventListener('click', () => {
    qrImg.src = '/api/qr?' + Date.now();
    qrModal.classList.remove('qr-modal-hidden');
  });

  qrCloseBtn.addEventListener('click', () => {
    qrModal.classList.add('qr-modal-hidden');
  });

  qrModal.addEventListener('click', (e) => {
    if (e.target === qrModal) qrModal.classList.add('qr-modal-hidden');
  });
}

// Android APK: mostrar boton Re-escanear QR + info de actualización
var isAndroidApp = navigator.userAgent.indexOf('LunaApp') >= 0;
var rescanBtn = document.getElementById('rescan-qr-btn');
if (isAndroidApp && rescanBtn) {
  rescanBtn.style.display = '';
  rescanBtn.addEventListener('click', function() {
    try {
      LunaBridge.scanQR();
    } catch(e) {
      console.warn('LunaBridge no disponible');
    }
  });
}

// Banner APK para móvil (no desktop, no APK)
(function() {
  var banner = document.getElementById('apk-banner');
  if (!banner) return;

  var isDesktop = document.documentElement.classList.contains('desktop');
  if (isDesktop || isAndroidApp) return;

  var closed = localStorage.getItem('luna_apk_banner_closed');
  if (closed) return;

  var body = banner.querySelector('.apk-banner-body');
  var tab = document.getElementById('apk-banner-tab');
  var closeBtn = document.getElementById('apk-banner-close');

  banner.classList.remove('apk-banner-hidden');

  var autoTimer = setTimeout(function() {
    banner.classList.add('apk-banner-collapsed');
  }, 5000);

  tab.addEventListener('click', function() {
    banner.classList.toggle('apk-banner-collapsed');
    clearTimeout(autoTimer);
  });

  closeBtn.addEventListener('click', function() {
    banner.classList.add('apk-banner-hidden');
    localStorage.setItem('luna_apk_banner_closed', '1');
    clearTimeout(autoTimer);
  });
})();

async function init() {
  await loadConfig();
  if (saved && profiles && profiles[saved]) switchProfile(saved);
  connect();
  requestWakeLock();
  setInterval(pollConfig, 5000);
}

init();
