import sys
import os
from pathlib import Path

# Garante que a raiz do projeto e a pasta src estejam no sys.path
_current_file = Path(__file__).resolve()
_src_dir = _current_file.parent
_root_dir = _src_dir.parent

for _p in (str(_root_dir), str(_src_dir)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from PyQt6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu
)
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor, QFont, QBrush, QPen
from PyQt6.QtCore import Qt

try:
    from src.config import config
    from src.core.hotkey import HotkeyListener
    from src.ui.overlay import TranslatorOverlay
    from src.ui.settings_dialog import SettingsDialog
except ImportError:
    from config import config
    from core.hotkey import HotkeyListener
    from ui.overlay import TranslatorOverlay
    from ui.settings_dialog import SettingsDialog


def get_resource_path(relative_path: str) -> str:
    """Resolve o caminho do recurso em desenvolvimento e quando compilado com PyInstaller."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent.parent
    return str(base_path / relative_path)


def load_app_icon() -> QIcon:
    """Carrega o ícone oficial ou gera um ícone nítido para a bandeja do sistema."""
    possible_paths = [
        get_resource_path("assets/icon.png"),
        str(Path(__file__).resolve().parent.parent / "assets" / "icon.png"),
        os.path.join(os.path.dirname(sys.executable), "assets", "icon.png"),
        os.path.join(os.path.dirname(sys.executable), "icon.png")
    ]

    for path in possible_paths:
        if os.path.exists(path):
            icon = QIcon(path)
            if not icon.isNull():
                return icon

    # Fallback garantido usando QPainter caso o arquivo não seja encontrado
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Fundo azul moderno arredondado
    painter.setBrush(QBrush(QColor(37, 99, 235)))
    painter.setPen(QPen(QColor(96, 165, 250), 2))
    painter.drawRoundedRect(4, 4, 56, 56, 14, 14)

    # Letra T estilizada
    painter.setPen(QPen(QColor(255, 255, 255)))
    font = QFont("Segoe UI", 26, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "T")
    painter.end()

    return QIcon(pixmap)


class InputTranslatorApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("InputTranslator")
        self.app.setQuitOnLastWindowClosed(False)

        # Ícone da aplicação garantido
        self.app_icon = load_app_icon()
        self.app.setWindowIcon(self.app_icon)

        # Janelas
        self.overlay = TranslatorOverlay()
        self.settings_dialog = None

        # Conectar sinais da barra flutuante
        self._opened_from_overlay = False
        self.overlay.open_settings_requested.connect(lambda: self.show_settings(from_overlay=True))
        self.overlay.quit_requested.connect(self.quit_app)

        # Inicializa o atalho global
        self.current_hotkey = config.get("hotkey", "alt+t")
        self.hotkey_listener = HotkeyListener(self.current_hotkey)
        self.hotkey_listener.triggered.connect(self.on_hotkey_triggered)

        # Inicializa o System Tray
        self._init_tray()

    def _init_tray(self):
        self.tray_icon = QSystemTrayIcon(self.app_icon, self.app)
        self.tray_icon.setToolTip(f"InputTranslator (Atalho: {self.current_hotkey.upper()})\nClique com botão direito para opções")

        tray_menu = QMenu()
        tray_menu.setStyleSheet("""
            QMenu {
                background-color: #161922;
                color: #e2e8f0;
                border: 1px solid #2b3040;
                border-radius: 8px;
                padding: 6px;
                font-size: 13px;
            }
            QMenu::item {
                padding: 6px 24px;
                border-radius: 6px;
            }
            QMenu::item:selected {
                background-color: #3b82f6;
                color: #ffffff;
            }
            QMenu::separator {
                height: 1px;
                background-color: #2b3040;
                margin: 4px 6px;
            }
        """)

        # Ação Abrir Tradutor
        self.open_action = QAction(f"🌐 Abrir Tradutor ({self.current_hotkey.upper()})", tray_menu)
        font = self.open_action.font()
        font.setBold(True)
        self.open_action.setFont(font)
        self.open_action.triggered.connect(lambda: self.overlay.show_overlay(0))
        tray_menu.addAction(self.open_action)

        # Ação Configurações
        settings_action = QAction("⚙️ Configurações...", tray_menu)
        settings_action.triggered.connect(lambda: self.show_settings(from_overlay=False))
        tray_menu.addAction(settings_action)

        tray_menu.addSeparator()

        # Ação Iniciar com o Windows (Toggle direto pelo menu!)
        self.startup_action = QAction("🔄 Iniciar com o Windows", tray_menu)
        self.startup_action.setCheckable(True)
        self.startup_action.setChecked(self._is_startup_enabled())
        self.startup_action.triggered.connect(self._toggle_startup)
        tray_menu.addAction(self.startup_action)

        tray_menu.addSeparator()

        # Ação Finalizar/Encerrar Processo
        quit_action = QAction("❌ Encerrar InputTranslator", tray_menu)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        
        # Exibe o ícone explicitamente
        self.tray_icon.show()

        # Notificação inicial na área de notificação do Windows
        self.tray_icon.showMessage(
            "InputTranslator Ativo",
            f"O tradutor está pronto! Pressione {self.current_hotkey.upper()} a qualquer momento para traduzir e enviar.",
            QSystemTrayIcon.MessageIcon.Information,
            4000
        )

    def _is_startup_enabled(self) -> bool:
        import winreg
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            _, _ = winreg.QueryValueEx(key, "InputTranslator")
            winreg.CloseKey(key)
            return True
        except Exception:
            return False

    def _toggle_startup(self, checked: bool):
        import winreg
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            if checked:
                if getattr(sys, 'frozen', False):
                    exe_path = f'"{sys.executable}"'
                else:
                    python_exe = sys.executable
                    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))
                    pythonw = python_exe.replace("python.exe", "pythonw.exe")
                    exe_path = f'"{pythonw}" "{script_path}"'
                winreg.SetValueEx(key, "InputTranslator", 0, winreg.REG_SZ, exe_path)
            else:
                try:
                    winreg.DeleteValue(key, "InputTranslator")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
            config.set("start_with_windows", checked)
        except Exception as e:
            print(f"Erro ao alternar inicializacao: {e}")

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:  # Clique esquerdo
            if self.overlay.isVisible():
                self.overlay.hide_overlay()
            else:
                self.overlay.show_overlay(0)

    def on_hotkey_triggered(self, hwnd: int):
        if self.overlay.isVisible():
            self.overlay.hide_overlay()
        else:
            self.overlay.show_overlay(hwnd)

    def show_settings(self, from_overlay=False):
        self._opened_from_overlay = from_overlay

        # Oculta a barra de tradução para que a tela de configurações fique isolada e limpa
        if self.overlay.isVisible():
            self.overlay.hide_overlay()

        if not self.settings_dialog:
            self.settings_dialog = SettingsDialog()
            self.settings_dialog.hotkey_updated.connect(self.on_hotkey_updated)
            self.settings_dialog.finished.connect(self._on_settings_finished)
            self.settings_dialog.quit_requested.connect(self.quit_app)

        # Atualiza o estado da opção de inicialização
        if hasattr(self, 'startup_action'):
            self.startup_action.setChecked(self._is_startup_enabled())

        # Centraliza a tela de configurações na tela ativa
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.settings_dialog.width()) // 2
        y = (screen.height() - self.settings_dialog.height()) // 2
        self.settings_dialog.move(x, y)

        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()

    def _on_settings_finished(self):
        # Atualiza o item de inicialização do menu se tiver mudado nas configurações
        if hasattr(self, 'startup_action'):
            self.startup_action.setChecked(self._is_startup_enabled())

        # Se foi aberto a partir da barra de tradução, reabre a barra com foco
        if getattr(self, "_opened_from_overlay", False):
            self._opened_from_overlay = False
            self.overlay.show_overlay(self.overlay.target_hwnd)

    def on_hotkey_updated(self, new_hotkey: str):
        self.current_hotkey = new_hotkey
        self.hotkey_listener.register(new_hotkey)
        self.open_action.setText(f"🌐 Abrir Tradutor ({new_hotkey.upper()})")
        self.tray_icon.setToolTip(f"InputTranslator (Atalho: {new_hotkey.upper()})\nClique com botão direito para opções")
        self.tray_icon.showMessage(
            "Atalho Atualizado",
            f"O novo atalho global é {new_hotkey.upper()}",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )

    def quit_app(self):
        """Finaliza o processo completamente."""
        try:
            self.hotkey_listener.unregister()
        except Exception:
            pass

        if hasattr(self, "tray_icon") and self.tray_icon:
            self.tray_icon.hide()

        self.app.quit()
        # Garante encerramento imediato do processo no Windows
        os._exit(0)

    def run(self):
        return self.app.exec()


def main():
    app = InputTranslatorApp()
    sys.exit(app.run())

if __name__ == "__main__":
    main()
