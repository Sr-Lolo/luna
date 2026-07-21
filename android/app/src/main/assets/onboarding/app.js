(function() {
  var lang;
  var isError;

  function getLang() {
    var m = location.search.match(/[?&]lang=(\w+)/);
    var l = m ? m[1] : ((navigator.language || '').split('-')[0] || 'en');
    if (l !== 'en' && l !== 'es' && l !== 'pt') l = 'en';
    return l;
  }

  var _dict;
  function ensureDict() {
    if (_dict) return;
    _dict = {
      en: {
        'title-main':'CONNECT YOUR PHONE TO THE PC!!','subtitle':'Choose how to connect your device',
        'card-wifi-title':'Wi-Fi','card-wifi-desc':'Wireless connection, same network',
        'card-usb-title':'USB','card-usb-desc':'Cable connection (USB Tethering)',
        'back':'Back','back-2':'Back',
        'wifi-title':'Wi-Fi Connection','wifi-sub':'Follow these steps to link your phone via Wi-Fi:',
        'wifi-step1':'Make sure the PC and phone are on the <strong>same Wi-Fi network</strong>',
        'wifi-step2':'Open <strong>LunaDeck</strong> on your PC (server must be running)',
        'wifi-step3':'On the PC dashboard find the <strong>6-digit pairing code</strong>',
        'wifi-step4':'Press <strong>"Search Wi-Fi"</strong> and select your PC from the list',
        'wifi-step5':'Enter the <strong>6-digit code</strong> when prompted',
        'wifi-btn':'Search Wi-Fi',
        'usb-title':'USB Tethering','usb-sub':'Follow these steps to link your phone via USB:',
        'usb-step1':'Connect the phone to the PC <strong>with a USB cable</strong>',
        'usb-step2':'Go to <strong>Settings &gt; Networks &gt; Hotspot/Tethering &gt; USB tethering</strong>',
        'usb-step3':'Enable <strong>"USB Tethering"</strong>',
        'usb-step4':'Press <strong>"Search PC via USB"</strong> to find your PC','usb-btn':'Search PC via USB',
        'panic-title':'Troubleshooting','panic-ok':'Got it',
        'panic':'\u2757 Not working?','panic-2':'\u2757 Not working?',
        'panic-wifi-1':'Windows Firewall is blocking the connection. Run LunaDeck as Administrator.',
        'panic-wifi-2':'Both devices are not on the same Wi-Fi network.',
        'panic-wifi-3':'Port 9120 is blocked. Check your firewall settings.',
        'panic-wifi-4':'LunaDeck server is not running on the PC.',
        'panic-wifi-5':'The Wi-Fi network blocks device-to-device communication (public network/hotel).',
        'panic-wifi-6':'Windows network profile is set to "Public". It must be "Private" for connections.',
        'panic-wifi-7':'Your router may be blocking UDP broadcast (port 53210) between devices.',
        'panic-wifi-8':'The pairing code entered is incorrect. Check the 6-digit code on the PC dashboard.',
        'panic-usb-1':'"USB Tethering" is not enabled. Go to Settings &gt; Networks &gt; Hotspot/Tethering.',
        'panic-usb-2':'The USB cable does not support data transfer (charging only). Try a different cable.',
        'panic-usb-3':'Windows Firewall is blocking the connection. Run LunaDeck as Administrator.',
        'panic-usb-4':'Try a different USB cable or port.',
        'panic-usb-5':'Disconnect USB, enable USB Tethering again, and retry.',
        'panic-usb-6':'Make sure the LunaDeck server is running on the PC.',
        'panic-usb-7':'Restart both the phone and PC, then retry the connection.',
        'panic-usb-8':'If the issue persists, try connecting via Wi-Fi or QR code instead.',
        'scan':'Scan QR','manual':'Manual IP','exit':'Exit','retry':'Retry connection',
        'error':'Could not connect. Make sure LunaDeck is running on your PC and try running it as Administrator.'
      },
      es: {
        'title-main':'VINCULA TU M\u00d3VIL A LA PC!!','subtitle':'Elige c\u00f3mo conectar tu dispositivo',
        'card-wifi-title':'Wi-Fi','card-wifi-desc':'Conexi\u00f3n inal\u00e1mbrica, misma red',
        'card-usb-title':'USB','card-usb-desc':'Conexi\u00f3n por cable (USB Tethering)',
        'back':'Volver','back-2':'Volver',
        'wifi-title':'Conexi\u00f3n Wi-Fi','wifi-sub':'Sigue estos pasos para vincular tu m\u00f3vil por Wi-Fi:',
        'wifi-step1':'Aseg\u00farate de que el PC y el m\u00f3vil est\u00e9n en la <strong>misma red Wi-Fi</strong>',
        'wifi-step2':'Abre <strong>LunaDeck</strong> en tu PC (el servidor debe estar ejecut\u00e1ndose)',
        'wifi-step3':'En el panel del PC busca el <strong>c\u00f3digo de emparejamiento</strong> de 6 d\u00edgitos',
        'wifi-step4':'Pulsa <strong>"Buscar Wi-Fi"</strong> y selecciona tu PC de la lista',
        'wifi-step5':'Introduce el <strong>c\u00f3digo de 6 d\u00edgitos</strong> cuando se te solicite',
        'wifi-btn':'Buscar Wi-Fi',
        'usb-title':'USB Tethering','usb-sub':'Sigue estos pasos para vincular tu m\u00f3vil por USB:',
        'usb-step1':'Conecta el m\u00f3vil al PC <strong>mediante un cable USB</strong>',
        'usb-step2':'Ve a <strong>Ajustes &gt; Redes &gt; Zona WiFi/Anclaje &gt; Anclaje USB</strong>',
        'usb-step3':'Activa <strong>"Anclaje USB"</strong> (USB Tethering)',
        'usb-step4':'Pulsa <strong>"Buscar PC por USB"</strong> para encontrar tu PC','usb-btn':'Buscar PC por USB',
        'panic-title':'Soluci\u00f3n de problemas','panic-ok':'Entendido',
        'panic':'\u2757 \u00bfNo funciona?','panic-2':'\u2757 \u00bfNo funciona?',
        'panic-wifi-1':'El Firewall de Windows bloquea la conexi\u00f3n. Ejecuta LunaDeck como Administrador.',
        'panic-wifi-2':'Ambos dispositivos no est\u00e1n en la misma red Wi-Fi.',
        'panic-wifi-3':'El puerto 9120 est\u00e1 bloqueado. Revisa el firewall.',
        'panic-wifi-4':'El servidor de LunaDeck no est\u00e1 ejecut\u00e1ndose en el PC.',
        'panic-wifi-5':'La red Wi-Fi bloquea la comunicaci\u00f3n entre dispositivos (red p\u00fablica/hotel).',
        'panic-wifi-6':'El perfil de red en Windows es "P\u00fablica". Debe ser "Privada" para permitir conexiones.',
        'panic-wifi-7':'Tu router puede estar bloqueando broadcast UDP (puerto 53210) entre dispositivos.',
        'panic-wifi-8':'El c\u00f3digo de emparejamiento es incorrecto. Revisa el c\u00f3digo de 6 d\u00edgitos en el panel del PC.',
        'panic-usb-1':'El "Anclaje USB" no est\u00e1 activado. Ve a Ajustes &gt; Redes &gt; Zona WiFi/Anclaje.',
        'panic-usb-2':'El cable USB no soporta transferencia de datos (solo carga). Prueba otro cable.',
        'panic-usb-3':'El Firewall de Windows bloquea la conexi\u00f3n. Ejecuta LunaDeck como Administrador.',
        'panic-usb-4':'Prueba con otro cable USB o puerto.',
        'panic-usb-5':'Desconecta el USB, activa el Anclaje USB de nuevo y reintenta.',
        'panic-usb-6':'Aseg\u00farate de que el servidor de LunaDeck est\u00e9 ejecut\u00e1ndose en el PC.',
        'panic-usb-7':'Reinicia el m\u00f3vil y el PC, luego vuelve a intentarlo.',
        'panic-usb-8':'Si el problema persiste, prueba con Wi-Fi o c\u00f3digo QR.',
        'scan':'Escanear QR','manual':'IP Manual','exit':'Salir','retry':'Reintentar conexi\u00f3n',
        'error':'No se pudo conectar. Aseg\u00farate de que LunaDeck est\u00e9 abierto en tu PC y prueba ejecutarlo como Administrador.'
      },
      pt: {
        'title-main':'CONECTE SEU CELULAR AO PC!!','subtitle':'Escolha como conectar seu dispositivo',
        'card-wifi-title':'Wi-Fi','card-wifi-desc':'Conex\u00e3o sem fio, mesma rede',
        'card-usb-title':'USB','card-usb-desc':'Conex\u00e3o por cabo (USB Tethering)',
        'back':'Voltar','back-2':'Voltar',
        'wifi-title':'Conex\u00e3o Wi-Fi','wifi-sub':'Siga estes passos para vincular seu celular via Wi-Fi:',
        'wifi-step1':'Certifique-se de que o PC e o celular estejam na <strong>mesma rede Wi-Fi</strong>',
        'wifi-step2':'Abra o <strong>LunaDeck</strong> no seu PC (o servidor deve estar em execu\u00e7\u00e3o)',
        'wifi-step3':'No painel do PC, encontre o <strong>c\u00f3digo de emparelhamento</strong> de 6 d\u00edgitos',
        'wifi-step4':'Pressione <strong>"Buscar Wi-Fi"</strong> e selecione seu PC na lista',
        'wifi-step5':'Digite o <strong>c\u00f3digo de 6 d\u00edgitos</strong> quando solicitado',
        'wifi-btn':'Buscar Wi-Fi',
        'usb-title':'USB Tethering','usb-sub':'Siga estes passos para vincular seu celular via USB:',
        'usb-step1':'Conecte o celular ao PC <strong>com um cabo USB</strong>',
        'usb-step2':'V\u00e1 para <strong>Configura\u00e7\u00f5es &gt; Redes &gt; Roteador Wi-Fi/Ancoragem &gt; Ancoragem USB</strong>',
        'usb-step3':'Ative <strong>"Ancoragem USB"</strong> (USB Tethering)',
        'usb-step4':'Pressione <strong>"Buscar PC via USB"</strong> para encontrar seu PC','usb-btn':'Buscar PC via USB',
        'panic-title':'Solu\u00e7\u00e3o de problemas','panic-ok':'Entendi',
        'panic':'\u2757 N\u00e3o funciona?','panic-2':'\u2757 N\u00e3o funciona?',
        'panic-wifi-1':'O Firewall do Windows est\u00e1 bloqueando a conex\u00e3o. Execute o LunaDeck como Administrador.',
        'panic-wifi-2':'Ambos os dispositivos n\u00e3o est\u00e3o na mesma rede Wi-Fi.',
        'panic-wifi-3':'A porta 9120 est\u00e1 bloqueada. Verifique as configura\u00e7\u00f5es do firewall.',
        'panic-wifi-4':'O servidor LunaDeck n\u00e3o est\u00e1 em execu\u00e7\u00e3o no PC.',
        'panic-wifi-5':'A rede Wi-Fi bloqueia a comunica\u00e7\u00e3o entre dispositivos (rede p\u00fablica/hotel).',
        'panic-wifi-6':'O perfil de rede no Windows est\u00e1 como "P\u00fablico". Deve ser "Privado" para conex\u00f5es.',
        'panic-wifi-7':'Seu roteador pode estar bloqueando broadcast UDP (porta 53210) entre dispositivos.',
        'panic-wifi-8':'O c\u00f3digo de emparelhamento est\u00e1 incorreto. Verifique o c\u00f3digo de 6 d\u00edgitos no painel do PC.',
        'panic-usb-1':'A "Ancoragem USB" n\u00e3o est\u00e1 ativada. V\u00e1 em Configura\u00e7\u00f5es &gt; Redes &gt; Roteador Wi-Fi/Ancoragem.',
        'panic-usb-2':'O cabo USB n\u00e3o suporta transfer\u00eancia de dados (apenas carga). Tente outro cabo.',
        'panic-usb-3':'O Firewall do Windows est\u00e1 bloqueando a conex\u00e3o. Execute o LunaDeck como Administrador.',
        'panic-usb-4':'Tente outro cabo USB ou porta.',
        'panic-usb-5':'Desconecte o USB, ative a Ancoragem USB novamente e tente de novo.',
        'panic-usb-6':'Certifique-se de que o servidor LunaDeck esteja em execu\u00e7\u00e3o no PC.',
        'panic-usb-7':'Reinicie o celular e o PC, depois tente novamente.',
        'panic-usb-8':'Se o problema persistir, tente conectar via Wi-Fi ou c\u00f3digo QR.',
        'scan':'Escanear QR','manual':'IP Manual','exit':'Sair','retry':'Reconectar',
        'error':'N\u00e3o foi poss\u00edvel conectar. Certifique-se de que o LunaDeck esteja aberto no seu PC e tente execut\u00e1-lo como Administrador.'
      }
    };
  }

  function t(key) {
    ensureDict();
    var dict = _dict[lang] || _dict.en;
    return dict[key] || key;
  }

  // ----- TRANSLATE ALL -----
  function applyLang() {
    document.getElementById('btn-lang').textContent = lang.toUpperCase();
    document.getElementById('onb-title-main').innerHTML = t('title-main');
    document.getElementById('onb-subtitle').innerHTML = t('subtitle');
    document.getElementById('onb-card-wifi-title').innerHTML = t('card-wifi-title');
    document.getElementById('onb-card-wifi-desc').innerHTML = t('card-wifi-desc');
    document.getElementById('onb-card-usb-title').innerHTML = t('card-usb-title');
    document.getElementById('onb-card-usb-desc').innerHTML = t('card-usb-desc');
    document.getElementById('onb-back').innerHTML = t('back');
    document.getElementById('onb-back-2').innerHTML = t('back-2');
    document.getElementById('onb-wifi-title').innerHTML = t('wifi-title');
    document.getElementById('onb-wifi-sub').innerHTML = t('wifi-sub');
    document.getElementById('onb-wifi-step1').innerHTML = t('wifi-step1');
    document.getElementById('onb-wifi-step2').innerHTML = t('wifi-step2');
    document.getElementById('onb-wifi-step3').innerHTML = t('wifi-step3');
    document.getElementById('onb-wifi-step4').innerHTML = t('wifi-step4');
    document.getElementById('onb-wifi-step5').innerHTML = t('wifi-step5');
    document.getElementById('onb-wifi-btn').innerHTML = t('wifi-btn');
    document.getElementById('onb-usb-title').innerHTML = t('usb-title');
    document.getElementById('onb-usb-sub').innerHTML = t('usb-sub');
    document.getElementById('onb-usb-step1').innerHTML = t('usb-step1');
    document.getElementById('onb-usb-step2').innerHTML = t('usb-step2');
    document.getElementById('onb-usb-step3').innerHTML = t('usb-step3');
    document.getElementById('onb-usb-step4').innerHTML = t('usb-step4');
    document.getElementById('onb-usb-step5').innerHTML = t('usb-step5');
    document.getElementById('onb-usb-step6').innerHTML = t('usb-step6');
    document.getElementById('onb-usb-btn').innerHTML = t('usb-btn');
    document.getElementById('onb-scan').innerHTML = t('scan');
    document.getElementById('onb-manual').innerHTML = t('manual');
    document.getElementById('onb-exit').innerHTML = t('exit');
    document.getElementById('onb-retry').innerHTML = t('retry');
    document.getElementById('onb-error-text').textContent = t('error');
    document.getElementById('onb-panic').innerHTML = t('panic');
    document.getElementById('onb-panic-2').innerHTML = t('panic-2');
    document.getElementById('onb-panic-ok').innerHTML = t('panic-ok');
    document.title = 'LunaDeck | ' + t('wifi-title');
  }

  // ----- NAVIGATION -----
  function goToSlide(id) {
    var slides = document.querySelectorAll('.slide');
    for (var i = 0; i < slides.length; i++) slides[i].classList.remove('active');
    var el = document.getElementById(id);
    if (el) el.classList.add('active');
  }

  // ----- PANIC -----
  function showPanic(mode) {
    var list = document.getElementById('panic-list');
    document.getElementById('onb-panic-title').innerHTML = t('panic-title');
    var html = '';
    for (var i = 1; i <= 8; i++) {
      html += '<li><span class="panic-bullet">&bull;</span><span>' + t('panic-' + mode + '-' + i) + '</span></li>';
    }
    list.innerHTML = html;
    document.getElementById('overlay-panic').style.display = 'flex';
  }

  function hidePanic() {
    document.getElementById('overlay-panic').style.display = 'none';
  }

  // ----- LANGUAGE PICKER -----
  function showLangPicker() {
    var overlay = document.getElementById('lang-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.id = 'lang-overlay';
      overlay.style.cssText = 'position:fixed;inset:0;z-index:200;display:flex;align-items:center;justify-content:center;animation:fade-in 0.2s ease;';
      var bg = document.createElement('div');
      bg.style.cssText = 'position:absolute;inset:0;background:rgba(0,0,0,0.6);backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px);';
      bg.onclick = hideLangPicker;
      overlay.appendChild(bg);
      var card = document.createElement('div');
      card.style.cssText = 'position:relative;background:#1A1A1A;border:1px solid #2A2A2A;border-radius:20px;padding:28px 24px 20px;width:280px;max-width:85vw;text-align:center;animation:overlay-in 0.3s ease;';
      var title = document.createElement('div');
      title.style.cssText = 'font-size:14px;color:#888;margin-bottom:16px;';
      title.id = 'onb-lang-title';
      title.innerHTML = 'Select language';
      card.appendChild(title);
      var opts = ['en','es','pt'];
      var labels = { en:'English', es:'Espa\u00f1ol', pt:'Portugu\u00eas' };
      for (var i = 0; i < opts.length; i++) {
        var btn = document.createElement('button');
        var isActive = opts[i] === lang;
        btn.style.cssText = 'display:block;width:100%;background:' + (isActive ? 'rgba(79,195,247,0.15)' : 'transparent') + ';border:' + (isActive ? '1.5px solid #4FC3F7' : '1px solid #2A2A2A') + ';border-radius:12px;color:' + (isActive ? '#4FC3F7' : '#CCC') + ';font-size:15px;font-weight:' + (isActive ? '700' : '500') + ';padding:12px 16px;cursor:pointer;margin-bottom:8px;text-align:left;transition:all 0.15s;';
        btn.textContent = labels[opts[i]];
        btn.dataset.lang = opts[i];
        (function(l) {
          btn.onclick = function() { setLang(l); hideLangPicker(); };
        })(opts[i]);
        card.appendChild(btn);
      }
      overlay.appendChild(card);
      document.body.appendChild(overlay);
      // translate title
      var langs3 = ['en','es','pt'];
      var langTitles = { en:'Select language', es:'Seleccionar idioma', pt:'Selecionar idioma' };
      document.getElementById('onb-lang-title').textContent = langTitles[lang];
    }
    overlay.style.display = 'flex';
  }

  function hideLangPicker() {
    var el = document.getElementById('lang-overlay');
    if (el) el.style.display = 'none';
  }

  function setLang(newLang) {
    lang = newLang;
    applyLang();
  }

  // ----- ERROR -----
  function showError() {
    document.getElementById('slide-error').style.display = 'flex';
    if (typeof LunaBridge !== 'undefined' && LunaBridge.hasSavedConnection()) {
      document.getElementById('btn-retry').style.display = 'block';
    }
  }

  // ====== GUARD: safely attach listeners ======
  function $(id, fn) {
    var el = document.getElementById(id);
    if (el) el.addEventListener('click', fn);
  }

  // ====== EVENT LISTENERS (keep Wi-Fi ones untouched!) ======
  $('btn-lang', showLangPicker);
  $('card-wifi', function() { goToSlide('slide-wifi'); });
  $('card-usb', function() { goToSlide('slide-usb'); });
  $('back-wifi', function() { goToSlide('slide-main'); });
  $('back-usb', function() { goToSlide('slide-main'); });
  $('btn-wifi-search', function() { if (typeof LunaBridge !== 'undefined') LunaBridge.searchWiFi(); });
  $('btn-usb-connect', function() { if (typeof LunaBridge !== 'undefined') LunaBridge.connectUSB(); });
  $('panic-wifi', function() { showPanic('wifi'); });
  $('panic-usb', function() { showPanic('usb'); });
  $('overlay-close', hidePanic);
  $('overlay-gotit', hidePanic);
  $('overlay-backdrop', hidePanic);
  $('link-scan', function() { if (typeof LunaBridge !== 'undefined') LunaBridge.scanQR(); });
  $('link-manual', function() { if (typeof LunaBridge !== 'undefined') LunaBridge.showManualEntry(); });
  $('link-exit', function() { if (typeof LunaBridge !== 'undefined') LunaBridge.finishApp(); });
  $('btn-retry', function() { if (typeof LunaBridge !== 'undefined') LunaBridge.retryConnection(); });

  // ====== INIT ======
  lang = getLang();
  isError = location.search.indexOf('error=1') >= 0;
  applyLang();
  if (isError) showError();
})();
