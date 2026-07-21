import os

# All strings organized by category
# [key, english, spanish, portuguese]
STRINGS = [
    # App
    ("app_name", "Luna", "Luna", "Luna"),

    # Camera / QR
    ("camera_perm_required", "Camera permission required", "Permiso de c\u00e1mara requerido", "Permiss\u00e3o de c\u00e2mera necess\u00e1ria"),
    ("scan_qr_prompt", "Scan the Luna server QR code", "Escanea el c\u00f3digo QR del servidor Luna", "Escaneie o c\u00f3digo QR do servidor Luna"),
    ("scan_qr", "Scan QR", "Escanear QR", "Escanear QR"),

    # Connection
    ("server_not_found", "Server not found at {0}", "Servidor no encontrado en {0}", "Servidor n\u00e3o encontrado em {0}"),
    ("config_error", "Error getting configuration", "Error al obtener configuraci\u00f3n", "Erro ao obter configura\u00e7\u00e3o"),
    ("connected", "Connected", "Conectado", "Conectado"),
    ("disconnected", "Disconnected", "Desconectado", "Desconectado"),
    ("connecting", "Connecting...", "Conectando...", "Conectando..."),
    ("status_connected", "Connected", "Conectado", "Conectado"),
    ("status_disconnected", "Disconnected", "Desconectado", "Desconectado"),
    ("status_error", "Connection error", "Error de conexi\u00f3n", "Erro de conex\u00e3o"),
    ("reconnect_toast", "Connection lost \u2014 Scan the QR on your PC", "Conexi\u00f3n perdida \u2014 Escanea el QR en tu PC", "Conex\u00e3o perdida \u2014 Escaneie o QR no seu PC"),
    ("conn_info_label", "Connected at:", "Conectado en:", "Conectado em:"),
    ("conn_info_none", "No server connection", "Sin conexi\u00f3n al servidor", "Sem conex\u00e3o com o servidor"),
    ("disconnect_btn", "Disconnect", "Desconectar", "Desconectar"),
    ("manual_connect_title", "Connect to Luna", "Conectar a Luna", "Conectar ao Luna"),
    ("manual_connect_msg", "Enter the server IP", "Ingresa la IP del servidor", "Digite o IP do servidor"),
    ("manual_connect_hint", "e.g. 192.168.1.100:9120", "ej: 192.168.1.100:9120", "ex: 192.168.1.100:9120"),
    ("manual_connect_btn", "Connect", "Conectar", "Conectar"),
    ("connect_cancel", "Cancel", "Cancelar", "Cancelar"),

    # Menu / Settings
    ("menu_title", "Menu", "Men\u00fa", "Menu"),
    ("menu_help", "Help", "Ayuda", "Ajuda"),
    ("menu_settings", "Settings", "Configuraci\u00f3n", "Configura\u00e7\u00f5es"),
    ("menu_close", "Close", "Cerrar", "Fechar"),
    ("settings_title", "Settings", "Configuraci\u00f3n", "Configura\u00e7\u00f5es"),
    ("settings_connection", "Connection", "Conexi\u00f3n", "Conex\u00e3o"),
    ("settings_server", "Server", "Servidor", "Servidor"),
    ("settings_not_connected", "Not connected", "No conectado", "N\u00e3o conectado"),
    ("settings_personalization", "Personalization", "Personalizaci\u00f3n", "Personaliza\u00e7\u00e3o"),
    ("settings_themes", "Themes", "Dise\u00f1os", "Temas"),
    ("settings_behavior", "Behavior", "Comportamiento", "Comportamento"),
    ("settings_wakelock", "Keep screen on", "Mantener pantalla encendida", "Manter tela ligada"),
    ("settings_wakelock_summary", "Prevent the screen from turning off", "Evita que la pantalla se apague", "Evita que a tela desligue"),
    ("settings_notifications", "Notifications", "Notificaciones", "Notifica\u00e7\u00f5es"),
    ("settings_notif_summary", "Notify on connection change", "Notificar cambio de conexi\u00f3n", "Notificar mudan\u00e7a de conex\u00e3o"),

    # Help dialog
    ("help_title", "Help", "Ayuda", "Ajuda"),
    ("help_got_it", "Got it", "Entendido", "Entendi"),
    ("help_step1", "Download LunaDeck on your PC from\nsr-lolo.github.io/luna", "Descarga LunaDeck en tu PC desde\nsr-lolo.github.io/luna", "Baixe o LunaDeck no seu PC em\nsr-lolo.github.io/luna"),
    ("help_step2", "Open LunaDeck on your PC and press\nthe QR button", "Abre LunaDeck en tu PC y presiona\nel bot\u00f3n QR", "Abra o LunaDeck no seu PC e pressione\no bot\u00e3o QR"),
    ("help_step3", "Scan the QR code from this\napp to connect automatically", "Escanea el c\u00f3digo QR desde esta\napp para conectar autom\u00e1ticamente", "Escaneie o c\u00f3digo QR deste\napp para conectar automaticamente"),
    ("help_step4", "Use the on-screen buttons to\ncontrol your PC instantly", "Usa los botones en pantalla para\ncontrolar tu PC al instante", "Use os bot\u00f5es na tela para\ncontrolar seu PC instantaneamente"),
    ("help_hint", "You can also enter the IP manually from Settings", "Tambi\u00e9n puedes ingresar la IP manualmente desde Configuraci\u00f3n", "Voc\u00ea tamb\u00e9m pode digitar o IP manualmente nas Configura\u00e7\u00f5es"),

    # Theme picker
    ("theme_picker_title", "Themes", "Dise\u00f1os", "Temas"),
    ("theme_dark", "Dark", "Oscuro", "Escuro"),
    ("theme_light", "Light", "Claro", "Claro"),
    ("theme_night_blue", "Night Blue", "Azul Nocturno", "Azul Noturno"),
    ("theme_neon_green", "Neon Green", "Ne\u00f3n Verde", "Neon Verde"),
    ("theme_magenta", "Magenta", "Magenta", "Magenta"),
    ("theme_amber", "Amber", "\u00c1mbar", "\u00c2mbar"),
    ("theme_gaming_red", "Gaming Red", "Rojo Gaming", "Vermelho Gaming"),
    ("theme_purple", "Purple", "P\u00farpura", "Roxo"),

    # Update dialog
    ("update_title", "Update available", "Actualizaci\u00f3n disponible", "Atualiza\u00e7\u00e3o dispon\u00edvel"),
    ("update_message", "New version {0} available. Download and install?", "Nueva versi\u00f3n {0} disponible. \u00bfDescargar e instalar?", "Nova vers\u00e3o {0} dispon\u00edvel. Baixar e instalar?"),
    ("update_btn", "Update", "Actualizar", "Atualizar"),
    ("update_not_now", "Not now", "Ahora no", "Agora n\u00e3o"),
    ("update_downloading", "Downloading update", "Descargando actualizaci\u00f3n", "Baixando atualiza\u00e7\u00e3o"),

    # Errors
    ("error_install", "Install error: enable 'Install unknown apps' in settings", "Error al instalar: habilita 'Instalar apps desconocidas' en ajustes", "Erro ao instalar: habilite 'Instalar apps desconhecidas' nas configura\u00e7\u00f5es"),
    ("error_download", "Download error: {0}", "Error al descargar: {0}", "Erro ao baixar: {0}"),

    # Share
    ("share_text", "Download LunaDeck for PC: https://sr-lolo.github.io/luna/", "Descarga LunaDeck para PC: https://sr-lolo.github.io/luna/", "Baixe LunaDeck para PC: https://sr-lolo.github.io/luna/"),
    ("share_title", "Share link", "Compartir enlace", "Compartilhar link"),

    # Notification
    ("notif_channel", "Luna Connection", "Conexi\u00f3n Luna", "Conex\u00e3o Luna"),
    ("notif_title", "LunaDeck", "LunaDeck", "LunaDeck"),
    ("notif_connected", "Connected to {0}:{1}", "Conectado a {0}:{1}", "Conectado a {0}:{1}"),
    ("notif_disconnected", "Connection lost", "Conexi\u00f3n perdida", "Conex\u00e3o perdida"),

    # Layout: header
    ("mode_keyboard", "Keyboard", "Teclado", "Teclado"),
    ("mode_sliders", "Sliders", "Sliders", "Sliders"),
    ("auto_switch", "Auto switch", "Cambio autom\u00e1tico", "Troca autom\u00e1tica"),
    ("hide_ui", "Hide UI", "Ocultar UI", "Ocultar UI"),
    ("rescan_qr", "Scan QR", "Escanear QR", "Escanear QR"),

    # Layout: sliders
    ("slider_volume", "Volume", "Volumen", "Volume"),
    ("slider_brightness", "Brightness", "Brillo", "Brilho"),
    ("slider_scroll_v", "Scroll V", "Despl. V", "Scroll V"),
    ("slider_scroll_h", "Scroll H", "Despl. H", "Scroll H"),
    ("slider_hint", "Drag here", "Arrastra aqu\u00ed", "Arraste aqui"),

    # APK banner
    ("apk_banner_text", "Prefer no address bar? Download the Luna APK app", "\u00bfPrefieres sin barra? Descarga la app Luna APK", "Prefere sem barra? Baixe o app Luna APK"),
    ("apk_banner_download", "Download", "Descargar", "Baixar"),

    # QR modal
    ("qr_close", "Close", "Cerrar", "Fechar"),

    # Onboarding
    ("onb_slide1_title", "Turn this device into your ultimate macro panel for streaming and design", "Convierte este dispositivo en tu panel de macros definitivo para streaming y dise\u00f1o", "Transforme este dispositivo em seu painel de macros definitivo para streaming e design"),
    ("onb_slide1_next", "Next", "Siguiente", "Pr\u00f3ximo"),
    ("onb_slide2_title", "You need the PC server", "Necesitas el servidor de PC", "Voc\u00ea precisa do servidor PC"),
    ("onb_slide2_desc", "Open your PC and visit sr-lolo.github.io/luna from any browser to download LunaDeck for Windows. You can also send yourself the link from here.", "Abre tu PC y visita sr-lolo.github.io/luna desde cualquier navegador para descargar LunaDeck para Windows. Tambi\u00e9n puedes enviarte el enlace desde aqu\u00ed.", "Abra seu PC e visite sr-lolo.github.io/luna de qualquer navegador para baixar o LunaDeck para Windows. Voc\u00ea tamb\u00e9m pode enviar o link daqui."),
    ("onb_slide2_share", "Share link with my PC", "Compartir enlace con mi PC", "Compartilhar link com meu PC"),
    ("onb_slide2_have_it", "I have it, next", "Ya lo tengo, siguiente", "J\u00e1 tenho, pr\u00f3ximo"),
    ("onb_slide3_title", "Scan the QR code", "Escanea el c\u00f3digo QR", "Escaneie o c\u00f3digo QR"),
    ("onb_slide3_desc", "Open LunaDeck on your PC and press the QR button. Scan the code with your camera to connect instantly.", "Abre LunaDeck en tu PC y presiona el bot\u00f3n QR. Escanea el c\u00f3digo con tu c\u00e1mara para conectar al instante.", "Abra o LunaDeck no seu PC e pressione o bot\u00e3o QR. Escaneie o c\u00f3digo com sua c\u00e2mera para conectar instantaneamente."),
    ("onb_slide3_scan", "Scan QR", "Escanear QR", "Escanear QR"),
    ("onb_slide3_retry", "Retry connection", "Reintentar conexi\u00f3n", "Reconectar"),
    ("onb_slide3_manual", "Enter IP manually", "Ingresar IP manual", "Digitar IP manualmente"),
    ("onb_slide3_exit", "Exit", "Salir", "Sair"),
    ("onb_error", "Server not found. Make sure LunaDeck is open on your PC.", "Servidor no encontrado. Aseg\u00farate de tener LunaDeck abierto en tu PC.", "Servidor n\u00e3o encontrado. Certifique-se de que o LunaDeck est\u00e1 aberto no seu PC."),
]

def write_strings_xml(path, lang_index):
    """Generate strings.xml for a given language index (0=EN, 1=ES, 2=PT)"""
    lines = ['<?xml version="1.0" encoding="utf-8"?>', '<resources>']
    for key, en, es, pt in STRINGS:
        val = [en, es, pt][lang_index]
        # Escape XML special chars
        val = val.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", "&apos;")
        lines.append(f'    <string name="{key}">{val}</string>')
    lines.append('</resources>')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
        f.write('\n')

base = r'C:\Users\Infinity Tech\Desktop\Mis Cosas\Proyecto Luna\LunaDeck v1.7.55\android\app\src\main\res'
write_strings_xml(os.path.join(base, 'values', 'strings.xml'), 0)   # English (default)
write_strings_xml(os.path.join(base, 'values-es', 'strings.xml'), 1) # Spanish
write_strings_xml(os.path.join(base, 'values-pt', 'strings.xml'), 2) # Portuguese
print("strings.xml created for EN (default), ES, PT")
print(f"Total strings: {len(STRINGS)}")
