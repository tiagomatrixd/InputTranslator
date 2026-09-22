THEME_STYLESHEET = """
/* Janela Principal e Containers */
QWidget#CentralWidget {
    background-color: #13161f;
    border: 1px solid #2a2f42;
    border-radius: 14px;
}

QFrame#HeaderBar {
    background-color: transparent;
    border: none;
    padding-bottom: 4px;
}

QFrame#ResultCard {
    background-color: #1a1e2b;
    border: 1px solid #282f45;
    border-radius: 10px;
    padding: 8px 12px;
}

/* Comboboxes de Idioma */
QComboBox {
    background-color: #1c202c;
    color: #e2e8f0;
    border: 1px solid #2e354a;
    border-radius: 8px;
    padding: 5px 12px 5px 10px;
    font-size: 13px;
    font-weight: 500;
}

QComboBox:hover {
    border-color: #3b82f6;
    background-color: #222838;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #94a3b8;
    margin-right: 6px;
}

QComboBox QAbstractItemView {
    background-color: #171a24;
    color: #e2e8f0;
    border: 1px solid #2d3447;
    border-radius: 8px;
    selection-background-color: #2b3652;
    selection-color: #ffffff;
    padding: 4px;
    outline: none;
}

/* Botões */
QPushButton {
    background-color: #202534;
    color: #cbd5e1;
    border: 1px solid #2d3448;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 13px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #293043;
    color: #f8fafc;
    border-color: #3d4763;
}

QPushButton:pressed {
    background-color: #1c202d;
}

QPushButton#SwapButton {
    background-color: #1c202c;
    border: 1px solid #2e354a;
    border-radius: 8px;
    padding: 5px 8px;
    font-size: 15px;
    font-weight: bold;
    color: #94a3b8;
}

QPushButton#SwapButton:hover {
    color: #60a5fa;
    border-color: #3b82f6;
    background-color: #23293a;
}

QPushButton#PrimaryButton {
    background-color: #3b82f6;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 7px 16px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton#PrimaryButton:hover {
    background-color: #2563eb;
}

QPushButton#PrimaryButton:pressed {
    background-color: #1d4ed8;
}

QPushButton#GhostButton {
    background-color: transparent;
    border: none;
    color: #94a3b8;
    padding: 4px 8px;
    font-size: 13px;
}

QPushButton#GhostButton:hover {
    color: #f1f5f9;
}

/* Campo de Entrada de Texto */
QTextEdit#InputText {
    background-color: #1a1d27;
    color: #f8fafc;
    border: 1px solid #2e354a;
    border-radius: 10px;
    padding: 10px 12px;
    font-size: 14px;
    line-height: 1.4;
    selection-background-color: #3b82f6;
}

QTextEdit#InputText:focus {
    border: 1px solid #3b82f6;
}

/* Área de Resultado */
QLabel#ResultLabel {
    color: #93c5fd;
    font-size: 14px;
    line-height: 1.4;
    font-weight: 500;
    selection-background-color: #2563eb;
}

QLabel#StatusLabel {
    color: #64748b;
    font-size: 11px;
}

QLabel#DetectedBadge {
    color: #38bdf8;
    background-color: #0c4a6e;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 11px;
    font-weight: 600;
}

/* Checkbox */
QCheckBox {
    color: #94a3b8;
    font-size: 12px;
    spacing: 6px;
}

QCheckBox:hover {
    color: #cbd5e1;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #333c52;
    background-color: #181b24;
}

QCheckBox::indicator:checked {
    background-color: #3b82f6;
    border-color: #3b82f6;
}
"""
