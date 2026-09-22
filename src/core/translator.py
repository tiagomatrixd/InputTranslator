import urllib.request
import urllib.parse
import json
import time
from PyQt6.QtCore import QObject, pyqtSignal, QThread

class TranslationWorker(QThread):
    finished = pyqtSignal(str, str, str)  # original, translated, detected_lang
    error = pyqtSignal(str, str)         # original, error_msg

    def __init__(self, text: str, source_lang: str, target_lang: str):
        super().__init__()
        self.text = text
        self.source_lang = source_lang
        self.target_lang = target_lang

    def run(self):
        text = self.text.strip()
        if not text:
            self.finished.emit("", "", "")
            return

        try:
            translated, detected = TranslatorService.translate(
                text, self.source_lang, self.target_lang
            )
            self.finished.emit(text, translated, detected)
        except Exception as e:
            self.error.emit(text, str(e))


class TranslatorService:
    _cache = {}

    @classmethod
    def translate(cls, text: str, source_lang: str = "auto", target_lang: str = "en") -> tuple[str, str]:
        text = text.strip()
        if not text:
            return "", ""

        cache_key = (text, source_lang, target_lang)
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        encoded_text = urllib.parse.quote(text)
        url = (
            f"https://translate.googleapis.com/translate_a/single?"
            f"client=gtx&sl={source_lang}&tl={target_lang}&dt=t&q={encoded_text}"
        )

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                content = response.read().decode("utf-8")
                data = json.loads(content)

                translated_parts = []
                if data and len(data) > 0 and data[0]:
                    for segment in data[0]:
                        if segment and segment[0]:
                            translated_parts.append(segment[0])

                translated_text = "".join(translated_parts)
                detected_lang = data[2] if len(data) > 2 and data[2] else source_lang

                result = (translated_text, str(detected_lang))
                cls._cache[cache_key] = result
                return result
        except Exception as e:
            # Fallback attempts or re-raise
            raise RuntimeError(f"Falha na tradução: {str(e)}")
