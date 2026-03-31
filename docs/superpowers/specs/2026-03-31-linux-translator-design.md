# Linux 翻译助手设计文档

**日期**: 2026-03-31  
**状态**: 待实现  

---

## 概述

一个 Linux GNOME Wayland 桌面环境下的中英文翻译工具，支持划词翻译、OCR 识别、语音朗读和历史记录管理。

---

## 目标平台

- **操作系统**: Linux
- **桌面环境**: GNOME
- **显示服务器**: Wayland

---

## 功能需求

### 1. 核心翻译功能
- 支持中英互译
- 支持翻译单词和句子
- 支持多种翻译 API（可配置切换）

### 2. 划词翻译
- 全局快捷键触发翻译
- GNOME Shell 扩展右键菜单
- 通过剪贴板获取选中文本

### 3. OCR 识别
- 截图框选识别区域
- 本地 Tesseract OCR（优先）
- 云端 OCR 作为备用

### 4. 语音功能
- 中英文朗读
- 在线 TTS（优先）
- 离线 TTS 作为备用
- 支持单独播放原文或译文

### 5. 历史记录
- SQLite 数据库存储
- 支持查询、删除、导出 CSV

### 6. 界面设计
- 主窗口：设置、历史记录、API 配置
- 悬浮窗：快速翻译输入
- 翻译结果弹窗：跟随鼠标位置显示

---

## 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                      GUI 层 (PyQt6)                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   主窗口    │  │   悬浮窗    │  │   翻译结果弹窗      │  │
│  │ - 设置面板  │  │ - 输入框    │  │   (跟随鼠标)        │  │
│  │ - 历史记录  │  │ - 快捷按钮  │  │                     │  │
│  │ - API配置   │  │             │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    核心服务层                               │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  翻译引擎   │  │  OCR引擎    │  │  TTS引擎    │         │
│  │ (多API可插) │  │(Tesseract+ │  │ (在线+离线) │         │
│  │             │  │  云端混合)  │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│                    数据层                                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ SQLite历史  │  │ JSON配置    │  │  GNOME Shell 扩展   │  │
│  │             │  │             │  │  (右键菜单集成)     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 组件详细设计

### 1. 翻译引擎 (TranslationEngine)

**接口定义**:
```python
class TranslationEngine(ABC):
    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass
```

**实现类**:
- `GoogleTranslator` - Google Translate API
- `BaiduTranslator` - 百度翻译 API
- `YoudaoTranslator` - 有道翻译 API
- `ArgosTranslator` - 本地离线翻译 (argos-translate)

**配置**:
```json
{
  "translation": {
    "priority": ["google", "baidu", "youdao", "argos"],
    "api_keys": {
      "baidu": {"appid": "", "key": ""},
      "youdao": {"appkey": "", "appsecret": ""}
    }
  }
}
```

### 2. OCR 引擎 (OCREngine)

**实现类**:
- `TesseractOCR` - 本地 OCR
  - 依赖: tesseract-ocr, tesseract-ocr-chi-sim
- `CloudOCR` - 云端 OCR
  - 支持: 百度、腾讯、阿里云 OCR API

**截图工具**:
- Wayland: `grim` + `slurp`
- 备选: `gnome-screenshot`

**工作流程**:
1. 用户触发 OCR（快捷键或按钮）
2. 调用截图工具获取用户框选区域
3. 优先使用 TesseractOCR
4. 若识别失败或质量不佳，自动切换到 CloudOCR

### 3. TTS 引擎 (TTSEngine)

**实现类**:
- `OnlineTTS` - 在线语音合成
  - gTTS (Google TTS)
  - 百度语音合成 API
- `OfflineTTS` - 离线语音
  - pyttsx3
  - espeak/espeak-ng + mbrola（中文）

**配置**:
```json
{
  "tts": {
    "priority": ["online", "offline"],
    "speed": 1.0,
    "volume": 1.0
  }
}
```

### 4. 历史记录 (HistoryManager)

**数据库表结构**:
```sql
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_text TEXT NOT NULL,
    translated_text TEXT NOT NULL,
    source_lang TEXT NOT NULL,
    target_lang TEXT NOT NULL,
    api_used TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_timestamp ON history(timestamp);
```

**功能**:
- 添加记录
- 分页查询
- 按关键词搜索
- 删除单条/批量删除
- 导出为 CSV

### 5. 系统集成

**全局快捷键**:
- 使用 `pynput` 或 `evdev` 监听系统级快捷键
- 默认快捷键: `Ctrl+Alt+T`（可配置）
- 触发后通过 `wl-clipboard` 获取剪贴板内容

**GNOME Shell 扩展**:
- 扩展 ID: `linux-translator@local`
- 功能: 在右键菜单中添加"翻译选中文本"选项
- 与主程序通过 D-Bus 通信

---

## 项目结构

```
linux-translate/
├── src/
│   ├── __init__.py
│   ├── main.py                 # 程序入口
│   ├── config.py               # 配置管理
│   ├── gui/                    # GUI 组件
│   │   ├── __init__.py
│   │   ├── main_window.py      # 主窗口
│   │   ├── float_window.py     # 悬浮窗
│   │   ├── result_popup.py     # 翻译结果弹窗
│   │   ├── history_dialog.py   # 历史记录对话框
│   │   └── settings_dialog.py  # 设置对话框
│   ├── core/                   # 核心逻辑
│   │   ├── __init__.py
│   │   ├── translation/        # 翻译引擎
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── google.py
│   │   │   ├── baidu.py
│   │   │   ├── youdao.py
│   │   │   └── argos.py
│   │   ├── ocr/                # OCR 引擎
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── tesseract.py
│   │   │   └── cloud.py
│   │   └── tts/                # TTS 引擎
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── online.py
│   │       └── offline.py
│   ├── services/               # 外部服务封装
│   │   ├── __init__.py
│   │   └── clipboard.py        # 剪贴板操作
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   └── translation.py
│   ├── db/                     # 数据库管理
│   │   ├── __init__.py
│   │   └── history.py
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       └── screenshot.py
├── gnome-shell-extension/      # GNOME Shell 扩展
│   ├── metadata.json
│   ├── extension.js
│   └── stylesheet.css
├── data/                       # 数据文件
│   └── config.json
├── requirements.txt
├── setup.py
├── install.sh                  # 安装脚本
└── README.md
```

---

## 依赖清单

### Python 依赖

```
PyQt6>=6.4.0
requests>=2.28.0
Pillow>=9.0.0
pytesseract>=0.3.10
pyttsx3>=2.90
gTTS>=2.3.0
pynput>=1.7.6
argostranslate>=1.8.0
```

### 系统依赖

```
# OCR
- tesseract-ocr
- tesseract-ocr-chi-sim
- tesseract-ocr-chi-tra
- tesseract-ocr-eng

# 截图 (Wayland)
- grim
- slurp

# 剪贴板
- wl-clipboard

# TTS (离线)
- espeak-ng
- mbrola
- mbrola-cn1

# Python 开发
- python3-dev
- python3-pip
```

---

## 数据流

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  用户操作   │────▶│  触发事件   │────▶│  获取输入   │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  保存历史   │◀────│  显示结果   │◀────│  翻译引擎   │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  TTS 播放   │ (可选)
                    └─────────────┘
```

---

## 配置文件

**位置**: `~/.config/linux-translate/config.json`

```json
{
  "translation": {
    "priority": ["google", "baidu", "youdao", "argos"],
    "default_source": "auto",
    "default_target": "zh",
    "api_keys": {
      "baidu": {
        "appid": "",
        "key": ""
      },
      "youdao": {
        "appkey": "",
        "appsecret": ""
      }
    }
  },
  "ocr": {
    "priority": ["tesseract", "cloud"],
    "api_keys": {
      "baidu": {"appid": "", "key": ""}
    }
  },
  "tts": {
    "priority": ["online", "offline"],
    "speed": 1.0,
    "volume": 1.0
  },
  "hotkeys": {
    "translate_selection": "<Ctrl><Alt>t",
    "ocr_translate": "<Ctrl><Alt>o",
    "show_float_window": "<Ctrl><Alt>f"
  },
  "ui": {
    "follow_mouse": true,
    "float_window_visible": true,
    "theme": "system"
  }
}
```

---

## 安装方式

通过源码安装：

```bash
git clone <repository>
cd linux-translate
./install.sh
```

`install.sh` 脚本将：
1. 检查并安装系统依赖
2. 创建 Python 虚拟环境
3. 安装 Python 依赖
4. 安装 GNOME Shell 扩展
5. 创建桌面快捷方式

---

## 风险与限制

1. **Wayland 限制**: 无法直接读取其他应用的选中文本，必须通过剪贴板间接获取
2. **API 限制**: 免费翻译 API 有调用频率限制
3. **离线 TTS 质量**: 中文离线语音合成质量不如在线服务
4. **Tesseract 准确性**: 复杂背景下的 OCR 识别率可能较低

---

## 未来扩展

- [ ] 支持更多翻译 API（DeepL、Azure 等）
- [ ] 支持划词即译（无需复制）通过 GNOME 扩展增强
- [ ] 支持翻译结果收藏
- [ ] 支持生词本功能
- [ ] 支持多种主题
