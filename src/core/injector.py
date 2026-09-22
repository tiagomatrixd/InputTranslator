import time
import win32gui
import win32con
import win32api
import win32process
from PyQt6.QtWidgets import QApplication

class TextInjector:
    @staticmethod
    def get_foreground_window():
        """Retorna o identificador HWND da janela atualmente em primeiro plano."""
        try:
            return win32gui.GetForegroundWindow()
        except Exception:
            return None

    @staticmethod
    def set_clipboard_text(text: str):
        """Define o texto na área de transferência do Windows de forma segura."""
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(text)

    @staticmethod
    def restore_and_paste(hwnd_target, text: str, auto_send: bool = True, delay_ms: int = 100):
        """
        Restaura o foco para a janela alvo (ex: Telegram) e envia o texto traduzido.
        1. Copia o texto para a área de transferência.
        2. Restaura o foco na janela anterior usando AttachThreadInput para garantir permissão.
        3. Simula Ctrl + V.
        4. Opcionalmente simula Enter se auto_send for True.
        """
        if not text:
            return

        # 1. Copia para o clipboard
        TextInjector.set_clipboard_text(text)

        if not hwnd_target:
            return

        try:
            # 2. Restaura o foco na janela alvo
            current_thread = win32api.GetCurrentThreadId()
            target_thread, _ = win32process.GetWindowThreadProcessId(hwnd_target)

            if current_thread != target_thread and target_thread != 0:
                win32process.AttachThreadInput(current_thread, target_thread, True)

            win32gui.ShowWindow(hwnd_target, win32con.SW_SHOW)
            win32gui.SetForegroundWindow(hwnd_target)

            if current_thread != target_thread and target_thread != 0:
                win32process.AttachThreadInput(current_thread, target_thread, False)

            # Aguarda a janela alvo receber e processar o foco
            time.sleep(max(delay_ms, 60) / 1000.0)

            # Garante que teclas modificadoras anteriores (como Alt) estejam totalmente liberadas
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.01)

            # 3. Simula Ctrl + V
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            win32api.keybd_event(ord('V'), 0, 0, 0)
            time.sleep(0.02)
            win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)

            # 4. Se auto_send ativado, aguarda e simula Enter
            if auto_send:
                time.sleep(0.06)
                win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
                time.sleep(0.02)
                win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)

        except Exception as e:
            print(f"Erro ao injetar texto na janela alvo: {e}")
