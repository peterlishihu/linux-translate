# Linux 翻译助手

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-6.4%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

一个基于 Python + PyQt6 的 Linux 桌面翻译应用，支持中英互译、OCR 识别、语音朗读和历史记录。

## 功能特性

**翻译**
- Google Translate API
- 百度翻译 API
- 有道翻译 API
- 支持单词和句子翻译
- 屏幕划词翻译
- OCR 截图识别翻译

**语音**
- 在线语音 (Google TTS)
- 离线语音 (pyttsx3)
- 中英文朗读

**界面**
- 主窗口翻译
- 悬浮窗快捷翻译
- 翻译结果弹窗（跟随鼠标）
- 历史记录管理
- 系统托盘图标

**其他**
- 全局快捷键支持
- SQLite 历史记录
- 配置持久化

## 快速开始

### 安装依赖

**Ubuntu/Debian:**
```bash
sudo apt install -y python3-dev python3-pip tesseract-ocr \
    tesseract-ocr-chi-sim wl-clipboard grim slurp espeak-ng
```

**Fedora:**
```bash
sudo dnf install -y python3-devel python3-pip tesseract \
    tesseract-langpack-chi_sim wl-clipboard grim slurp espeak-ng
```

**Arch:**
```bash
sudo pacman -S python python-pip tesseract tesseract-data-chi_sim \
    wl-clipboard grim slurp espeak-ng
```

### 安装应用

```bash
git clone https://github.com/peterlishihu/linux-translate.git
cd linux-translate
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 运行

```bash
python -m src.main
```

## 详细文档

- [安装与使用手册](docs/INSTALL.md) - 完整的安装、编译、调试指南
- [设计文档](docs/superpowers/specs/2026-03-31-linux-translator-design.md) - 架构设计

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| Ctrl+Alt+T | 翻译选中文本 |
| Ctrl+Alt+O | OCR 截图翻译 |
| Ctrl+Alt+F | 显示/隐藏悬浮窗 |

## 项目结构

```
linux-translate/
├── src/
│   ├── core/
│   │   ├── translation/    # 翻译引擎 (Google, 百度, 有道)
│   │   ├── tts/            # 语音引擎 (在线/离线)
│   │   └── ocr/            # OCR 引擎 (Tesseract)
│   ├── gui/                # GUI 组件
│   ├── services/           # 服务层 (全局快捷键)
│   ├── db/                 # 数据库 (SQLite)
│   └── utils/              # 工具 (剪贴板)
├── tests/                  # 测试 (34 个测试)
├── docs/                   # 文档
└── requirements.txt        # 依赖
```

## 测试

```bash
python -m pytest tests/ -v
```

预期输出：
```
============================= test session starts =============================
platform linux -- Python 3.10.12, pytest-9.0.2, pluggy-1.6.0
collected 34 items

tests/test_clipboard.py ...
tests/test_config.py ...
tests/test_history.py ...
tests/test_hotkey.py ...
tests/test_ocr_tesseract.py ...
tests/test_translation_baidu.py ...
tests/test_translation_google.py ...
tests/test_translation_youdao.py ...
tests/test_tts_offline.py ...
tests/test_tts_online.py ...

============================== 34 passed in 1.69s ==============================
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
