const PROTO = {
  MSG_KEY: 0x01, MSG_SLIDER: 0x02,
  ACT_TAP: 0x03, ACT_PRESS: 0x01, ACT_RELEASE: 0x02,
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

var ICON_MAP = {
  '\u232B': 'backspace', '\u23CE': 'enter', '\u238B': 'escape',
  '\u21E7': 'shift', 'Tab': 'tap', '\u2423': 'space',
  '\u25C1': 'arrow-left', '\u25B2': 'arrow-up',
  '\u25BC': 'arrow-down', '\u25B7': 'arrow-right',
  'PTT': 'mic', 'MicSil': 'mic-off',
  'Vol+': 'vol-up', 'Vol-': 'vol-down',
  'Vol\u2191': 'vol-up', 'Vol\u2193': 'vol-down',
  'obs1': 'esc-1', 'obs2': 'esc-2', 'obs3': 'esc-3', 'obs4': 'esc-4',
  'Str On': 'stream-on', 'Str Off': 'stream-off',
  'Rec On': 'rec-on', 'Rec Off': 'rec-off',
  'Silen': 'silent', 'Mute': 'silent',
  'P/P': 'play-pause2', '\u23EF': 'play-pause2',
  'Next': 'skip-next', 'Prev': 'skip-prev',
  '\u23ED': 'skip-next', '\u23EE': 'skip-prev',
  '+Pest': 'tab-new', 'Cerrar': 'tap-close',
  'Sig': 'skip-next', 'Ant': 'skip-prev',
  'URL': 'url', 'Recarg': 'reload',
  'Atr\u00E1s': 'back', 'Adel': 'forward',
  'Reabrir': 'tab-reopen', 'Fav': 'fav',
  'Desc': 'downloads', 'Hist': 'history',
  'Buscar': 'search', 'Esc': 'escape',
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
    { label: 'Ctrl+Z', key: KC.Z, mods: PROTO.MOD_CTRL, cls: 'mod' },
    { label: 'Ctrl+X', key: KC.X, mods: PROTO.MOD_CTRL, cls: 'mod' },
    { label: 'Ctrl+C', key: KC.C, mods: PROTO.MOD_CTRL, cls: 'mod' },
    { label: 'Ctrl+V', key: KC.V, mods: PROTO.MOD_CTRL, cls: 'mod' },
    { label: 'Ctrl+S', key: KC.S, mods: PROTO.MOD_CTRL, cls: 'mod' },
    { label: 'Ctrl+A', key: KC.A, mods: PROTO.MOD_CTRL, cls: 'mod' },
    { label: 'Ctrl+F', key: KC.F, mods: PROTO.MOD_CTRL, cls: 'mod' },
    { label: 'Ctrl+D', key: KC.D, mods: PROTO.MOD_CTRL, cls: 'mod' },
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
    { label: 'obs1', key: 126, mods: 0, cls: '' },
    { label: 'obs2', key: 127, mods: 0, cls: '' },
    { label: 'obs3', key: 128, mods: 0, cls: '' },
    { label: 'obs4', key: 129, mods: 0, cls: '' },
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

const profileBar = document.getElementById('profile-bar');
const presetBar = document.getElementById('preset-bar');

let ws = null;
let reconnectTimer = null;
let reconnectAttempt = 0;
let wakeLock = null;
let currentProfile = 'default';
let currentMode = 'grid';
var activePointers = {};
let isPro = false;

const SLIDER_CONFIG = {
  volume: { el: 'slider-volume', val: 'volume-value', id: PROTO.SLIDER_VOLUME, units: '%', factor: 100/255 },
  brightness: { el: 'slider-brightness', val: 'brightness-value', id: PROTO.SLIDER_BRIGHTNESS, units: '%', factor: 100/255   },
};

function convertKey(k) {
  let cls = '';
  if (k.mods & 1) cls = 'mod';
  else if ([8, 9, 13, 16, 27, 32].includes(k.keyCode)) cls = 'special';
  else if (k.keyCode >= 37 && k.keyCode <= 40) cls = 'arrow';
  return { label: k.label, key: k.keyCode, mods: k.mods, cls, icon: k.icon, sound: k.sound };
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
    isPro = data.pro_license === true;
  } catch(e) {
    profiles = HARDCODED_PROFILES;
  }
  loadTheme();
  buildProfileChips();
  buildPresetChips();
  renderButtons();
}

function loadTheme() {
  fetch('/api/themes').then(function(r){return r.json();}).then(function(td) {
    if (td && td.pc) applyCustomPCTheme(td.pc);
  }).catch(function() {});
}

function applyCustomPCTheme(pc) {
  var s = document.getElementById('luna-custom-theme');
  if (!s) {
    s = document.createElement('style');
    s.id = 'luna-custom-theme';
    document.head.appendChild(s);
  }
  s.textContent = ':root{' +
    Object.entries(pc).filter(function(kv){return typeof kv[1]==='string';}).map(function(kv) {
      return '--' + kv[0].replace(/_/g, '-') + ':' + kv[1] + ';';
    }).join('') +
  '}';
}

var _rgbStops = {
  rainbow: [0,51,102,153,204,255,306,360],
  respiro: [190,220,250,220,190],
  wave: [0,120,240,360],
  neon: [0,72,144,216,288,360],
  flash: [0,60,120,180,240,300],
  drift: [0,360],
  aurora: [140,180,230,280,140],
  meteor: [30,90,150,210,270,330],
  static: [0],
  party: [0,60,120,180,240,300]
};

function _genKF(id, stops) {
  var pct = 100 / (stops.length - 1);
  var g = '@keyframes lg-' + id + '{', a = '@keyframes la-' + id + '{', t = '@keyframes lt-' + id + '{';
  stops.forEach(function(h, i) {
    var k = i === stops.length - 1 ? '100%' : Math.round(i * pct) + '%';
    var c1 = 'hsl(' + h + ',65%,55%)', c2 = 'hsl(' + h + ',65%,35%)';
    g += k + '{box-shadow:0 0 10px ' + c1 + ',0 0 22px ' + c2 + '}';
    a += k + '{box-shadow:inset 0 0 10px ' + c1 + '}';
    t += k + '{box-shadow:inset 0 -2px 0 ' + c1 + '}';
  });
  return g + '}' + a + '}' + t + '}';
}

function applyRGB(rgb) {
  var oldStyle = document.getElementById('luna-rgb-css');
  if (oldStyle) oldStyle.remove();
  stopRGBParty();

  var html = document.documentElement;
  Object.keys(_rgbStops).forEach(function(m){html.classList.remove('luna-rgb-'+m);});
  html.classList.remove('luna-rgb-on', 'luna-rgb-accent-only');

  if (!rgb || !rgb.enabled) return;

  var speed = (rgb.speed || 1.0).toFixed(1) + 's';
  var mode = rgb.mode || 'rainbow';
  var s = document.createElement('style');
  s.id = 'luna-rgb-css';

  if (mode === 'party') {
    document.head.appendChild(s);
    startRGBParty(rgb);
    html.classList.add('luna-rgb-party', 'luna-rgb-on');
    if (rgb.accent_only) html.classList.add('luna-rgb-accent-only');
    html.style.setProperty('--rgb-speed', speed);
    return;
  }

  if (mode === 'static') {
    var sc = rgb.static_color || '#FF0000';
    s.textContent =
      '.luna-rgb-on.luna-rgb-static #canvas{box-shadow:0 0 10px ' + sc + ',0 0 22px ' + sc + '}' +
      '.luna-rgb-on.luna-rgb-static button:active{box-shadow:inset 0 0 10px ' + sc + '}' +
      '.luna-rgb-on.luna-rgb-static .profile-chip.chip-active{box-shadow:inset 0 -2px 0 ' + sc + '}';
    document.head.appendChild(s);
    html.classList.add('luna-rgb-static', 'luna-rgb-on');
    if (rgb.accent_only) html.classList.add('luna-rgb-accent-only');
    html.style.setProperty('--rgb-speed', speed);
    return;
  }

  var stops = _rgbStops[mode];
  s.textContent = _genKF(mode, stops) +
    '.luna-rgb-on.luna-rgb-' + mode + ' #canvas{animation:lg-' + mode + ' var(--rgb-speed,' + speed + ') linear infinite}' +
    '.luna-rgb-on.luna-rgb-' + mode + ' button:active{animation:la-' + mode + ' var(--rgb-speed,2s) linear infinite}' +
    '.luna-rgb-on.luna-rgb-' + mode + ' .profile-chip.chip-active{animation:lt-' + mode + ' var(--rgb-speed,3s) linear infinite}';
  document.head.appendChild(s);
  html.classList.add('luna-rgb-' + mode, 'luna-rgb-on');
  if (rgb.accent_only) html.classList.add('luna-rgb-accent-only');
  html.style.setProperty('--rgb-speed', speed);
}

function startRGBParty(rgb) {
  stopRGBParty();
  var s = document.createElement('style');
  s.id = 'luna-rgb-css';
  document.head.appendChild(s);
  var colors = ['#FF0000','#FF8800','#FFFF00','#00FF00','#0088FF','#8800FF','#FF00FF'];
  if (window._rgbPartyInterval) clearInterval(window._rgbPartyInterval);
  window._rgbPartyInterval = setInterval(function() {
    var c = colors[Math.floor(Math.random() * colors.length)];
    s.textContent =
      '.luna-rgb-on.luna-rgb-party #canvas{box-shadow:0 0 10px ' + c + ',0 0 22px ' + c + '}' +
      '.luna-rgb-on.luna-rgb-party button:active{box-shadow:inset 0 0 10px ' + c + '}' +
      '.luna-rgb-on.luna-rgb-party .profile-chip.chip-active{box-shadow:inset 0 -2px 0 ' + c + '}';
  }, 200);
  document.documentElement.classList.add('luna-rgb-party');
}

function stopRGBParty() {
  if (window._rgbPartyInterval) {
    clearInterval(window._rgbPartyInterval);
    window._rgbPartyInterval = null;
  }
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
  const names = Object.keys(profiles);
  const limit = isPro ? names.length : Math.min(names.length, 3);
  for (var i = 0; i < limit; i++) {
    const name = names[i];
    const chip = document.createElement('button');
    chip.className = 'profile-chip' + (name === currentProfile ? ' chip-active' : '');
    chip.dataset.profile = name;
    chip.textContent = name.charAt(0).toUpperCase() + name.slice(1);
    chip.addEventListener('click', () => switchProfile(name));
    profileBar.appendChild(chip);
  }
  if (!isPro && names.length > 3) {
    const chip = document.createElement('button');
    chip.className = 'profile-chip chip-locked';
    chip.textContent = '\u{1F512} +' + (names.length - 3);
    chip.title = 'Actualiza a Pro para ver m\u00E1s perfiles';
    profileBar.appendChild(chip);
  }
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
  setStatus('connecting');
  ws = new WebSocket(url);
  ws.binaryType = 'arraybuffer';
  ws.onopen = () => {
    reconnectAttempt = 0;
    setStatus('connected');
    setDisconnected(false);
    hideServerError();

  };
  ws.onclose = () => {
    setStatus('disconnected');
    setDisconnected(true);
    if (reconnectAttempt > 3) {
      showServerError();
    }
    scheduleReconnect();
  };
  ws.onerror = () => {
    if (ws.readyState !== WebSocket.OPEN) {
      setStatus('disconnected');
      setDisconnected(true);
    }
  };
  ws.onmessage = (e) => {
    if (typeof e.data !== 'string') return;
    try {
      const msg = JSON.parse(e.data);
      if (msg.type === 'switch_profile') {
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

function setStatus(state) {
  dot.className = 'dot ' + state;
}

function showServerError(msg) {
  var banner = document.getElementById('server-error-banner');
  if (banner) banner.style.display = 'flex';
  var txt = document.getElementById('server-error-text');
  if (txt && msg) txt.textContent = msg;
}

function hideServerError() {
  var banner = document.getElementById('server-error-banner');
  if (banner) banner.style.display = 'none';
}

function retryServer() {
  var btn = document.getElementById('server-retry-btn');
  if (btn) { btn.disabled = true; btn.textContent = __('server.retrying') || 'Retrying...'; }
  if (typeof pywebview !== 'undefined' && pywebview.api && pywebview.api.retry_server) {
    pywebview.api.retry_server();
  } else {
    location.reload();
  }
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
    showToast(__('toast.reconnect'), '');
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

function packKeyPress(keyCode, mods) {
  const bytes = [PROTO.MSG_KEY, PROTO.ACT_PRESS, mods, keyCode];
  const cksum = bytes.reduce((a, b) => a ^ b, 0);
  return new Uint8Array([...bytes, cksum]);
}

function packKeyRelease(keyCode, mods) {
  const bytes = [PROTO.MSG_KEY, PROTO.ACT_RELEASE, mods, keyCode];
  const cksum = bytes.reduce((a, b) => a ^ b, 0);
  return new Uint8Array([...bytes, cksum]);
}

function sendKeyTap(keyCode, mods) {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;
  ws.send(packKeyTap(keyCode, mods));
}

function sendKeyPress(keyCode, mods, pid) {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;
  ws.send(packKeyPress(keyCode, mods));
  activePointers[pid] = { key: keyCode, mods: mods };
}

function sendKeyRelease(keyCode, mods, pid) {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;
  if (activePointers[pid]) {
    ws.send(packKeyRelease(keyCode, mods));
    delete activePointers[pid];
  }
}

function releaseAllPointers() {
  for (var pid in activePointers) {
    if (activePointers.hasOwnProperty(pid)) {
      var p = activePointers[pid];
      if (!ws || ws.readyState !== WebSocket.OPEN) break;
      ws.send(packKeyRelease(p.key, p.mods));
    }
  }
  activePointers = {};
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

function getDisplayDims(cols) {
  if (cols === 5) return { cols: 7, rows: 3, total: 21 };
  if (cols === 6) return { cols: 6, rows: 4, total: 24 };
  return { cols: 4, rows: 4, total: 16 };
}

function renderButtons() {
    canvas.innerHTML = '';
  if (!profiles || !profiles[currentProfile]) return;
  const profile = profiles[currentProfile];
  const cols = profile.cols || 4;
  const keys = profile.keys || [];
  const dims = getDisplayDims(cols);
  canvas.style.gridTemplateColumns = 'repeat(' + dims.cols + ', 1fr)';
  canvas.style.gridTemplateRows = 'repeat(' + dims.rows + ', 1fr)';
  canvas.style.setProperty('--cols', dims.cols);
  for (var i = 0; i < dims.total; i++) {
    if (i < keys.length) {
      const btn = keys[i];
      const el = document.createElement('button');
      var iconUrl = null;
      if (btn.icon && btn.icon.startsWith('custom/')) {
        iconUrl = '/custom-icons/' + btn.icon.replace('custom/', '');
      } else if (btn.icon) {
        iconUrl = '/icons/' + btn.icon + '.png';
      } else if (ICON_MAP[btn.label]) {
        iconUrl = '/icons/' + ICON_MAP[btn.label] + '.png';
      }
      if (iconUrl) {
        var img = document.createElement('img');
        img.src = iconUrl;
        img.className = 'btn-icon';
        img.alt = btn.label;
        img.draggable = false;
        el.appendChild(img);
      } else {
        el.textContent = btn.label;
      }
      if (btn.cls) el.className = btn.cls;
      el.style.setProperty('--i', i);
      if (btn.mods) {
        el.addEventListener('pointerdown', (function(b) {
          return function(e) {
            e.preventDefault();
            if (navigator.vibrate) navigator.vibrate(8);
            sendKeyTap(b.key, b.mods);
          };
        })(btn));
      } else {
        el.addEventListener('pointerdown', (function(b) {
          return function(e) {
            e.preventDefault();
            e.target.setPointerCapture(e.pointerId);
            if (navigator.vibrate) navigator.vibrate(8);
            sendKeyPress(b.key, b.mods, e.pointerId);
          };
        })(btn));
        el.addEventListener('pointerup', (function(b) {
          return function(e) {
            sendKeyRelease(b.key, b.mods, e.pointerId);
          };
        })(btn));
        el.addEventListener('pointercancel', (function(b) {
          return function(e) {
            sendKeyRelease(b.key, b.mods, e.pointerId);
          };
        })(btn));
      }
      canvas.appendChild(el);
    } else {
      const el = document.createElement('button');
      el.className = 'empty';
      canvas.appendChild(el);
    }
  }
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
  document.querySelectorAll('.mode-icon').forEach((b) => {
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

document.querySelectorAll('.mode-icon').forEach((b) => {
  b.addEventListener('click', () => switchMode(b.dataset.mode));
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
const connAdb = document.getElementById('conn-adb');
const connQrBtn = document.getElementById('conn-qr-btn');
const qrModal = document.getElementById('qr-modal');
const qrImg = document.getElementById('qr-img');
const qrIpLabel = document.getElementById('qr-ip-label');
const qrApkLabel = document.getElementById('qr-apk-label');
const qrCloseBtn = document.getElementById('qr-close-btn');

if (connInfo && document.documentElement.classList.contains('desktop')) {
  fetch('/api/ip').then(r => r.json()).then(data => {
    var ipText = '';
    if (data.ips && data.ips.length > 0) {
      ipText = data.ips[0] + ':' + data.port;
    } else {
      ipText = data.ip + ':' + data.port;
    }
    connIp.innerHTML = __('status.ip_info').replace('{0}', '<strong>' + ipText + '</strong>');
    if (connAdb) {
      fetch('/api/adb-status').then(function(r) { return r.json(); }).then(function(d) {
        if (d.status === 'ok') { connAdb.style.display = 'inline'; }
        else if (d.status === 'no_adb') { connAdb.style.display = 'inline'; connAdb.style.background = 'rgba(255,152,0,0.15)'; connAdb.style.color = '#FF9800'; connAdb.textContent = 'ADB?'; }
      }).catch(function() {});
    }
    qrImg.src = '/api/qr?' + Date.now();
    qrIpLabel.textContent = 'http://' + ipText;
  }).catch(() => {
    connIp.textContent = __('status.no_server');
  });

  function switchQrTab(tab) {
    document.querySelectorAll('.qr-tab').forEach(function(t) { t.classList.remove('qr-tab-active'); });
    tab.classList.add('qr-tab-active');
    if (tab.getAttribute('data-qr') === 'apk') {
      qrImg.src = '/api/qr-apk?' + Date.now();
      qrIpLabel.style.display = 'none';
      qrApkLabel.style.display = '';
    } else {
      qrImg.src = '/api/qr?' + Date.now();
      qrIpLabel.style.display = '';
      qrApkLabel.style.display = 'none';
    }
  }

  connQrBtn.addEventListener('click', () => {
    var firstTab = document.querySelector('.qr-tab[data-qr="connect"]');
    if (firstTab) switchQrTab(firstTab);
    qrImg.src = '/api/qr?' + Date.now();
    qrModal.classList.remove('qr-modal-hidden');
  });

  document.querySelectorAll('.qr-tab').forEach(function(tab) {
    tab.addEventListener('click', function() { switchQrTab(this); });
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
      LunaBridge.scanQR('rescan');
    } catch(e) {
      console.warn('LunaBridge no disponible');
    }
  });
}

// Callback desde escáner nativo (CameraX inline)
window.onQRResult = function(callbackId, result) {
  if (callbackId === 'rescan') {
    if (!/^\d+\.\d+\.\d+\.\d+$/.test(result)) return;
    window.location.href = 'http://' + result + '/';
  }
};

// Banner APK para móvil (no desktop, no APK)
(function() {
  var banner = document.getElementById('apk-banner');
  if (!banner) return;

  var isDesktop = document.documentElement.classList.contains('desktop');
  if (isDesktop || isAndroidApp) return;

  var closed = localStorage.getItem('luna_apk_banner_closed');
  if (closed) return;

  var tab = document.getElementById('apk-banner-tab');

  banner.classList.remove('apk-banner-hidden');

  var appEl = document.getElementById('app');
  function updateBannerPadding() {
    appEl.style.paddingTop = banner.classList.contains('apk-banner-collapsed') ? '30px' : '80px';
  }
  updateBannerPadding();

  tab.addEventListener('click', function() {
    banner.classList.toggle('apk-banner-collapsed');
    updateBannerPadding();
  });
})();

// Limpieza de teclas presionadas al perder foco o cambiar pestaña
window.addEventListener('pagehide', function() {
  releaseAllPointers();
});
window.addEventListener('blur', function() {
  releaseAllPointers();
});





// ── Tooltips ──
(function() {
  var el, timer, shown = {};
  document.addEventListener('mouseover', function(e) {
    var t = e.target.closest('[data-tooltip]');
    if (!t) { if (el) { el.remove(); el = null; } return; }
    var key = t.getAttribute('data-i18n-tooltip') || t.getAttribute('data-tooltip');
    if (shown[key]) return;
    clearTimeout(timer);
    timer = setTimeout(function() {
      if (el) el.remove();
      el = document.createElement('div');
      el.className = 'tooltip';
      el.textContent = t.getAttribute('data-tooltip');
      document.body.appendChild(el);
      var tr = t.getBoundingClientRect();
      var vr = el.getBoundingClientRect();
      var top = tr.top - vr.height - 8;
      if (top < 4) top = tr.bottom + 8;
      var left = Math.max(4, Math.min(tr.left + (tr.width - vr.width) / 2, window.innerWidth - vr.width - 4));
      el.style.left = left + 'px'; el.style.top = top + 'px';
      requestAnimationFrame(function() { el.classList.add('visible'); });
      shown[key] = true;
      setTimeout(function() { if (el) { el.remove(); el = null; } }, 30000);
    }, document.body.classList.contains('tooltip-review') ? 0 : 250);
  });
  document.addEventListener('mouseout', function(e) {
    if (!e.target.closest('[data-tooltip]')) return;
    clearTimeout(timer);
    if (el) { el.remove(); el = null; }
  });
})();

// ── Diálogo de cierre (solo escritorio, polling vía pywebview) ──
function muestrarDialogoCierre() {
  var el = document.getElementById('luna-close-overlay');
  if (el) el.classList.add('visible');
}
function cerrarCompletamente() {
  document.getElementById('luna-close-overlay').classList.remove('visible');
  if (typeof pywebview !== 'undefined' && pywebview.api && pywebview.api.close_completly) {
    pywebview.api.close_completly();
  }
}
function cerrarSegundoPlano() {
  document.getElementById('luna-close-overlay').classList.remove('visible');
  if (typeof pywebview !== 'undefined' && pywebview.api && pywebview.api.hide_to_tray) {
    pywebview.api.hide_to_tray();
  }
}
function cancelarCierre() {
  document.getElementById('luna-close-overlay').classList.remove('visible');
  if (typeof pywebview !== 'undefined' && pywebview.api && pywebview.api.cancel_close) {
    pywebview.api.cancel_close();
  }
}
(function(){
  setInterval(function() {
    if (typeof pywebview !== 'undefined' && pywebview.api && pywebview.api.is_close_pending) {
      pywebview.api.is_close_pending().then(function(pending) {
        if (pending) muestrarDialogoCierre();
      }).catch(function() {});
    }
  }, 300);
})();



// ── Pro Purchase (Modal) ──
(function(){
  var btn = document.getElementById('pro-purchase-btn');
  var banner = document.getElementById('ad-banner');
  var connInfo = document.getElementById('conn-info');
  var modal = document.getElementById('pro-modal');
  var closeBtn = document.getElementById('pro-modal-close');
  var buyBtn = document.getElementById('pro-buy-btn');
  if (!btn || !banner || !connInfo || !modal || !closeBtn || !buyBtn) return;

  function hideProModal() {
    modal.classList.add('pro-modal-hidden');
  }

  function showProModal() {
    modal.classList.remove('pro-modal-hidden');
  }

  function setProState(data) {
    if (data.pro) {
      banner.classList.add('ad-banner-hidden');
      document.body.style.paddingBottom = '0';
      btn.textContent = '\u2705 Pro';
      btn.className = 'conn-qr-btn pro-active';
      buyBtn.textContent = '\u2705 Pro activado';
      buyBtn.className = 'pro-buy-btn pro-active-btn';
      buyBtn.disabled = true;
    } else {
      btn.textContent = '\uD83D\uDC51 Pro';
      btn.className = 'conn-qr-btn';
      banner.classList.remove('ad-banner-hidden');
      document.body.style.paddingBottom = '60px';
      buyBtn.textContent = '\uD83D\uDCB3 Comprar Pro';
      buyBtn.className = 'pro-buy-btn';
      buyBtn.disabled = false;
    }
  }

  fetch('/api/pro-status')
    .then(function(r) { return r.json(); })
    .then(setProState)
    .catch(function() {});

  btn.addEventListener('click', function() {
    showProModal();
  });

  closeBtn.addEventListener('click', function() {
    hideProModal();
  });

  modal.addEventListener('click', function(e) {
    if (e.target === modal) hideProModal();
  });

  buyBtn.addEventListener('click', function() {
    if (buyBtn.disabled) return;
    buyBtn.textContent = '...';
    buyBtn.disabled = true;
    fetch('/api/pro-purchase', { method: 'POST' })
      .then(function(r) { return r.json(); })
      .then(function(data) {
        if (data.redirect_url) {
          var storeLink = document.getElementById('pro-store-link');
          var storeWrap = document.getElementById('pro-store-link-wrap');
          if (storeLink) storeLink.href = data.redirect_url;
          var fallbackShown = false;
          var showFallback = function() {
            if (fallbackShown) return;
            fallbackShown = true;
            if (storeWrap) storeWrap.classList.remove('pro-store-link-hidden');
            buyBtn.textContent = '\uD83D\uDCB3 Comprar Pro';
            buyBtn.disabled = false;
          };
          alert('Se abrir\u00e1 la Microsoft Store para comprar Pro. Despu\u00e9s de comprar, reinicia Luna para activarlo.');
          fetch('/api/open-url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: data.redirect_url })
          })
            .then(function(r) { return r.json(); })
            .then(function(res) {
              if (!res.ok) showFallback();
            })
            .catch(function() { showFallback(); });
          return;
        }
        setProState(data);
        hideProModal();
      })
      .catch(function() {
        buyBtn.textContent = '\uD83D\uDCB3 Comprar Pro';
        buyBtn.disabled = false;
      });
  });


})();

async function init() {
  await loadConfig();
  if (saved && profiles && profiles[saved]) switchProfile(saved);
  connect();
  requestWakeLock();
  setInterval(function() { if (ws && ws.readyState === WebSocket.OPEN) pollConfig(); }, 5000);
}

init();
