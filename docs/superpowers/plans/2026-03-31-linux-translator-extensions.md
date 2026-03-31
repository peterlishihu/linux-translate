# Linux 翻译助手 - 扩展功能实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 Linux 翻译助手添加扩展功能：悬浮窗、有道翻译、离线 TTS、全局快捷键、OCR 引擎、翻译结果弹窗、历史记录对话框和设置对话框。

**Architecture:** 延续现有架构，新增 GUI 组件（悬浮窗、弹窗、对话框），扩展翻译/TTS/OCR 引擎，添加全局快捷键服务。保持模块化设计，各功能可独立配置和启用。

**Tech Stack:** Python 3.10+, PyQt6, pytesseract, pynput, pyttsx3, Pillow

---

## Task 1: 有道翻译实现

**Files:**
- Create: `src/core/translation/youdao.py`
- Create: `tests/test_translation_youdao.py`
- Modify: `src/core/translation/__init__.py`

- [ ] **Step 1: 编写测试**

```python
# tests/test_translation_youdao.py
import pytest
from unittest.mock import patch, MagicMock
from src.core.translation.youdao import YoudaoTranslator


class TestYoudaoTranslator:
    def test_is_available_with_config(self):
        translator = YoudaoTranslator(appkey="test", appsecret="test")
        assert translator.is_available() is True

    def test_is_available_without_config(self):
        translator = YoudaoTranslator()
        assert translator.is_available() is False

    def test_translate_mock(self):
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "errorCode": "0",
                "query": "hello",
                "translation": ["你好"],
                "basic": {"phonetic": "həˈləʊ"}
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            translator = YoudaoTranslator(appkey="test", appsecret="test")
            result = translator.translate("hello", "en", "zh")
            assert result.text == "你好"
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd /home/peter/project/linux-translate
python -m pytest tests/test_translation_youdao.py -v
```

- [ ] **Step 3: 实现有道翻译**

```python
# src/core/translation/youdao.py
import requests
import hashlib
import uuid
import time
from .base import TranslationEngine, TranslationResult


class YoudaoTranslator(TranslationEngine):
    BASE_URL = "https://openapi.youdao.com/api"

    def __init__(self, appkey: str = None, appsecret: str = None, timeout: int = 10):
        self.appkey = appkey
        self.appsecret = appsecret
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "youdao"

    def is_available(self) -> bool:
        return bool(self.appkey and self.appsecret)

    def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        if not self.is_available():
            raise TranslationError("Youdao translator not configured")

        salt = uuid.uuid4().hex
        curtime = str(int(time.time()))
        sign_str = self.appkey + self._truncate(text) + salt + curtime + self.appsecret
        sign = hashlib.sha256(sign_str.encode()).hexdigest()

        # Language code mapping
        lang_map = {'zh': 'zh-CHS', 'en': 'en', 'auto': 'auto'}
        from_lang = lang_map.get(source_lang, source_lang)
        to_lang = lang_map.get(target_lang, target_lang)

        payload = {
            'q': text,
            'from': from_lang,
            'to': to_lang,
            'appKey': self.appkey,
            'salt': salt,
            'sign': sign,
            'signType': 'v3',
            'curtime': curtime
        }

        try:
            response = requests.post(self.BASE_URL, data=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            if data.get('errorCode') != '0':
                raise TranslationError(f"Youdao API error: {data.get('errorCode')}")

            translated = ' '.join(data.get('translation', []))
            return TranslationResult(
                text=translated,
                source_lang=from_lang,
                target_lang=to_lang,
                original_text=text,
                pronunciation=data.get('basic', {}).get('phonetic')
            )
        except Exception as e:
            raise TranslationError(f"Youdao translate failed: {e}")

    def _truncate(self, text: str) -> str:
        """Truncate text for sign generation (youdao requirement)"""
        if len(text) <= 20:
            return text
        return text[:10] + str(len(text)) + text[-10:]


class TranslationError(Exception):
    pass
```

- [ ] **Step 4: 更新 __init__.py**

```python
# src/core/translation/__init__.py
from .base import TranslationEngine, TranslationResult
from .google import GoogleTranslator
from .baidu import BaiduTranslator
from .youdao import YoudaoTranslator

__all__ = ['TranslationEngine', 'TranslationResult', 'GoogleTranslator', 'BaiduTranslator', 'YoudaoTranslator']
```

- [ ] **Step 5: 运行测试确认通过**

```bash
python -m pytest tests/test_translation_youdao.py -v
```

- [ ] **Step 6: 提交**

```bash
git add src/core/translation/youdao.py tests/test_translation_youdao.py
git commit -m "feat: add Youdao translator"
```

---

## Task 2: 离线 TTS 实现

**Files:**
- Create: `src/core/tts/offline.py`
- Create: `tests/test_tts_offline.py`
- Modify: `src/core/tts/__init__.py`

- [ ] **Step 1: 编写测试**

```python
# tests/test_tts_offline.py
import pytest
from unittest.mock import patch, MagicMock
from src.core.tts.offline import OfflineTTS


class TestOfflineTTS:
    def test_is_available_with_pyttsx3(self):
        with patch.dict('sys.modules', {'pyttsx3': MagicMock()}):
            tts = OfflineTTS()
            assert tts.is_available() is True

    def test_is_available_without_pyttsx3(self):
        with patch.dict('sys.modules', {'pyttsx3': None}):
            tts = OfflineTTS()
            assert tts.is_available() is False

    def test_name(self):
        tts = OfflineTTS()
        assert tts.name == "offline"
```

- [ ] **Step 2: 运行测试确认失败**

```bash
python -m pytest tests/test_tts_offline.py -v
```

- [ ] **Step 3: 实现离线 TTS**

```python
# src/core/tts/offline.py
import threading
from .base import TTSEngine, TTSError


class OfflineTTS(TTSEngine):
    def __init__(self, rate: int = 150):
        self.rate = rate
        self._engine = None

    @property
    def name(self) -> str:
        return "offline"

    def is_available(self) -> bool:
        try:
            import pyttsx3
            return True
        except ImportError:
            return False

    def _get_engine(self):
        if self._engine is None:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._engine.setProperty('rate', self.rate)
        return self._engine

    def play_text(self, text: str, lang: str = 'zh') -> bool:
        if not text or not text.strip():
            return False

        try:
            engine = self._get_engine()

            # Set voice based on language
            voices = engine.getProperty('voices')
            if lang == 'zh':
                # Try to find Chinese voice
                for voice in voices:
                    if 'chinese' in voice.name.lower() or 'mandarin' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
            else:
                # Default to English
                for voice in voices:
                    if 'english' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break

            engine.say(text)
            engine.runAndWait()
            return True

        except Exception as e:
            raise TTSError(f"Offline TTS failed: {e}")

    def stop(self):
        """Stop current speech"""
        if self._engine:
            try:
                self._engine.stop()
            except:
                pass
```

- [ ] **Step 4: 更新 TTS __init__.py**

```python
# src/core/tts/__init__.py
from .base import TTSEngine, TTSError
from .online import OnlineTTS
from .offline import OfflineTTS

__all__ = ['TTSEngine', 'TTSError', 'OnlineTTS', 'OfflineTTS']
```

- [ ] **Step 5: 运行测试确认通过**

```bash
python -m pytest tests/test_tts_offline.py -v
```

- [ ] **Step 6: 提交**

```bash
git add src/core/tts/offline.py tests/test_tts_offline.py
git commit -m "feat: add offline TTS using pyttsx3"
```

---

## Task 3: OCR 引擎基类与 Tesseract 实现

**Files:**
- Create: `src/core/ocr/__init__.py`
- Create: `src/core/ocr/base.py`
- Create: `src/core/ocr/tesseract.py`
- Create: `tests/test_ocr_tesseract.py`

- [ ] **Step 1: 编写测试**

```python
# tests/test_ocr_tesseract.py
import pytest
from unittest.mock import patch, MagicMock
from src.core.ocr.base import OCRResult
from src.core.ocr.tesseract import TesseractOCR


class TestOCRResult:
    def test_result_creation(self):
        result = OCRResult(text="hello", confidence=95.5)
        assert result.text == "hello"
        assert result.confidence == 95.5


class TestTesseractOCR:
    def test_is_available_with_tesseract(self):
        with patch('shutil.which', return_value='/usr/bin/tesseract'):
            ocr = TesseractOCR()
            assert ocr.is_available() is True

    def test_is_available_without_tesseract(self):
        with patch('shutil.which', return_value=None):
            ocr = TesseractOCR()
            assert ocr.is_available() is False

    def test_recognize_mock(self):
        with patch('pytesseract.image_to_string', return_value="hello world"), \
             patch('pytesseract.image_to_data', return_value={
                 'conf': [-1, 95, 90],
                 'text': ['', 'hello', 'world']
             }), \
             patch('PIL.Image.open') as mock_open:

            mock_image = MagicMock()
            mock_open.return_value = mock_image

            ocr = TesseractOCR()
            result = ocr.recognize("/path/to/image.png", lang='eng')
            assert result.text == "hello world"
```

- [ ] **Step 2: 运行测试确认失败**

```bash
python -m pytest tests/test_ocr_tesseract.py -v
```

- [ ] **Step 3: 实现 OCR 模块**

```python
# src/core/ocr/__init__.py
from .base import OCREngine, OCRResult
from .tesseract import TesseractOCR

__all__ = ['OCREngine', 'OCRResult', 'TesseractOCR']
```

```python
# src/core/ocr/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class OCRResult:
    text: str
    confidence: Optional[float] = None


class OCREngine(ABC):
    @abstractmethod
    def recognize(self, image_path: str, lang: str = 'eng') -> OCRResult:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass
```

```python
# src/core/ocr/tesseract.py
import shutil
import pytesseract
from PIL import Image
from .base import OCREngine, OCRResult


class TesseractOCR(OCREngine):
    def __init__(self):
        self._tesseract_cmd = None

    @property
    def name(self) -> str:
        return "tesseract"

    def is_available(self) -> bool:
        cmd = shutil.which('tesseract')
        if cmd:
            self._tesseract_cmd = cmd
            pytesseract.pytesseract.tesseract_cmd = cmd
            return True
        return False

    def recognize(self, image_path: str, lang: str = 'eng') -> OCRResult:
        if not self.is_available():
            raise OCRError("Tesseract is not available")

        try:
            # Map language codes
            lang_map = {'zh': 'chi_sim+chi_tra', 'en': 'eng', 'auto': 'chi_sim+eng'}
            tesseract_lang = lang_map.get(lang, lang)

            # Open image
            image = Image.open(image_path)

            # Perform OCR
            text = pytesseract.image_to_string(image, lang=tesseract_lang)

            # Get confidence data
            try:
                data = pytesseract.image_to_data(image, lang=tesseract_lang, output_type=pytesseract.Output.DICT)
                confidences = [int(c) for c in data['conf'] if int(c) > 0]
                avg_confidence = sum(confidences) / len(confidences) if confidences else None
            except:
                avg_confidence = None

            return OCRResult(text=text.strip(), confidence=avg_confidence)

        except Exception as e:
            raise OCRError(f"OCR recognition failed: {e}")


class OCRError(Exception):
    pass
```

- [ ] **Step 4: 运行测试确认通过**

```bash
python -m pytest tests/test_ocr_tesseract.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/core/ocr/ tests/test_ocr_tesseract.py
git commit -m "feat: add OCR engine base and Tesseract implementation"
```

---

## Task 4: 全局快捷键服务

**Files:**
- Create: `src/services/__init__.py`
- Create: `src/services/hotkey.py`
- Create: `tests/test_hotkey.py`

- [ ] **Step 1: 编写测试**

```python
# tests/test_hotkey.py
import pytest
from unittest.mock import patch, MagicMock
from src.services.hotkey import HotkeyManager


class TestHotkeyManager:
    def test_init(self):
        manager = HotkeyManager()
        assert manager.shortcuts == {}

    def test_register_shortcut(self):
        manager = HotkeyManager()
        callback = MagicMock()

        with patch.object(manager, '_start_listener'):
            manager.register('<ctrl>+<alt>+t', callback)
            assert '<ctrl>+<alt>+t' in manager.shortcuts

    def test_unregister_shortcut(self):
        manager = HotkeyManager()
        callback = MagicMock()

        with patch.object(manager, '_start_listener'):
            manager.register('<ctrl>+<alt>+t', callback)
            manager.unregister('<ctrl>+<alt>+t')
            assert '<ctrl>+<alt>+t' not in manager.shortcuts
```

- [ ] **Step 2: 运行测试确认失败**

```bash
python -m pytest tests/test_hotkey.py -v
```

- [ ] **Step 3: 实现快捷键服务**

```python
# src/services/__init__.py
from .hotkey import HotkeyManager

__all__ = ['HotkeyManager']
```

```python
# src/services/hotkey.py
import threading
from typing import Callable, Dict


class HotkeyManager:
    def __init__(self):
        self.shortcuts: Dict[str, Callable] = {}
        self._listener = None
        self._running = False

    def register(self, shortcut: str, callback: Callable):
        """Register a global hotkey

        Args:
            shortcut: Hotkey combination like '<ctrl>+<alt>+t'
            callback: Function to call when hotkey is pressed
        """
        self.shortcuts[shortcut] = callback
        if not self._running:
            self._start_listener()

    def unregister(self, shortcut: str):
        """Unregister a hotkey"""
        if shortcut in self.shortcuts:
            del self.shortcuts[shortcut]

    def stop(self):
        """Stop the hotkey listener"""
        self._running = False
        if self._listener:
            self._listener.stop()

    def _start_listener(self):
        """Start the global hotkey listener"""
        try:
            from pynput import keyboard

            def on_activate(shortcut):
                callback = self.shortcuts.get(shortcut)
                if callback:
                    callback()

            # Create hotkey combinations
            hotkeys = {}
            for shortcut, callback in self.shortcuts.items():
                hotkeys[shortcut] = lambda s=shortcut: on_activate(s)

            self._listener = keyboard.GlobalHotKeys(hotkeys)
            self._listener.start()
            self._running = True

        except ImportError:
            print("Warning: pynput not available, hotkeys disabled")
        except Exception as e:
            print(f"Warning: Failed to start hotkey listener: {e}")

    def is_available(self) -> bool:
        """Check if hotkey support is available"""
        try:
            from pynput import keyboard
            return True
        except ImportError:
            return False
```

- [ ] **Step 4: 运行测试确认通过**

```bash
python -m pytest tests/test_hotkey.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/services/ tests/test_hotkey.py
git commit -m "feat: add global hotkey service using pynput"
```

---

## Task 5: 悬浮窗

**Files:**
- Create: `src/gui/float_window.py`
- Modify: `src/gui/__init__.py`

- [ ] **Step 1: 实现悬浮窗**

```python
# src/gui/float_window.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QApplication
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QFont, QIcon


class FloatWindow(QWidget):
    """Floating translation input window"""

    translate_requested = pyqtSignal(str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("翻译")
        self.setMinimumSize(300, 150)
        self.setMaximumSize(400, 200)

        # Frameless window that stays on top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        # Enable mouse tracking for dragging
        self.setMouseTracking(True)
        self._drag_pos = None

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Title bar with drag handle
        title_layout = QHBoxLayout()
        self.title_label = QLabel("翻译")
        self.title_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        # Close button
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #ff4444;
                color: white;
                border-radius: 3px;
            }
        """)
        self.close_btn.clicked.connect(self.hide)
        title_layout.addWidget(self.close_btn)

        layout.addLayout(title_layout)

        # Input area
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("输入文本翻译...")
        self.input_text.setMaximumHeight(80)
        self.input_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.input_text)

        # Buttons
        btn_layout = QHBoxLayout()

        self.translate_btn = QPushButton("翻译")
        self.translate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.translate_btn.clicked.connect(self._on_translate)
        btn_layout.addWidget(self.translate_btn)

        btn_layout.addStretch()

        # Pin button
        self.pin_btn = QPushButton("📌")
        self.pin_btn.setFixedSize(25, 25)
        self.pin_btn.setCheckable(True)
        self.pin_btn.setChecked(True)
        self.pin_btn.setToolTip("保持置顶")
        btn_layout.addWidget(self.pin_btn)

        layout.addLayout(btn_layout)

        # Styling
        self.setStyleSheet("""
            FloatWindow {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 8px;
            }
        """)

    def _on_translate(self):
        text = self.input_text.toPlainText().strip()
        if text:
            self.translate_requested.emit(text, 'auto', 'zh')

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def show_at(self, pos: QPoint):
        """Show window at specific position"""
        self.move(pos)
        self.show()
        self.raise_()
        self.activateWindow()

    def clear(self):
        """Clear input text"""
        self.input_text.clear()
```

- [ ] **Step 2: 更新 gui __init__.py**

```python
# src/gui/__init__.py
from .main_window import MainWindow
from .float_window import FloatWindow

__all__ = ['MainWindow', 'FloatWindow']
```

- [ ] **Step 3: 提交**

```bash
git add src/gui/float_window.py src/gui/__init__.py
git commit -m "feat: add floating translation window"
```

---

## Task 6: 翻译结果弹窗

**Files:**
- Create: `src/gui/result_popup.py`
- Modify: `src/gui/__init__.py`

- [ ] **Step 1: 实现翻译结果弹窗**

```python
# src/gui/result_popup.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QApplication
)
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt6.QtGui import QFont


class ResultPopup(QWidget):
    """Popup window to display translation results near mouse"""

    copy_requested = pyqtSignal(str)
    speak_requested = pyqtSignal(str, str)  # text, lang

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("翻译结果")

        # Frameless, stay on top, popup
        self.setWindowFlags(
            Qt.WindowType.Popup |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Auto-close timer
        self._close_timer = QTimer(self)
        self._close_timer.timeout.connect(self.hide)
        self._auto_close_delay = 10000  # 10 seconds

        self._setup_ui()

    def _setup_ui(self):
        # Main container with styling
        self.container = QWidget(self)
        self.container.setObjectName("container")
        self.container.setStyleSheet("""
            QWidget#container {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.container)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(15, 10, 15, 10)
        container_layout.setSpacing(8)

        # Header with source text
        header_layout = QHBoxLayout()
        self.source_label = QLabel("原文")
        self.source_label.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))
        header_layout.addWidget(self.source_label)
        header_layout.addStretch()

        # Close button
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #999;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                color: #333;
            }
        """)
        self.close_btn.clicked.connect(self.hide)
        header_layout.addWidget(self.close_btn)

        container_layout.addLayout(header_layout)

        # Source text (truncated)
        self.source_text = QLabel()
        self.source_text.setWordWrap(True)
        self.source_text.setMaximumWidth(350)
        self.source_text.setStyleSheet("color: #666; font-size: 12px;")
        container_layout.addWidget(self.source_text)

        # Separator
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #eee;")
        container_layout.addWidget(separator)

        # Translation result
        self.result_label = QLabel("翻译")
        self.result_label.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))
        container_layout.addWidget(self.result_label)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(100)
        self.result_text.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: #f9f9f9;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        container_layout.addWidget(self.result_text)

        # Action buttons
        btn_layout = QHBoxLayout()

        self.copy_btn = QPushButton("复制")
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 4px 12px;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.copy_btn.clicked.connect(self._on_copy)
        btn_layout.addWidget(self.copy_btn)

        self.speak_btn = QPushButton("朗读")
        self.speak_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 4px 12px;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        self.speak_btn.clicked.connect(self._on_speak)
        btn_layout.addWidget(self.speak_btn)

        btn_layout.addStretch()

        # Pin button to disable auto-close
        self.pin_btn = QPushButton("📌")
        self.pin_btn.setCheckable(True)
        self.pin_btn.setFixedSize(25, 25)
        self.pin_btn.setToolTip("保持显示")
        self.pin_btn.toggled.connect(self._on_pin_toggled)
        btn_layout.addWidget(self.pin_btn)

        container_layout.addLayout(btn_layout)

        self.setMaximumWidth(400)

    def show_result(self, source: str, result: str, pos: QPoint = None, lang: str = 'zh'):
        """Show translation result at specified position"""
        # Truncate source if too long
        display_source = source[:100] + "..." if len(source) > 100 else source
        self.source_text.setText(display_source)
        self.result_text.setPlainText(result)
        self._current_lang = lang

        # Position near mouse if not specified
        if pos is None:
            from PyQt6.QtGui import QCursor
            pos = QCursor.pos()

        # Adjust position to keep on screen
        screen = QApplication.primaryScreen().geometry()
        x = min(pos.x(), screen.width() - 400)
        y = min(pos.y() + 20, screen.height() - 200)

        self.move(x, y)
        self.show()

        # Start auto-close timer
        if not self.pin_btn.isChecked():
            self._close_timer.start(self._auto_close_delay)

    def _on_copy(self):
        text = self.result_text.toPlainText()
        if text:
            self.copy_requested.emit(text)
            # Visual feedback
            self.copy_btn.setText("已复制")
            QTimer.singleShot(1000, lambda: self.copy_btn.setText("复制"))

    def _on_speak(self):
        text = self.result_text.toPlainText()
        if text:
            self.speak_requested.emit(text, getattr(self, '_current_lang', 'zh'))

    def _on_pin_toggled(self, checked):
        if checked:
            self._close_timer.stop()
            self.pin_btn.setToolTip("点击取消固定")
        else:
            self._close_timer.start(self._auto_close_delay)
            self.pin_btn.setToolTip("保持显示")

    def hideEvent(self, event):
        self._close_timer.stop()
        super().hideEvent(event)

    def enterEvent(self, event):
        """Pause auto-close when mouse enters"""
        if not self.pin_btn.isChecked():
            self._close_timer.stop()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Resume auto-close when mouse leaves"""
        if not self.pin_btn.isChecked() and self.isVisible():
            self._close_timer.start(self._auto_close_delay)
        super().leaveEvent(event)
```

- [ ] **Step 2: 更新 gui __init__.py**

```python
# src/gui/__init__.py
from .main_window import MainWindow
from .float_window import FloatWindow
from .result_popup import ResultPopup

__all__ = ['MainWindow', 'FloatWindow', 'ResultPopup']
```

- [ ] **Step 3: 提交**

```bash
git add src/gui/result_popup.py src/gui/__init__.py
git commit -m "feat: add translation result popup window"
```

---

## Task 7: 历史记录对话框

**Files:**
- Create: `src/gui/history_dialog.py`
- Modify: `src/gui/__init__.py`

- [ ] **Step 1: 实现历史记录对话框**

```python
# src/gui/history_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLineEdit, QLabel,
    QMessageBox, QFileDialog, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime

from src.db.history import HistoryManager, TranslationRecord


class HistoryDialog(QDialog):
    """Dialog for viewing and managing translation history"""

    record_selected = pyqtSignal(str)  # Emits source text when record selected

    def __init__(self, history_manager: HistoryManager, parent=None):
        super().__init__(parent)
        self.history = history_manager
        self.setWindowTitle("历史记录")
        self.setMinimumSize(700, 500)
        self._setup_ui()
        self._load_history()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索:"))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词搜索...")
        self.search_input.returnPressed.connect(self._on_search)
        search_layout.addWidget(self.search_input)

        self.search_btn = QPushButton("搜索")
        self.search_btn.clicked.connect(self._on_search)
        search_layout.addWidget(self.search_btn)

        self.clear_search_btn = QPushButton("清除")
        self.clear_search_btn.clicked.connect(self._on_clear_search)
        search_layout.addWidget(self.clear_search_btn)

        layout.addLayout(search_layout)

        # History table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["时间", "原文", "译文", "语言", "API"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.doubleClicked.connect(self._on_record_selected)

        # Column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.table)

        # Action buttons
        btn_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self._load_history)
        btn_layout.addWidget(self.refresh_btn)

        btn_layout.addStretch()

        self.export_btn = QPushButton("导出 CSV")
        self.export_btn.clicked.connect(self._on_export)
        btn_layout.addWidget(self.export_btn)

        self.delete_btn = QPushButton("删除")
        self.delete_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.delete_btn.clicked.connect(self._on_delete)
        btn_layout.addWidget(self.delete_btn)

        self.clear_all_btn = QPushButton("清空全部")
        self.clear_all_btn.setStyleSheet("background-color: #d32f2f; color: white;")
        self.clear_all_btn.clicked.connect(self._on_clear_all)
        btn_layout.addWidget(self.clear_all_btn)

        layout.addLayout(btn_layout)

        # Status label
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

    def _load_history(self):
        """Load all history records"""
        records = self.history.get_records(limit=1000)
        self._populate_table(records)
        self.status_label.setText(f"共 {len(records)} 条记录")

    def _populate_table(self, records: list):
        """Populate table with records"""
        self.table.setRowCount(len(records))

        for row, record in enumerate(records):
            # Time
            time_str = record.timestamp.strftime("%Y-%m-%d %H:%M") if record.timestamp else ""
            self.table.setItem(row, 0, QTableWidgetItem(time_str))

            # Source text (truncated)
            source = record.source_text[:50] + "..." if len(record.source_text) > 50 else record.source_text
            self.table.setItem(row, 1, QTableWidgetItem(source))

            # Translated text (truncated)
            translated = record.translated_text[:50] + "..." if len(record.translated_text) > 50 else record.translated_text
            self.table.setItem(row, 2, QTableWidgetItem(translated))

            # Languages
            lang_str = f"{record.source_lang} → {record.target_lang}"
            self.table.setItem(row, 3, QTableWidgetItem(lang_str))

            # API used
            self.table.setItem(row, 4, QTableWidgetItem(record.api_used or ""))

            # Store full record in first column's data
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, record)

    def _on_search(self):
        """Search history"""
        keyword = self.search_input.text().strip()
        if keyword:
            records = self.history.search_records(keyword)
            self._populate_table(records)
            self.status_label.setText(f"搜索 '{keyword}': {len(records)} 条结果")
        else:
            self._load_history()

    def _on_clear_search(self):
        """Clear search and reload all"""
        self.search_input.clear()
        self._load_history()

    def _on_record_selected(self):
        """Handle record selection (double-click)"""
        row = self.table.currentRow()
        if row >= 0:
            item = self.table.item(row, 0)
            record = item.data(Qt.ItemDataRole.UserRole)
            if record:
                self.record_selected.emit(record.source_text)

    def _on_delete(self):
        """Delete selected record"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择要删除的记录")
            return

        item = self.table.item(row, 0)
        record = item.data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除这条记录吗?\n原文: {record.source_text[:30]}...",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.history.delete_record(record.id)
            self._load_history()

    def _on_clear_all(self):
        """Clear all history"""
        reply = QMessageBox.warning(
            self, "确认清空",
            "确定要清空所有历史记录吗?\n此操作不可恢复!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.history.clear_all()
            self._load_history()

    def _on_export(self):
        """Export history to CSV"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "导出历史记录", "translation_history.csv",
            "CSV Files (*.csv)"
        )

        if filepath:
            try:
                self.history.export_to_csv(filepath)
                QMessageBox.information(self, "成功", f"历史记录已导出到:\n{filepath}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {e}")
```

- [ ] **Step 2: 更新 gui __init__.py**

```python
# src/gui/__init__.py
from .main_window import MainWindow
from .float_window import FloatWindow
from .result_popup import ResultPopup
from .history_dialog import HistoryDialog

__all__ = ['MainWindow', 'FloatWindow', 'ResultPopup', 'HistoryDialog']
```

- [ ] **Step 3: 提交**

```bash
git add src/gui/history_dialog.py src/gui/__init__.py
git commit -m "feat: add history dialog for managing translation history"
```

---

## Task 8: 设置对话框

**Files:**
- Create: `src/gui/settings_dialog.py`
- Modify: `src/gui/__init__.py`

- [ ] **Step 1: 实现设置对话框**

```python
# src/gui/settings_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QLabel, QLineEdit, QPushButton,
    QComboBox, QSpinBox, QCheckBox, QMessageBox,
    QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt

from src.config import Config, ConfigManager


class SettingsDialog(QDialog):
    """Dialog for application settings"""

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.config = config_manager.load()
        self.setWindowTitle("设置")
        self.setMinimumSize(500, 400)
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # API Settings tab
        self.api_tab = self._create_api_tab()
        self.tabs.addTab(self.api_tab, "API 设置")

        # Hotkey Settings tab
        self.hotkey_tab = self._create_hotkey_tab()
        self.tabs.addTab(self.hotkey_tab, "快捷键")

        # UI Settings tab
        self.ui_tab = self._create_ui_tab()
        self.tabs.addTab(self.ui_tab, "界面")

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.save_btn = QPushButton("保存")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 6px 20px;
                border-radius: 4px;
            }
        """)
        self.save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

    def _create_api_tab(self) -> QWidget:
        """Create API settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Translation API priority
        priority_group = QGroupBox("翻译引擎优先级")
        priority_layout = QFormLayout(priority_group)

        self.trans_priority = QLineEdit()
        self.trans_priority.setPlaceholderText("google,baidu,youdao,argos")
        priority_layout.addRow("优先级 (逗号分隔):", self.trans_priority)

        layout.addWidget(priority_group)

        # Baidu API
        baidu_group = QGroupBox("百度翻译 API")
        baidu_layout = QFormLayout(baidu_group)

        self.baidu_appid = QLineEdit()
        self.baidu_appid.setPlaceholderText("输入百度翻译 App ID")
        baidu_layout.addRow("App ID:", self.baidu_appid)

        self.baidu_key = QLineEdit()
        self.baidu_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.baidu_key.setPlaceholderText("输入百度翻译密钥")
        baidu_layout.addRow("密钥:", self.baidu_key)

        layout.addWidget(baidu_group)

        # Youdao API
        youdao_group = QGroupBox("有道翻译 API")
        youdao_layout = QFormLayout(youdao_group)

        self.youdao_appkey = QLineEdit()
        self.youdao_appkey.setPlaceholderText("输入有道翻译 App Key")
        youdao_layout.addRow("App Key:", self.youdao_appkey)

        self.youdao_secret = QLineEdit()
        self.youdao_secret.setEchoMode(QLineEdit.EchoMode.Password)
        self.youdao_secret.setPlaceholderText("输入有道翻译密钥")
        youdao_layout.addRow("密钥:", self.youdao_secret)

        layout.addWidget(youdao_group)
        layout.addStretch()

        return tab

    def _create_hotkey_tab(self) -> QWidget:
        """Create hotkey settings tab"""
        tab = QWidget()
        layout = QFormLayout(tab)

        self.hotkey_translate = QLineEdit()
        self.hotkey_translate.setPlaceholderText("<ctrl>+<alt>+t")
        layout.addRow("翻译选中文本:", self.hotkey_translate)

        self.hotkey_ocr = QLineEdit()
        self.hotkey_ocr.setPlaceholderText("<ctrl>+<alt>+o")
        layout.addRow("OCR 翻译:", self.hotkey_ocr)

        self.hotkey_float = QLineEdit()
        self.hotkey_float.setPlaceholderText("<ctrl>+<alt>+f")
        layout.addRow("显示悬浮窗:", self.hotkey_float)

        layout.addRow("", QLabel("格式: <ctrl>+<alt>+字母"))

        return tab

    def _create_ui_tab(self) -> QWidget:
        """Create UI settings tab"""
        tab = QWidget()
        layout = QFormLayout(tab)

        self.follow_mouse = QCheckBox("翻译结果弹窗跟随鼠标")
        layout.addRow(self.follow_mouse)

        self.float_visible = QCheckBox("启动时显示悬浮窗")
        layout.addRow(self.float_visible)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["系统默认", "浅色", "深色"])
        layout.addRow("主题:", self.theme_combo)

        self.tts_speed = QSpinBox()
        self.tts_speed.setRange(50, 200)
        self.tts_speed.setSuffix("%")
        layout.addRow("语音速度:", self.tts_speed)

        return tab

    def _load_settings(self):
        """Load current settings into UI"""
        # Translation priority
        priority = self.config.translation.get('priority', [])
        self.trans_priority.setText(','.join(priority))

        # Baidu
        baidu_keys = self.config.translation.get('api_keys', {}).get('baidu', {})
        self.baidu_appid.setText(baidu_keys.get('appid', ''))
        self.baidu_key.setText(baidu_keys.get('key', ''))

        # Youdao
        youdao_keys = self.config.translation.get('api_keys', {}).get('youdao', {})
        self.youdao_appkey.setText(youdao_keys.get('appkey', ''))
        self.youdao_secret.setText(youdao_keys.get('appsecret', ''))

        # Hotkeys
        hotkeys = self.config.hotkeys
        self.hotkey_translate.setText(hotkeys.get('translate_selection', ''))
        self.hotkey_ocr.setText(hotkeys.get('ocr_translate', ''))
        self.hotkey_float.setText(hotkeys.get('show_float_window', ''))

        # UI
        ui = self.config.ui
        self.follow_mouse.setChecked(ui.get('follow_mouse', True))
        self.float_visible.setChecked(ui.get('float_window_visible', True))

        theme_map = {'system': 0, 'light': 1, 'dark': 2}
        self.theme_combo.setCurrentIndex(theme_map.get(ui.get('theme', 'system'), 0))

        tts = self.config.tts
        speed = int(tts.get('speed', 1.0) * 100)
        self.tts_speed.setValue(speed)

    def _on_save(self):
        """Save settings"""
        # Translation priority
        priority_str = self.trans_priority.text().strip()
        self.config.translation['priority'] = [p.strip() for p in priority_str.split(',') if p.strip()]

        # Baidu
        if 'api_keys' not in self.config.translation:
            self.config.translation['api_keys'] = {}
        self.config.translation['api_keys']['baidu'] = {
            'appid': self.baidu_appid.text().strip(),
            'key': self.baidu_key.text().strip()
        }

        # Youdao
        self.config.translation['api_keys']['youdao'] = {
            'appkey': self.youdao_appkey.text().strip(),
            'appsecret': self.youdao_secret.text().strip()
        }

        # Hotkeys
        self.config.hotkeys['translate_selection'] = self.hotkey_translate.text().strip()
        self.config.hotkeys['ocr_translate'] = self.hotkey_ocr.text().strip()
        self.config.hotkeys['show_float_window'] = self.hotkey_float.text().strip()

        # UI
        self.config.ui['follow_mouse'] = self.follow_mouse.isChecked()
        self.config.ui['float_window_visible'] = self.float_visible.isChecked()

        theme_map = {0: 'system', 1: 'light', 2: 'dark'}
        self.config.ui['theme'] = theme_map.get(self.theme_combo.currentIndex(), 'system')

        self.config.tts['speed'] = self.tts_speed.value() / 100.0

        # Save
        try:
            self.config_manager.save(self.config)
            QMessageBox.information(self, "成功", "设置已保存")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {e}")
```

- [ ] **Step 2: 更新 gui __init__.py**

```python
# src/gui/__init__.py
from .main_window import MainWindow
from .float_window import FloatWindow
from .result_popup import ResultPopup
from .history_dialog import HistoryDialog
from .settings_dialog import SettingsDialog

__all__ = ['MainWindow', 'FloatWindow', 'ResultPopup', 'HistoryDialog', 'SettingsDialog']
```

- [ ] **Step 3: 提交**

```bash
git add src/gui/settings_dialog.py src/gui/__init__.py
git commit -m "feat: add settings dialog for configuration"
```

---

## 自审查检查

**1. Spec 覆盖检查:**
- ✅ 有道翻译 (Task 1)
- ✅ 离线 TTS (Task 2)
- ✅ OCR 引擎 + Tesseract (Task 3)
- ✅ 全局快捷键 (Task 4)
- ✅ 悬浮窗 (Task 5)
- ✅ 翻译结果弹窗 (Task 6)
- ✅ 历史记录对话框 (Task 7)
- ✅ 设置对话框 (Task 8)

**2. 占位符扫描:**
- ✅ 无 TBD/TODO 占位符

**3. 类型一致性:**
- ✅ TranslationError 在多个翻译模块中保持一致
- ✅ TTSError 在 TTS 模块中保持一致
- ✅ OCRError 在 OCR 模块中定义

---

## 执行方式

**计划已完成并保存到 `docs/superpowers/plans/2026-03-31-linux-translator-extensions.md`**

两个执行选项：

**1. Subagent-Driven (推荐)** - 我为每个任务派遣新的子代理，任务间审查，快速迭代

**2. Inline Execution** - 在当前会话中使用 executing-plans 直接执行任务，批量执行并设置检查点

请选择执行方式（输入 1 或 2）：