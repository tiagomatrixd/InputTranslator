import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QTextEdit, 
    QLabel, QPushButton, QCheckBox, QFrame, QGraphicsDropShadowEffect,
    QApplication, QMenu
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt6.QtGui import QColor, QFont, QKeyEvent

try:
    from src.config import config, SUPPORTED_LANGUAGES
    from src.core.translator import TranslationWorker
    from src.core.injector import TextInjector
    from src.ui.theme import THEME_STYLESHEET
except ImportError:
    from config import config, SUPPORTED_LANGUAGES
    from core.translator import TranslationWorker
    from core.injector import TextInjector
    from ui.theme import THEME_STYLESHEET

class CustomInputEdit(QTextEdit):
    send_requested = pyqtSignal()
    cancel_requested = pyqtSignal()

    def keyPressEvent(self, event: QKeyEvent):
        # Enter sem Shift/Ctrl envia
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if not (event.modifiers() & (Qt.KeyboardModifier.ShiftModifier | Qt.KeyboardModifier.ControlModifier)):
                event.accept()
                self.send_requested.emit()
                return
            else:
                # Permite quebra de linha com Shift+Enter
                super().keyPressEvent(event)
                return

        # Esc fecha
        if event.key() == Qt.Key.Key_Escape:
            event.accept()
            self.cancel_requested.emit()
            return

        super().keyPressEvent(event)


class TranslatorOverlay(QWidget):
    open_settings_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.target_hwnd = None
        self.drag_position = QPoint()
        self.is_dragging = False

        self.translation_worker = None
        self.debounce_timer = QTimer(self)
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(250)
        self.debounce_timer.timeout.connect(self._start_translation)

        self.last_translated_text = ""
        self.last_detected_lang = ""

        self._init_window()
        self._init_ui()

    def _init_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(THEME_STYLESHEET)
        self.resize(config.get("window_width", 620), config.get("window_height", 280))

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Container Central com Borda Arredondada
        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("CentralWidget")
        
        # Sombra externa suave
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 8)
        self.central_widget.setGraphicsEffect(shadow)

        central_layout = QVBoxLayout(self.central_widget)
        central_layout.setContentsMargins(16, 14, 16, 14)
        central_layout.setSpacing(10)

        # 1. Barra de Cabeçalho (Idiomas + Ações)
        header_frame = QFrame(self.central_widget)
        header_frame.setObjectName("HeaderBar")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        # Ícone e Título
        title_label = QLabel("🌐 Tradutor", header_frame)
        title_label.setStyleSheet("color: #e2e8f0; font-size: 13px; font-weight: bold;")
        header_layout.addWidget(title_label)

        header_layout.addSpacing(6)

        # Seletor Idioma Origem
        self.source_combo = QComboBox(header_frame)
        for code, name in SUPPORTED_LANGUAGES.items():
            self.source_combo.addItem(name, code)
        self._set_combo_value(self.source_combo, config.get("source_lang", "auto"))
        self.source_combo.currentIndexChanged.connect(self._on_language_changed)
        header_layout.addWidget(self.source_combo)

        # Botão de Troca (Swap)
        self.swap_btn = QPushButton("⇄", header_frame)
        self.swap_btn.setObjectName("SwapButton")
        self.swap_btn.setToolTip("Inverter idiomas")
        self.swap_btn.setFixedWidth(34)
        self.swap_btn.clicked.connect(self._swap_languages)
        header_layout.addWidget(self.swap_btn)

        # Seletor Idioma Destino
        self.target_combo = QComboBox(header_frame)
        for code, name in SUPPORTED_LANGUAGES.items():
            if code != "auto":
                self.target_combo.addItem(name, code)
        self._set_combo_value(self.target_combo, config.get("target_lang", "en"))
        self.target_combo.currentIndexChanged.connect(self._on_language_changed)
        header_layout.addWidget(self.target_combo)

        header_layout.addStretch()

        # Botão Configurações
        settings_btn = QPushButton("⚙", header_frame)
        settings_btn.setObjectName("GhostButton")
        settings_btn.setToolTip("Configurações")
        settings_btn.setFixedWidth(28)
        settings_btn.clicked.connect(self.open_settings_requested.emit)
        header_layout.addWidget(settings_btn)

        # Botão Fechar
        close_btn = QPushButton("✕", header_frame)
        close_btn.setObjectName("GhostButton")
        close_btn.setToolTip("Fechar (Esc)")
        close_btn.setFixedWidth(28)
        close_btn.clicked.connect(self.hide_overlay)
        header_layout.addWidget(close_btn)

        central_layout.addWidget(header_frame)

        # 2. Campo de Entrada de Texto
        self.input_text = CustomInputEdit(self.central_widget)
        self.input_text.setObjectName("InputText")
        self.input_text.setPlaceholderText("Digite sua mensagem aqui... (Enter para enviar)")
        self.input_text.setFixedHeight(68)
        self.input_text.textChanged.connect(self._on_text_changed)
        self.input_text.send_requested.connect(self.send_translation)
        self.input_text.cancel_requested.connect(self.hide_overlay)
        central_layout.addWidget(self.input_text)

        # 3. Card de Tradução em Tempo Real
        self.result_card = QFrame(self.central_widget)
        self.result_card.setObjectName("ResultCard")
        result_layout = QVBoxLayout(self.result_card)
        result_layout.setContentsMargins(10, 8, 10, 8)
        result_layout.setSpacing(4)

        result_header = QHBoxLayout()
        result_header.setContentsMargins(0, 0, 0, 0)
        self.result_title = QLabel("Tradução:", self.result_card)
        self.result_title.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600;")
        result_header.addWidget(self.result_title)

        self.detected_badge = QLabel("", self.result_card)
        self.detected_badge.setObjectName("DetectedBadge")
        self.detected_badge.hide()
        result_header.addWidget(self.detected_badge)

        result_header.addStretch()

        self.status_label = QLabel("", self.result_card)
        self.status_label.setObjectName("StatusLabel")
        result_header.addWidget(self.status_label)

        result_layout.addLayout(result_header)

        self.result_label = QLabel("", self.result_card)
        self.result_label.setObjectName("ResultLabel")
        self.result_label.setWordWrap(True)
        self.result_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.result_label.setMinimumHeight(24)
        result_layout.addWidget(self.result_label)

        central_layout.addWidget(self.result_card)

        # 4. Rodapé de Ações
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 2, 0, 0)

        self.auto_send_check = QCheckBox("Enviar direto (Enter)", self.central_widget)
        self.auto_send_check.setChecked(config.get("auto_send", True))
        self.auto_send_check.stateChanged.connect(self._on_auto_send_changed)
        footer_layout.addWidget(self.auto_send_check)

        footer_layout.addStretch()

        # Botão Copiar
        self.copy_btn = QPushButton("📋 Copiar", self.central_widget)
        self.copy_btn.setToolTip("Copiar tradução para a área de transferência")
        self.copy_btn.clicked.connect(self._copy_result)
        footer_layout.addWidget(self.copy_btn)

        # Botão Principal Traduzir & Enviar
        self.send_btn = QPushButton("Traduzir & Enviar ➔", self.central_widget)
        self.send_btn.setObjectName("PrimaryButton")
        self.send_btn.setToolTip("Traduz, volta ao Telegram/App e envia (Enter)")
        self.send_btn.clicked.connect(self.send_translation)
        footer_layout.addWidget(self.send_btn)

        central_layout.addLayout(footer_layout)
        main_layout.addWidget(self.central_widget)

    def _set_combo_value(self, combo: QComboBox, code: str):
        index = combo.findData(code)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _on_language_changed(self):
        source_code = self.source_combo.currentData()
        target_code = self.target_combo.currentData()

        config.set("source_lang", source_code)
        config.set("target_lang", target_code)

        self._start_translation()

    def _swap_languages(self):
        source_code = self.source_combo.currentData()
        target_code = self.target_combo.currentData()

        # Se origem era 'auto', usa a língua detectada ou inverte
        if source_code == "auto":
            new_target = self.last_detected_lang if self.last_detected_lang in SUPPORTED_LANGUAGES else "pt"
            new_source = target_code
        else:
            new_source = target_code
            new_target = source_code

        self._set_combo_value(self.source_combo, new_source)
        self._set_combo_value(self.target_combo, new_target)
        self._start_translation()

    def _on_auto_send_changed(self, state):
        config.set("auto_send", bool(state))

    def _on_text_changed(self):
        text = self.input_text.toPlainText().strip()
        if not text:
            self.result_label.setText("")
            self.last_translated_text = ""
            self.status_label.setText("")
            self.detected_badge.hide()
            return

        self.status_label.setText("Traduzindo...")
        self.debounce_timer.start()

    def _start_translation(self):
        text = self.input_text.toPlainText().strip()
        if not text:
            return

        source = self.source_combo.currentData()
        target = self.target_combo.currentData()

        if self.translation_worker and self.translation_worker.isRunning():
            self.translation_worker.terminate()

        self.translation_worker = TranslationWorker(text, source, target)
        self.translation_worker.finished.connect(self._on_translation_finished)
        self.translation_worker.error.connect(self._on_translation_error)
        self.translation_worker.start()

    def _on_translation_finished(self, original: str, translated: str, detected_lang: str):
        current_text = self.input_text.toPlainText().strip()
        if original != current_text:
            return

        self.last_translated_text = translated
        self.last_detected_lang = detected_lang
        self.result_label.setText(translated if translated else "(Sem tradução)")
        self.status_label.setText("Pronto")

        if self.source_combo.currentData() == "auto" and detected_lang:
            lang_name = SUPPORTED_LANGUAGES.get(detected_lang, detected_lang.upper())
            self.detected_badge.setText(f"Detectado: {lang_name}")
            self.detected_badge.show()
        else:
            self.detected_badge.hide()

    def _on_translation_error(self, original: str, error_msg: str):
        self.status_label.setText("Erro de conexão")
        self.result_label.setText("Não foi possível traduzir no momento.")

    def _copy_result(self):
        text = self.last_translated_text or self.input_text.toPlainText().strip()
        if text:
            TextInjector.set_clipboard_text(text)
            self.status_label.setText("Copiado!")

    def show_overlay(self, hwnd_target: int = 0):
        self.target_hwnd = hwnd_target
        self.input_text.clear()
        self.result_label.setText("")
        self.last_translated_text = ""
        self.status_label.setText("")
        self.detected_badge.hide()

        # Centraliza na tela ativa
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 3  # Fica levemente acima do centro, estilo Spotlight
        self.move(x, y)

        self.show()
        self.raise_()
        self.activateWindow()
        self.input_text.setFocus()

    def hide_overlay(self):
        self.hide()

    def send_translation(self):
        text = self.input_text.toPlainText().strip()
        if not text:
            self.hide_overlay()
            return

        # Garante tradução se ainda não estiver concluída
        if not self.last_translated_text:
            source = self.source_combo.currentData()
            target = self.target_combo.currentData()
            try:
                translated, _ = TranslationWorker.translate_now = (
                    __import__('src.core.translator', fromlist=['TranslatorService'])
                    .TranslatorService.translate(text, source, target)
                )
                final_text = translated
            except Exception:
                final_text = text
        else:
            final_text = self.last_translated_text

        auto_send = self.auto_send_check.isChecked()
        delay_ms = config.get("paste_delay_ms", 100)
        target_hwnd = self.target_hwnd

        # Esconde a janela flutuante
        self.hide_overlay()

        # Injeta o texto e envia
        TextInjector.restore_and_paste(
            hwnd_target=target_hwnd,
            text=final_text,
            auto_send=auto_send,
            delay_ms=delay_ms
        )

    # Permitir arrastar a janela clicando no cabeçalho
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.is_dragging = True
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.is_dragging = False

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #161922;
                color: #e2e8f0;
                border: 1px solid #2b3040;
                border-radius: 8px;
                padding: 4px;
                font-size: 13px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
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

        cfg_act = menu.addAction("⚙️ Configurações...")
        cfg_act.triggered.connect(self.open_settings_requested.emit)

        hide_act = menu.addAction("👁️ Ocultar Barra (Esc)")
        hide_act.triggered.connect(self.hide_overlay)

        menu.addSeparator()

        quit_act = menu.addAction("❌ Encerrar InputTranslator")
        quit_act.triggered.connect(self.quit_requested.emit)

        menu.exec(event.globalPos())
