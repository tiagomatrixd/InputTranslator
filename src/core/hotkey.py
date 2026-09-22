import keyboard
from PyQt6.QtCore import QObject, pyqtSignal

try:
    from src.core.injector import TextInjector
except ImportError:
    from core.injector import TextInjector

class HotkeyListener(QObject):
    triggered = pyqtSignal(int)  # Emite o HWND da janela que estava em primeiro plano

    def __init__(self, hotkey_str: str = "alt+t"):
        super().__init__()
        self.current_hotkey = None
        self.hotkey_hook = None
        self.register(hotkey_str)

    def _on_hotkey_pressed(self):
        # Captura imediatamente a janela em primeiro plano (ex: chat do Telegram)
        hwnd = TextInjector.get_foreground_window()
        self.triggered.emit(hwnd if hwnd else 0)

    def register(self, hotkey_str: str):
        if not hotkey_str:
            return

        # Desregistra o atalho anterior se houver
        self.unregister()

        try:
            self.hotkey_hook = keyboard.add_hotkey(
                hotkey_str,
                self._on_hotkey_pressed,
                suppress=True
            )
            self.current_hotkey = hotkey_str
            print(f"[Hotkey] Atalho registrado com sucesso: {hotkey_str}")
        except Exception as e:
            print(f"[Hotkey] Erro ao registrar atalho '{hotkey_str}': {e}")

    def unregister(self):
        if self.current_hotkey:
            try:
                keyboard.remove_hotkey(self.current_hotkey)
            except Exception:
                pass
            self.current_hotkey = None
