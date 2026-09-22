import sys
import os
import winreg
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QCheckBox, QSpinBox, QGroupBox, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal

try:
    from src.config import config
    from src.ui.theme import THEME_STYLESHEET
except ImportError:
    from config import config
    from ui.theme import THEME_STYLESHEET

class SettingsDialog(QDialog):
    hotkey_updated = pyqtSignal(str)
    quit_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações - InputTranslator")
        self.setFixedSize(460, 420)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet(THEME_STYLESHEET + """
            QDialog {
                background-color: #13161f;
                color: #e2e8f0;
            }
            QGroupBox {
                border: 1px solid #282f45;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 14px;
                font-weight: 600;
                color: #94a3b8;
                font-size: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 6px;
            }
            QLineEdit, QSpinBox {
                background-color: #1a1d27;
                color: #f8fafc;
                border: 1px solid #2e354a;
                border-radius: 6px;
                padding: 5px 8px;
            }
        """)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Cabeçalho
        title = QLabel("⚙ Configurações do Tradutor", self)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #f1f5f9;")
        layout.addWidget(title)

        subtitle = QLabel("Personalize o atalho global e o comportamento de envio.", self)
        subtitle.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(subtitle)

        # Grupo 1: Atalho Global
        hotkey_group = QGroupBox("Atalho Global de Ativação", self)
        hotkey_layout = QVBoxLayout(hotkey_group)
        hotkey_layout.setSpacing(8)

        hk_row = QHBoxLayout()
        hk_label = QLabel("Atalho atual:", hotkey_group)
        self.hotkey_input = QLineEdit(hotkey_group)
        self.hotkey_input.setText(config.get("hotkey", "alt+t"))
        self.hotkey_input.setPlaceholderText("ex: alt+t, ctrl+alt+t, ctrl+shift+t")
        hk_row.addWidget(hk_label)
        hk_row.addWidget(self.hotkey_input)
        hotkey_layout.addLayout(hk_row)

        hk_help = QLabel("Exemplos: alt+t, ctrl+alt+t, ctrl+shift+t, alt+space", hotkey_group)
        hk_help.setStyleSheet("color: #64748b; font-size: 11px;")
        hotkey_layout.addWidget(hk_help)
        layout.addWidget(hotkey_group)

        # Grupo 2: Comportamento
        behavior_group = QGroupBox("Comportamento de Envio", self)
        behavior_layout = QVBoxLayout(behavior_group)
        behavior_layout.setSpacing(10)

        self.auto_send_check = QCheckBox("Enviar automaticamente após colar (simula Enter)", behavior_group)
        self.auto_send_check.setChecked(config.get("auto_send", True))
        behavior_layout.addWidget(self.auto_send_check)

        delay_row = QHBoxLayout()
        delay_label = QLabel("Atraso antes de colar (ms):", behavior_group)
        self.delay_spin = QSpinBox(behavior_group)
        self.delay_spin.setRange(30, 1000)
        self.delay_spin.setSingleStep(10)
        self.delay_spin.setValue(config.get("paste_delay_ms", 100))
        delay_row.addWidget(delay_label)
        delay_row.addWidget(self.delay_spin)
        delay_row.addStretch()
        behavior_layout.addLayout(delay_row)

        self.startup_check = QCheckBox("Iniciar junto com o Windows", behavior_group)
        self.startup_check.setChecked(self._is_startup_enabled())
        behavior_layout.addWidget(self.startup_check)

        layout.addWidget(behavior_group)

        layout.addStretch()

        # Botões de Ação
        buttons_layout = QHBoxLayout()

        quit_btn = QPushButton("❌ Encerrar App", self)
        quit_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a151b;
                color: #f87171;
                border: 1px solid #4c1d28;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3b1d25;
                color: #fca5a5;
                border-color: #ef4444;
            }
        """)
        quit_btn.setToolTip("Finaliza completamente o processo do InputTranslator")
        quit_btn.clicked.connect(self._confirm_quit)
        buttons_layout.addWidget(quit_btn)

        buttons_layout.addStretch()

        cancel_btn = QPushButton("Cancelar", self)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Salvar Alterações", self)
        save_btn.setObjectName("PrimaryButton")
        save_btn.clicked.connect(self._save_settings)
        buttons_layout.addWidget(save_btn)

        layout.addLayout(buttons_layout)

    def _confirm_quit(self):
        reply = QMessageBox.question(
            self,
            "Encerrar Aplicativo",
            "Deseja realmente finalizar o processo do InputTranslator?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.quit_requested.emit()

    def showEvent(self, event):
        super().showEvent(event)
        self.hotkey_input.setText(config.get("hotkey", "alt+t"))
        self.auto_send_check.setChecked(config.get("auto_send", True))
        self.delay_spin.setValue(config.get("paste_delay_ms", 100))
        self.startup_check.setChecked(self._is_startup_enabled())

    def _is_startup_enabled(self) -> bool:
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

    def _set_startup_enabled(self, enable: bool):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            if enable:
                # Se for executável compilado ou script python
                if getattr(sys, 'frozen', False):
                    exe_path = f'"{sys.executable}"'
                else:
                    python_exe = sys.executable
                    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
                    # Executar com pythonw para não abrir console
                    pythonw = python_exe.replace("python.exe", "pythonw.exe")
                    exe_path = f'"{pythonw}" "{script_path}"'
                
                winreg.SetValueEx(key, "InputTranslator", 0, winreg.REG_SZ, exe_path)
            else:
                try:
                    winreg.DeleteValue(key, "InputTranslator")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Erro ao configurar inicializacao com Windows: {e}")

    def _save_settings(self):
        new_hotkey = self.hotkey_input.text().strip().lower()
        old_hotkey = config.get("hotkey", "alt+t")

        config.set("hotkey", new_hotkey)
        config.set("auto_send", self.auto_send_check.isChecked())
        config.set("paste_delay_ms", self.delay_spin.value())

        should_startup = self.startup_check.isChecked()
        self._set_startup_enabled(should_startup)
        config.set("start_with_windows", should_startup)

        if new_hotkey != old_hotkey:
            self.hotkey_updated.emit(new_hotkey)

        self.accept()
