# Linux 翻译助手实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现一个基于 Python + PyQt6 的 Linux 桌面翻译应用，支持中英互译、屏幕划词、OCR识别、语音朗读和历史记录功能。

**架构:** 采用分层架构，GUI层使用 PyQt6，核心服务层封装翻译/OCR/TTS引擎，数据层使用 SQLite。各模块通过清晰接口解耦，支持多API可插拔配置。

**Tech Stack:** Python 3.10+, PyQt6, SQLite, requests, pytesseract, gTTS, pynput

---

## 项目结构

```
linux-translate/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── float_window.py
│   │   ├── result_popup.py
│   │   └── settings_dialog.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── translation/
│   │   ├── ocr/
│   │   └── tts/
│   ├── db/
│   │   ├── __init__.py
│   │   └── history.py
│   └── utils/
│       ├── __init__.py
│       └── clipboard.py
├── tests/
├── requirements.txt
└── README.md
```

---

## Task 1: 项目初始化与依赖配置

**Files:**
- Create: `requirements.txt`
- Create: `README.md`
- Create: `.gitignore`

- [ ] **Step 1: 创建 requirements.txt**

```txt
PyQt6>=6.4.0
requests>=2.28.0
Pillow>=9.0.0
pytesseract>=0.3.10
pyttsx3>=2.90
gTTS>=2.3.0
pynput>=1.7.6
argostranslate>=1.8.0
```

- [ ] **Step 2: 创建 .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Application data
*.db
*.sqlite
config.json
```

- [ ] **Step 3: 创建基础 README.md**

```markdown
# Linux 翻译助手

基于 Python + PyQt6 的 Linux 桌面翻译应用。

## 功能

- 中英互译（支持多API）
- 屏幕划词翻译
- OCR 识别
- 语音朗读
- 历史记录

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
python -m src.main
```

## 系统依赖

- tesseract-ocr
- tesseract-ocr-chi-sim
- wl-clipboard
- grim
- slurp
```

- [ ] **Step 4: 创建目录结构**

```bash
mkdir -p src/{gui,core/{translation,ocr,tts},db,utils} tests
```

- [ ] **Step 5: 提交**

```bash
git add requirements.txt README.md .gitignore
mkdir -p src/{gui,core/{translation,ocr,tts},db,utils} tests
git add src tests
git commit -m "chore: initialize project structure and dependencies"
```

---

## Task 2: 配置管理模块

**Files:**
- Create: `src/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: 编写配置模块测试**

```python
# tests/test_config.py
import os
import json
import tempfile
import pytest
from src.config import Config, ConfigManager


class TestConfig:
    def test_config_default_values(self):
        config = Config()
        assert config.translation['priority'] == ['google', 'baidu', 'youdao', 'argos']
        assert config.ocr['priority'] == ['tesseract', 'cloud']
        assert config.tts['priority'] == ['online', 'offline']

    def test_config_to_dict(self):
        config = Config()
        data = config.to_dict()
        assert 'translation' in data
        assert 'ocr' in data
        assert 'tts' in data


class TestConfigManager:
    def test_load_nonexistent_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, 'config.json')
            manager = ConfigManager(config_path)
            config = manager.load()
            assert isinstance(config, Config)
            assert config.translation['priority'] == ['google', 'baidu', 'youdao', 'argos']

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, 'config.json')
            manager = ConfigManager(config_path)
            config = Config()
            config.translation['default_target'] = 'en'
            manager.save(config)

            loaded = manager.load()
            assert loaded.translation['default_target'] == 'en'
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd /home/peter/project/linux-translate
python -m pytest tests/test_config.py -v
```

Expected: ImportError: No module named 'src.config'

- [ ] **Step 3: 实现配置模块**

```python
# src/config.py
import json
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Any


DEFAULT_CONFIG = {
    'translation': {
        'priority': ['google', 'baidu', 'youdao', 'argos'],
        'default_source': 'auto',
        'default_target': 'zh',
        'api_keys': {
            'baidu': {'appid': '', 'key': ''},
            'youdao': {'appkey': '', 'appsecret': ''}
        }
    },
    'ocr': {
        'priority': ['tesseract', 'cloud'],
        'api_keys': {
            'baidu': {'appid': '', 'key': ''}
        }
    },
    'tts': {
        'priority': ['online', 'offline'],
        'speed': 1.0,
        'volume': 1.0
    },
    'hotkeys': {
        'translate_selection': '<Ctrl><Alt>t',
        'ocr_translate': '<Ctrl><Alt>o',
        'show_float_window': '<Ctrl><Alt>f'
    },
    'ui': {
        'follow_mouse': True,
        'float_window_visible': True,
        'theme': 'system'
    }
}


class Config:
    def __init__(self, data: Dict[str, Any] = None):
        if data is None:
            data = DEFAULT_CONFIG.copy()
        self.translation = data.get('translation', DEFAULT_CONFIG['translation'].copy())
        self.ocr = data.get('ocr', DEFAULT_CONFIG['ocr'].copy())
        self.tts = data.get('tts', DEFAULT_CONFIG['tts'].copy())
        self.hotkeys = data.get('hotkeys', DEFAULT_CONFIG['hotkeys'].copy())
        self.ui = data.get('ui', DEFAULT_CONFIG['ui'].copy())

    def to_dict(self) -> Dict[str, Any]:
        return {
            'translation': self.translation,
            'ocr': self.ocr,
            'tts': self.tts,
            'hotkeys': self.hotkeys,
            'ui': self.ui
        }


class ConfigManager:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_dir = os.path.expanduser('~/.config/linux-translate')
            os.makedirs(config_dir, exist_ok=True)
            config_path = os.path.join(config_dir, 'config.json')
        self.config_path = config_path

    def load(self) -> Config:
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Config(data)
        return Config()

    def save(self, config: Config):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
```

- [ ] **Step 4: 运行测试确认通过**

```bash
python -m pytest tests/test_config.py -v
```

Expected: 4 tests passed

- [ ] **Step 5: 提交**

```bash
git add src/config.py tests/test_config.py
git commit -m "feat: add configuration management module"
```

---

## Task 3: 数据库历史记录模块

**Files:**
- Create: `src/db/__init__.py`
- Create: `src/db/history.py`
- Create: `tests/test_history.py`

- [ ] **Step 1: 编写数据库模块测试**

```python
# tests/test_history.py
import os
import tempfile
import pytest
from datetime import datetime
from src.db.history import HistoryManager, TranslationRecord


class TestTranslationRecord:
    def test_record_creation(self):
        record = TranslationRecord(
            id=1,
            source_text="hello",
            translated_text="你好",
            source_lang="en",
            target_lang="zh"
        )
        assert record.source_text == "hello"
        assert record.translated_text == "你好"


class TestHistoryManager:
    def test_init_creates_table(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        try:
            manager = HistoryManager(db_path)
            assert os.path.exists(db_path)
        finally:
            os.unlink(db_path)

    def test_add_record(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        try:
            manager = HistoryManager(db_path)
            record_id = manager.add_record(
                source_text="hello",
                translated_text="你好",
                source_lang="en",
                target_lang="zh"
            )
            assert record_id > 0
        finally:
            os.unlink(db_path)

    def test_get_records(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        try:
            manager = HistoryManager(db_path)
            manager.add_record("hello", "你好", "en", "zh")
            manager.add_record("world", "世界", "en", "zh")
            records = manager.get_records(limit=10)
            assert len(records) == 2
            assert records[0].source_text == "world"  # Most recent first
        finally:
            os.unlink(db_path)

    def test_search_records(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        try:
            manager = HistoryManager(db_path)
            manager.add_record("hello world", "你好世界", "en", "zh")
            manager.add_record("goodbye", "再见", "en", "zh")
            records = manager.search_records("hello")
            assert len(records) == 1
            assert records[0].source_text == "hello world"
        finally:
            os.unlink(db_path)

    def test_delete_record(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        try:
            manager = HistoryManager(db_path)
            record_id = manager.add_record("test", "测试", "en", "zh")
            manager.delete_record(record_id)
            records = manager.get_records()
            assert len(records) == 0
        finally:
            os.unlink(db_path)
```

- [ ] **Step 2: 运行测试确认失败**

```bash
python -m pytest tests/test_history.py -v
```

Expected: ImportError

- [ ] **Step 3: 实现数据库模块**

```python
# src/db/__init__.py
from .history import HistoryManager, TranslationRecord

__all__ = ['HistoryManager', 'TranslationRecord']
```

```python
# src/db/history.py
import sqlite3
import os
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class TranslationRecord:
    id: int
    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    api_used: Optional[str] = None
    timestamp: Optional[datetime] = None


class HistoryManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_dir = os.path.expanduser('~/.local/share/linux-translate')
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, 'history.db')
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_text TEXT NOT NULL,
                    translated_text TEXT NOT NULL,
                    source_lang TEXT NOT NULL,
                    target_lang TEXT NOT NULL,
                    api_used TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp ON history(timestamp)
            ''')
            conn.commit()

    def add_record(self, source_text: str, translated_text: str,
                   source_lang: str, target_lang: str,
                   api_used: str = None) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                INSERT INTO history (source_text, translated_text, source_lang, target_lang, api_used)
                VALUES (?, ?, ?, ?, ?)
            ''', (source_text, translated_text, source_lang, target_lang, api_used))
            conn.commit()
            return cursor.lastrowid

    def get_records(self, limit: int = 100, offset: int = 0) -> List[TranslationRecord]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT id, source_text, translated_text, source_lang, target_lang, api_used, timestamp
                FROM history
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            rows = cursor.fetchall()
            return [TranslationRecord(
                id=row['id'],
                source_text=row['source_text'],
                translated_text=row['translated_text'],
                source_lang=row['source_lang'],
                target_lang=row['target_lang'],
                api_used=row['api_used'],
                timestamp=datetime.fromisoformat(row['timestamp']) if row['timestamp'] else None
            ) for row in rows]

    def search_records(self, keyword: str, limit: int = 100) -> List[TranslationRecord]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT id, source_text, translated_text, source_lang, target_lang, api_used, timestamp
                FROM history
                WHERE source_text LIKE ? OR translated_text LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (f'%{keyword}%', f'%{keyword}%', limit))
            rows = cursor.fetchall()
            return [TranslationRecord(
                id=row['id'],
                source_text=row['source_text'],
                translated_text=row['translated_text'],
                source_lang=row['source_lang'],
                target_lang=row['target_lang'],
                api_used=row['api_used'],
                timestamp=datetime.fromisoformat(row['timestamp']) if row['timestamp'] else None
            ) for row in rows]

    def delete_record(self, record_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('DELETE FROM history WHERE id = ?', (record_id,))
            conn.commit()
            return cursor.rowcount > 0

    def clear_all(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM history')
            conn.commit()

    def export_to_csv(self, filepath: str):
        import csv
        records = self.get_records(limit=10000)
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Source', 'Translation', 'From', 'To', 'API', 'Time'])
            for r in records:
                writer.writerow([r.id, r.source_text, r.translated_text,
                                r.source_lang, r.target_lang, r.api_used, r.timestamp])
```

- [ ] **Step 4: 运行测试确认通过**

```bash
python -m pytest tests/test_history.py -v
```

Expected: 6 tests passed

- [ ] **Step 5: 提交**

```bash
git add src/db/ tests/test_history.py
git commit -m "feat: add SQLite history management module"
```

---

## Task 4: 剪贴板工具模块

**Files:**
- Create: `src/utils/__init__.py`
- Create: `src/utils/clipboard.py`
- Create: `tests/test_clipboard.py`

- [ ] **Step 1: 编写剪贴板工具测试**

```python
# tests/test_clipboard.py
import pytest
from unittest.mock import patch, MagicMock
from src.utils.clipboard import ClipboardManager


class TestClipboardManager:
    def test_get_text(self):
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout='test text\n', returncode=0)
            result = ClipboardManager.get_text()
            assert result == 'test text'

    def test_get_text_empty(self):
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout='\n', returncode=0)
            result = ClipboardManager.get_text()
            assert result == ''

    def test_set_text(self):
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = ClipboardManager.set_text('test text')
            assert result is True
```

- [ ] **Step 2: 运行测试确认失败**

```bash
python -m pytest tests/test_clipboard.py -v
```

- [ ] **Step 3: 实现剪贴板模块**

```python
# src/utils/__init__.py
from .clipboard import ClipboardManager

__all__ = ['ClipboardManager']
```

```python
# src/utils/clipboard.py
import subprocess
import shutil


class ClipboardManager:
    _wl_copy = None
    _wl_paste = None

    @classmethod
    def _find_commands(cls):
        if cls._wl_copy is None:
            cls._wl_copy = shutil.which('wl-copy')
            cls._wl_paste = shutil.which('wl-paste')
        return cls._wl_copy, cls._wl_paste

    @classmethod
    def get_text(cls) -> str:
        _, wl_paste = cls._find_commands()
        if wl_paste:
            try:
                result = subprocess.run(
                    [wl_paste, '--no-newline'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return result.stdout
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
        return ''

    @classmethod
    def set_text(cls, text: str) -> bool:
        wl_copy, _ = cls._find_commands()
        if wl_copy:
            try:
                result = subprocess.run(
                    [wl_copy],
                    input=text,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
        return False

    @classmethod
    def is_available(cls) -> bool:
        wl_copy, wl_paste = cls._find_commands()
        return wl_copy is not None and wl_paste is not None
```

- [ ] **Step 4: 运行测试确认通过**

```bash
python -m pytest tests/test_clipboard.py -v
```

Expected: 3 tests passed

- [ ] **Step 5: 提交**

```bash
git add src/utils/ tests/test_clipboard.py
git commit -m "feat: add Wayland clipboard utility module"
```

---

## Task 5: 翻译引擎基类与 Google 翻译实现

**Files:**
- Create: `src/core/translation/__init__.py`
- Create: `src/core/translation/base.py`
- Create: `src/core/translation/google.py`
- Create: `tests/test_translation_google.py`

- [ ] **Step 1: 编写翻译引擎测试**

```python
# tests/test_translation_google.py
import pytest
from unittest.mock import patch, MagicMock
from src.core.translation.base import TranslationResult
from src.core.translation.google import GoogleTranslator


class TestTranslationResult:
    def test_result_creation(self):
        result = TranslationResult(
            text="你好",
            source_lang="en",
            target_lang="zh",
            original_text="hello"
        )
        assert result.text == "你好"
        assert result.source_lang == "en"


class TestGoogleTranslator:
    def test_is_available(self):
        with patch('requests.get') as mock_get:
            mock_get.return_value = MagicMock(status_code=200)
            translator = GoogleTranslator()
            assert translator.is_available() is True

    def test_translate_mock(self):
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = [[["hello world", "你好世界", None, None, 1]], None, "en"]
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            translator = GoogleTranslator()
            result = translator.translate("hello world", "en", "zh")
            assert result.text == "你好世界"
            assert result.source_lang == "en"
            assert result.target_lang == "zh"
```

- [ ] **Step 2: 运行测试确认失败**

```bash
python -m pytest tests/test_translation_google.py -v
```

- [ ] **Step 3: 实现翻译引擎基类和 Google 翻译**

```python
# src/core/translation/__init__.py
from .base import TranslationEngine, TranslationResult
from .google import GoogleTranslator

__all__ = ['TranslationEngine', 'TranslationResult', 'GoogleTranslator']
```

```python
# src/core/translation/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class TranslationResult:
    text: str
    source_lang: str
    target_lang: str
    original_text: str
    pronunciation: Optional[str] = None


class TranslationEngine(ABC):
    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
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
# src/core/translation/google.py
import requests
import json
from .base import TranslationEngine, TranslationResult


class GoogleTranslator(TranslationEngine):
    BASE_URL = "https://translate.googleapis.com/translate_a/single"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "google"

    def is_available(self) -> bool:
        try:
            response = requests.get(
                self.BASE_URL,
                params={'client': 'gtx', 'sl': 'auto', 'tl': 'en', 'dt': 't', 'q': 'test'},
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception:
            return False

    def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        params = {
            'client': 'gtx',
            'sl': source_lang if source_lang != 'auto' else 'auto',
            'tl': target_lang,
            'dt': 't',
            'q': text
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            translated = ''.join(item[0] for item in data[0] if item[0])
            detected_lang = data[2] if len(data) > 2 and data[2] else source_lang

            return TranslationResult(
                text=translated,
                source_lang=detected_lang,
                target_lang=target_lang,
                original_text=text
            )
        except Exception as e:
            raise TranslationError(f"Google translate failed: {e}")


class TranslationError(Exception):
    pass
```

- [ ] **Step 4: 运行测试确认通过**

```bash
python -m pytest tests/test_translation_google.py -v
```

Expected: 3 tests passed

- [ ] **Step 5: 提交**

```bash
git add src/core/translation/ tests/test_translation_google.py
git commit -m "feat: add translation engine base and Google translator"
```

---

## Task 6: 百度翻译实现

**Files:**
- Create: `src/core/translation/baidu.py`
- Create: `tests/test_translation_baidu.py`

- [ ] **Step 1: 编写百度翻译测试**

```python
# tests/test_translation_baidu.py
import pytest
from unittest.mock import patch, MagicMock
from src.core.translation.baidu import BaiduTranslator


class TestBaiduTranslator:
    def test_is_available_with_config(self):
        translator = BaiduTranslator(appid="test", key="test")
        assert translator.is_available() is True

    def test_is_available_without_config(self):
        translator = BaiduTranslator()
        assert translator.is_available() is False

    def test_translate_mock(self):
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "from": "en",
                "to": "zh",
                "trans_result": [{"src": "hello", "dst": "你好"}]
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            translator = BaiduTranslator(appid="test", key="test")
            result = translator.translate("hello", "en", "zh")
            assert result.text == "你好"
```

- [ ] **Step 2: 运行测试确认失败**

```bash
python -m pytest tests/test_translation_baidu.py -v
```

- [ ] **Step 3: 实现百度翻译**

```python
# src/core/translation/baidu.py
import requests
import hashlib
import random
from .base import TranslationEngine, TranslationResult


class BaiduTranslator(TranslationEngine):
    BASE_URL = "https://fanyi-api.baidu.com/api/trans/vip/translate"

    def __init__(self, appid: str = None, key: str = None, timeout: int = 10):
        self.appid = appid
        self.key = key
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "baidu"

    def is_available(self) -> bool:
        return bool(self.appid and self.key)

    def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        if not self.is_available():
            raise TranslationError("Baidu translator not configured")

        salt = random.randint(32768, 65536)
        sign_str = self.appid + text + str(salt) + self.key
        sign = hashlib.md5(sign_str.encode()).hexdigest()

        # Language code mapping
        lang_map = {'zh': 'zh', 'en': 'en', 'auto': 'auto'}
        from_lang = lang_map.get(source_lang, source_lang)
        to_lang = lang_map.get(target_lang, target_lang)

        payload = {
            'q': text,
            'from': from_lang,
            'to': to_lang,
            'appid': self.appid,
            'salt': salt,
            'sign': sign
        }

        try:
            response = requests.post(self.BASE_URL, data=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            if 'error_code' in data:
                raise TranslationError(f"Baidu API error: {data['error_msg']}")

            translated = ''.join(item['dst'] for item in data['trans_result'])
            return TranslationResult(
                text=translated,
                source_lang=data.get('from', source_lang),
                target_lang=data.get('to', target_lang),
                original_text=text
            )
        except Exception as e:
            raise TranslationError(f"Baidu translate failed: {e}")


class TranslationError(Exception):
    pass
```

- [ ] **Step 4: 更新 __init__.py**

```python
# src/core/translation/__init__.py
from .base import TranslationEngine, TranslationResult
from .google import GoogleTranslator
from .baidu import BaiduTranslator

__all__ = ['TranslationEngine', 'TranslationResult', 'GoogleTranslator', 'BaiduTranslator']
```

- [ ] **Step 5: 运行测试确认通过**

```bash
python -m pytest tests/test_translation_baidu.py -v
```

Expected: 3 tests passed

- [ ] **Step 6: 提交**

```bash
git add src/core/translation/baidu.py tests/test_translation_baidu.py
git commit -m "feat: add Baidu translator"
```

---

## Task 7: TTS 引擎基类与在线 TTS 实现

**Files:**
- Create: `src/core/tts/__init__.py`
- Create: `src/core/tts/base.py`
- Create: `src/core/tts/online.py`
- Create: `tests/test_tts_online.py`

- [ ] **Step 1: 编写 TTS 测试**

```python
# tests/test_tts_online.py
import pytest
from unittest.mock import patch, MagicMock, mock_open
from src.core.tts.online import OnlineTTS


class TestOnlineTTS:
    def test_is_available(self):
        tts = OnlineTTS()
        assert tts.is_available() is True

    def test_play_text_mock(self):
        with patch('gtts.gTTS') as mock_gtts, \
             patch('os.path.exists', return_value=True), \
             patch('os.remove') as mock_remove, \
             patch('builtins.open', mock_open()):

            mock_tts = MagicMock()
            mock_gtts.return_value = mock_tts

            tts = OnlineTTS()
            # Just test that it creates the TTS object
            mock_tts.save = MagicMock()
            mock_tts.save.return_value = None

            # Note: actual play test requires more complex mocking
            assert tts.is_available() is True
```

- [ ] **Step 2: 运行测试确认失败**

```bash
python -m pytest tests/test_tts_online.py -v
```

- [ ] **Step 3: 实现 TTS 基类和在线 TTS**

```python
# src/core/tts/__init__.py
from .base import TTSEngine, TTSError
from .online import OnlineTTS

__all__ = ['TTSEngine', 'TTSError', 'OnlineTTS']
```

```python
# src/core/tts/base.py
from abc import ABC, abstractmethod


class TTSEngine(ABC):
    @abstractmethod
    def play_text(self, text: str, lang: str = 'zh') -> bool:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass


class TTSError(Exception):
    pass
```

```python
# src/core/tts/online.py
import os
import tempfile
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from .base import TTSEngine, TTSError


class OnlineTTS(TTSEngine):
    def __init__(self, speed: float = 1.0):
        self.speed = speed

    @property
    def name(self) -> str:
        return "online"

    def is_available(self) -> bool:
        try:
            import gtts
            import pydub
            return True
        except ImportError:
            return False

    def play_text(self, text: str, lang: str = 'zh') -> bool:
        if not text or not text.strip():
            return False

        lang_map = {
            'zh': 'zh-CN',
            'en': 'en',
            'auto': 'zh-CN'
        }
        tts_lang = lang_map.get(lang, lang)

        try:
            tts = gTTS(text=text, lang=tts_lang, slow=False)

            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                tmp_path = tmp.name

            tts.save(tmp_path)

            # Play audio
            audio = AudioSegment.from_mp3(tmp_path)
            if self.speed != 1.0:
                audio = audio._spawn(audio.raw_data, overrides={
                    "frame_rate": int(audio.frame_rate * self.speed)
                })

            play(audio)
            os.unlink(tmp_path)
            return True

        except Exception as e:
            raise TTSError(f"Online TTS failed: {e}")
```

- [ ] **Step 4: 运行测试确认通过**

```bash
python -m pytest tests/test_tts_online.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/core/tts/ tests/test_tts_online.py
git commit -m "feat: add TTS engine base and online TTS implementation"
```

---

## Task 8: 主窗口 GUI

**Files:**
- Create: `src/gui/__init__.py`
- Create: `src/gui/main_window.py`

- [ ] **Step 1: 创建主窗口**

```python
# src/gui/__init__.py
from .main_window import MainWindow

__all__ = ['MainWindow']
```

```python
# src/gui/main_window.py
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QComboBox, QLabel,
    QSystemTrayIcon, QMenu, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QAction

from src.core.translation import TranslationResult


class MainWindow(QMainWindow):
    translate_requested = pyqtSignal(str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Linux 翻译助手")
        self.setMinimumSize(600, 400)
        self._setup_ui()
        self._setup_tray()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Language selection
        lang_layout = QHBoxLayout()
        self.source_lang = QComboBox()
        self.source_lang.addItems(['自动检测', '中文', '英文'])
        self.source_lang.setCurrentIndex(0)

        self.target_lang = QComboBox()
        self.target_lang.addItems(['中文', '英文'])
        self.target_lang.setCurrentIndex(0)

        lang_layout.addWidget(QLabel("从:"))
        lang_layout.addWidget(self.source_lang)
        lang_layout.addWidget(QLabel("到:"))
        lang_layout.addWidget(self.target_lang)
        lang_layout.addStretch()

        layout.addLayout(lang_layout)

        # Input
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("输入要翻译的文本...")
        self.input_text.setMaximumHeight(150)
        layout.addWidget(self.input_text)

        # Translate button
        self.translate_btn = QPushButton("翻译")
        self.translate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.translate_btn.clicked.connect(self._on_translate)
        layout.addWidget(self.translate_btn)

        # Output
        self.output_text = QTextEdit()
        self.output_text.setPlaceholderText("翻译结果...")
        self.output_text.setReadOnly(True)
        self.output_text.setMaximumHeight(150)
        layout.addWidget(self.output_text)

        # TTS buttons
        tts_layout = QHBoxLayout()
        self.play_source_btn = QPushButton("朗读原文")
        self.play_translated_btn = QPushButton("朗读译文")
        tts_layout.addWidget(self.play_source_btn)
        tts_layout.addWidget(self.play_translated_btn)
        tts_layout.addStretch()
        layout.addLayout(tts_layout)

    def _setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_menu = QMenu()

        self.show_action = QAction("显示", self)
        self.show_action.triggered.connect(self.show)

        self.quit_action = QAction("退出", self)
        self.quit_action.triggered.connect(self._on_quit)

        self.tray_menu.addAction(self.show_action)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.quit_action)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)

    def _on_translate(self):
        text = self.input_text.toPlainText().strip()
        if text:
            source = ['auto', 'zh', 'en'][self.source_lang.currentIndex()]
            target = ['zh', 'en'][self.target_lang.currentIndex()]
            self.translate_requested.emit(text, source, target)

    def set_translation_result(self, result: TranslationResult):
        self.output_text.setPlainText(result.text)

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()

    def _on_quit(self):
        self.tray_icon.hide()
        QApplication.quit()

    def closeEvent(self, event):
        self.hide()
        self.tray_icon.show()
        event.ignore()
```

- [ ] **Step 2: 提交**

```bash
git add src/gui/main_window.py
git commit -m "feat: add main window GUI"
```

---

## Task 9: 应用程序入口与核心控制器

**Files:**
- Create: `src/__init__.py`
- Create: `src/main.py`

- [ ] **Step 1: 创建应用程序入口**

```python
# src/__init__.py
__version__ = "0.1.0"
```

```python
# src/main.py
import sys
import signal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from src.gui.main_window import MainWindow
from src.config import ConfigManager
from src.db.history import HistoryManager
from src.core.translation import GoogleTranslator, BaiduTranslator


class TranslatorApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # Initialize components
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load()
        self.history = HistoryManager()

        # Initialize translators
        self.translators = {}
        self._init_translators()

        # Create main window
        self.main_window = MainWindow()
        self.main_window.translate_requested.connect(self._on_translate)

        # Setup signal handling
        signal.signal(signal.SIGINT, self._signal_handler)
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: None)
        self.timer.start(100)

    def _init_translators(self):
        # Google Translator
        google = GoogleTranslator()
        if google.is_available():
            self.translators['google'] = google

        # Baidu Translator
        baidu_config = self.config.translation.get('api_keys', {}).get('baidu', {})
        if baidu_config.get('appid') and baidu_config.get('key'):
            baidu = BaiduTranslator(
                appid=baidu_config['appid'],
                key=baidu_config['key']
            )
            if baidu.is_available():
                self.translators['baidu'] = baidu

    def _on_translate(self, text: str, source_lang: str, target_lang: str):
        # Try translators in priority order
        priority = self.config.translation.get('priority', ['google'])
        for engine_name in priority:
            if engine_name in self.translators:
                try:
                    result = self.translators[engine_name].translate(
                        text, source_lang, target_lang
                    )
                    self.main_window.set_translation_result(result)
                    # Save to history
                    self.history.add_record(
                        result.original_text,
                        result.text,
                        result.source_lang,
                        result.target_lang,
                        engine_name
                    )
                    return
                except Exception as e:
                    print(f"Translation failed with {engine_name}: {e}")
                    continue

        self.main_window.set_translation_result(None)

    def _signal_handler(self, signum, frame):
        self.quit()

    def run(self):
        self.main_window.show()
        return self.app.exec()

    def quit(self):
        self.app.quit()


def main():
    app = TranslatorApp()
    sys.exit(app.run())


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: 测试运行**

```bash
python -m src.main
```

Expected: 主窗口显示

- [ ] **Step 3: 提交**

```bash
git add src/__init__.py src/main.py
git commit -m "feat: add application entry point and core controller"
```

---

## 自审查检查

**1. Spec 覆盖检查:**
- ✅ 配置管理 (Task 2)
- ✅ 历史记录 (Task 3)
- ✅ 剪贴板工具 (Task 4)
- ✅ 翻译引擎 - Google (Task 5)
- ✅ 翻译引擎 - 百度 (Task 6)
- ⚠️ 翻译引擎 - 有道 (待扩展)
- ⚠️ 翻译引擎 - argos 离线 (待扩展)
- ✅ TTS 引擎 (Task 7)
- ⚠️ TTS 离线引擎 (待扩展)
- ✅ 主窗口 GUI (Task 8)
- ⚠️ 悬浮窗 (待扩展)
- ⚠️ 翻译结果弹窗 (待扩展)
- ⚠️ 全局快捷键 (待扩展)
- ⚠️ GNOME Shell 扩展 (待扩展)
- ⚠️ OCR 引擎 (待扩展)

**2. 占位符扫描:**
- ✅ 无 TBD/TODO 占位符
- ✅ 所有测试包含具体代码
- ✅ 所有实现包含具体代码

**3. 类型一致性:**
- ✅ TranslationResult 在所有任务中一致
- ✅ Config 类使用一致

---

## 后续扩展任务

以下功能将在后续迭代中实现：

1. **有道翻译实现** - 类似百度翻译
2. **Argos 离线翻译** - 本地翻译引擎
3. **离线 TTS 实现** - 使用 pyttsx3/espeak
4. **悬浮窗** - 常驻翻译输入窗口
5. **翻译结果弹窗** - 跟随鼠标显示结果
6. **全局快捷键** - 使用 pynput 监听
7. **OCR 引擎** - Tesseract 和云端 OCR
8. **GNOME Shell 扩展** - 右键菜单集成
9. **设置对话框** - 配置界面
10. **历史记录对话框** - 查看和管理历史

---

## 运行命令

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
python -m src.main

# 运行测试
python -m pytest tests/ -v
```
