from .protocol import KeyCommand, MODIFIER_MAP, ACTION_TAP, ACTION_PRESS, ACTION_RELEASE

_pressed_names: set = set()


def execute(cmd: KeyCommand) -> bool:
    import keyboard
    if cmd.action == ACTION_TAP:
        _send_tap(cmd, keyboard)
        return True
    elif cmd.action == ACTION_PRESS:
        _send_press(cmd, keyboard)
        return True
    elif cmd.action == ACTION_RELEASE:
        _send_release(cmd, keyboard)
        return True
    return False


def _build_key_name(cmd: KeyCommand) -> str:
    mod = MODIFIER_MAP.get(cmd.modifiers, "")
    if mod:
        return f"{mod}+{cmd.key}"
    return cmd.key


def _send_tap(cmd: KeyCommand, kb):
    key_name = _build_key_name(cmd)
    kb.send(key_name)


def _send_press(cmd: KeyCommand, kb):
    key_name = _build_key_name(cmd)
    kb.press(key_name)
    _pressed_names.add(key_name)


def _send_release(cmd: KeyCommand, kb):
    key_name = _build_key_name(cmd)
    kb.release(key_name)
    _pressed_names.discard(key_name)


def release_all():
    import keyboard
    for name in list(_pressed_names):
        try:
            keyboard.release(name)
        except Exception:
            pass
    _pressed_names.clear()
