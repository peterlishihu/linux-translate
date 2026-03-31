# Linux 翻译助手 - 安装与使用手册

## 目录

1. [系统要求](#系统要求)
2. [安装步骤](#安装步骤)
3. [编译构建](#编译构建)
4. [调试指南](#调试指南)
5. [配置说明](#配置说明)
6. [使用指南](#使用指南)
7. [常见问题](#常见问题)
8. [卸载](#卸载)

---

## 系统要求

### 操作系统
- **支持**: Ubuntu 20.04+, Debian 11+, Fedora 34+, Arch Linux
- **桌面环境**: GNOME (Wayland 或 X11), KDE Plasma, XFCE
- **架构**: x86_64, ARM64

### 必需依赖

#### Python 环境
```
Python >= 3.10
pip >= 21.0
```

#### 系统包

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    tesseract-ocr-chi-tra \
    tesseract-ocr-eng \
    wl-clipboard \
    grim \
    slurp \
    espeak-ng \
    libespeak-dev \
    portaudio19-dev \
    libasound2-dev
```

**Fedora:**
```bash
sudo dnf install -y \
    python3-devel \
    python3-pip \
    tesseract \
    tesseract-langpack-chi_sim \
    tesseract-langpack-chi_tra \
    tesseract-langpack-eng \
    wl-clipboard \
    grim \
    slurp \
    espeak-ng \
    espeak-ng-devel \
    portaudio-devel \
    alsa-lib-devel
```

**Arch Linux:**
```bash
sudo pacman -S \
    python \
    python-pip \
    tesseract \
    tesseract-data-chi_sim \
    tesseract-data-chi_tra \
    tesseract-data-eng \
    wl-clipboard \
    grim \
    slurp \
    espeak-ng \
    portaudio
```

---

## 安装步骤

### 方法一：从源码安装（推荐）

#### 1. 克隆仓库

```bash
cd ~
git clone https://github.com/peterlishihu/linux-translate.git
cd linux-translate
```

#### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. 安装 Python 依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. 验证安装

```bash
python -m pytest tests/ -v
```

预期输出：
```
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.0.2, pluggy-1.6.0
...
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

#### 5. 首次运行

```bash
python -m src.main
```

---

### 方法二：创建桌面快捷方式

#### 创建启动脚本

```bash
cat > ~/.local/bin/linux-translate << 'EOF'
#!/bin/bash
source ~/linux-translate/venv/bin/activate
cd ~/linux-translate
python -m src.main "$@"
EOF

chmod +x ~/.local/bin/linux-translate
```

#### 创建桌面文件

```bash
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/linux-translate.desktop << 'EOF'
[Desktop Entry]
Name=Linux 翻译助手
Name[en]=Linux Translator
Comment=中英翻译工具
Comment[en]=Chinese-English Translation Tool
Exec=/home/USERNAME/.local/bin/linux-translate
Icon=/home/USERNAME/linux-translate/data/icon.png
Terminal=false
Type=Application
Categories=Utility;TextTools;
StartupNotify=true
EOF

# 替换用户名
sed -i "s/USERNAME/$USER/g" ~/.local/share/applications/linux-translate.desktop

# 刷新桌面缓存
update-desktop-database ~/.local/share/applications/
```

---

### 方法三：系统级安装（可选）

#### 安装到 /opt

```bash
sudo mkdir -p /opt/linux-translate
sudo cp -r ~/linux-translate/* /opt/linux-translate/
sudo chown -R root:root /opt/linux-translate

# 创建启动脚本
sudo tee /usr/local/bin/linux-translate << 'EOF'
#!/bin/bash
cd /opt/linux-translate
source venv/bin/activate
python -m src.main "$@"
EOF

sudo chmod +x /usr/local/bin/linux-translate
```

---

## 编译构建

### 打包为 AppImage（高级用户）

#### 1. 安装工具

```bash
pip install appimage-builder
```

#### 2. 创建 AppImage 配置

```yaml
# appimage-builder.yml
version: 1
AppDir:
  path: ./AppDir
  app_info:
    id: com.example.linux-translate
    name: Linux 翻译助手
    icon: icon
    version: 0.1.0
    exec: usr/bin/python3
    exec_args: -m src.main
  runtime:
    env:
      PYTHONPATH: "${APPDIR}/usr/lib/python3.10/site-packages:${APPDIR}/usr/lib/python3/dist-packages"
  
  apt:
    arch: amd64
    sources:
      - sourceline: 'deb [arch=amd64] http://archive.ubuntu.com/ubuntu/ jammy main restricted universe multiverse'
    include:
      - python3
      - python3-pip
      - tesseract-ocr
      - tesseract-ocr-chi-sim
      - tesseract-ocr-eng
      - wl-clipboard
      
AppImage:
  arch: x86_64
  update-information: None
```

#### 3. 构建

```bash
appimage-builder --recipe appimage-builder.yml
```

---

## 调试指南

### 启用调试模式

#### 1. 修改日志级别

```python
# 在 src/main.py 开头添加
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('~/linux-translate/debug.log'),
        logging.StreamHandler()
    ]
)
```

#### 2. 运行调试版本

```bash
python -m src.main 2>&1 | tee debug.log
```

---

### 常见问题排查

#### 问题 1：PyQt6 导入错误

**症状:**
```
ImportError: cannot import name 'Qt' from 'PyQt6.QtCore'
```

**解决:**
```bash
pip uninstall PyQt6 PyQt6-sip PyQt6-Qt6
pip install PyQt6==6.4.0
```

#### 问题 2：Tesseract 未找到

**症状:**
```
OCRError: Tesseract is not available
```

**排查:**
```bash
# 检查是否安装
which tesseract
tesseract --version

# 检查中文语言包
ls /usr/share/tesseract-ocr/4.00/tessdata/chi_sim.traineddata

# 手动指定路径
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata
```

#### 问题 3：Wayland 剪贴板失败

**症状:**
```
ClipboardManager.get_text() returns empty
```

**排查:**
```bash
# 检查 wl-clipboard 是否安装
which wl-copy
which wl-paste

# 测试剪贴板
echo "test" | wl-copy
wl-paste

# 如果是 X11 环境，安装 xclip 作为备用
sudo apt install xclip
```

#### 问题 4：全局快捷键不工作

**症状:**
快捷键无响应

**排查:**
```bash
# 检查 pynput 是否安装
python -c "from pynput import keyboard; print('OK')"

# 检查权限（Wayland 需要特定权限）
echo $XDG_SESSION_TYPE

# 对于 X11，检查是否有其他程序占用快捷键
xev | grep -i key
```

#### 问题 5：语音播放失败

**症状:**
点击"朗读"无声音

**排查:**
```bash
# 测试 pyttsx3
python -c "
import pyttsx3
engine = pyttsx3.init()
engine.say('Hello')
engine.runAndWait()
"

# 测试 gTTS
python -c "
from gtts import gTTS
import os
tts = gTTS('Hello', lang='en')
tts.save('test.mp3')
os.system('mpg123 test.mp3')
"

# 检查音频设备
aplay -l
```

---

### 使用 GDB 调试 Python 崩溃

```bash
# 安装 python-dbg（如需要）
sudo apt install python3-dbg

# 运行 gdb
gdb python3
(gdb) run -m src.main

# 崩溃后获取回溯
(gdb) bt
(gdb) py-bt
```

---

### 性能分析

#### 使用 cProfile

```bash
python -m cProfile -o profile.stats -m src.main

# 分析结果
python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(20)
"
```

---

## 配置说明

### 配置文件位置

```
~/.config/linux-translate/config.json
```

### 完整配置示例

```json
{
  "translation": {
    "priority": ["google", "baidu", "youdao"],
    "default_source": "auto",
    "default_target": "zh",
    "api_keys": {
      "baidu": {
        "appid": "your_baidu_appid",
        "key": "your_baidu_key"
      },
      "youdao": {
        "appkey": "your_youdao_key",
        "appsecret": "your_youdao_secret"
      }
    }
  },
  "ocr": {
    "priority": ["tesseract", "cloud"],
    "api_keys": {
      "baidu": {
        "appid": "",
        "key": ""
      }
    }
  },
  "tts": {
    "priority": ["online", "offline"],
    "speed": 1.0,
    "volume": 1.0
  },
  "hotkeys": {
    "translate_selection": "<ctrl>+<alt>+t",
    "ocr_translate": "<ctrl>+<alt>+o",
    "show_float_window": "<ctrl>+<alt>+f"
  },
  "ui": {
    "follow_mouse": true,
    "float_window_visible": true,
    "theme": "system"
  }
}
```

### 获取 API 密钥

#### 百度翻译 API

1. 访问 https://fanyi-api.baidu.com/
2. 注册账号并登录
3. 进入"管理控制台" → "开发者信息"
4. 获取 APP ID 和密钥

#### 有道翻译 API

1. 访问 https://ai.youdao.com/product-fanyi.s
2. 注册账号
3. 创建应用，获取应用 ID 和密钥

---

## 使用指南

### 启动应用

```bash
# 方式 1: 直接运行
python -m src.main

# 方式 2: 使用启动脚本
linux-translate

# 方式 3: 从桌面快捷方式
# 点击"Linux 翻译助手"图标
```

### 基本操作

#### 主窗口

1. **输入文本**: 在上方文本框输入要翻译的内容
2. **选择语言**: 使用下拉框选择源语言和目标语言
3. **点击翻译**: 点击绿色"翻译"按钮
4. **查看结果**: 在下方文本框查看翻译结果
5. **朗读**: 点击"朗读原文"或"朗读译文"

#### 悬浮窗

- **显示/隐藏**: Ctrl+Alt+F
- **拖动**: 按住标题栏拖动
- **快速翻译**: 输入文本后按 Enter

#### 全局快捷键

| 快捷键 | 功能 |
|--------|------|
| Ctrl+Alt+T | 翻译选中的文本（从剪贴板） |
| Ctrl+Alt+O | OCR 截图翻译 |
| Ctrl+Alt+F | 显示/隐藏悬浮窗 |

#### OCR 截图翻译

1. 按 Ctrl+Alt+O
2. 使用 grim + slurp 选择屏幕区域（Wayland）
3. 或选择区域后从图片识别文字
4. 自动翻译识别结果

---

## 常见问题

### Q: 如何更新到最新版本？

```bash
cd ~/linux-translate
git pull origin master
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### Q: 如何备份历史记录？

```bash
# 历史记录位置
~/.local/share/linux-translate/history.db

# 备份
cp ~/.local/share/linux-translate/history.db ~/backup/

# 导出为 CSV（在应用的历史记录对话框中）
```

### Q: 如何重置配置？

```bash
rm ~/.config/linux-translate/config.json
```

### Q: 支持哪些翻译引擎？

- **Google Translate**: 无需配置，可能需翻墙
- **百度翻译**: 需要 API 密钥
- **有道翻译**: 需要 API 密钥

### Q: 支持哪些语音引擎？

- **在线 TTS**: 使用 Google TTS（需要网络）
- **离线 TTS**: 使用 pyttsx3（需要安装 espeak-ng）

---

## 卸载

### 源码安装卸载

```bash
# 删除项目目录
rm -rf ~/linux-translate

# 删除配置文件
rm -rf ~/.config/linux-translate

# 删除数据文件
rm -rf ~/.local/share/linux-translate

# 删除启动脚本
rm ~/.local/bin/linux-translate

# 删除桌面文件
rm ~/.local/share/applications/linux-translate.desktop

# 刷新桌面缓存
update-desktop-database ~/.local/share/applications/
```

### 系统级安装卸载

```bash
sudo rm -rf /opt/linux-translate
sudo rm /usr/local/bin/linux-translate
```

---

## 故障报告

如果遇到问题，请收集以下信息：

1. **操作系统版本**: `cat /etc/os-release`
2. **Python 版本**: `python3 --version`
3. **桌面环境**: `echo $XDG_CURRENT_DESKTOP`
4. **显示服务器**: `echo $XDG_SESSION_TYPE`
5. **错误日志**: `cat ~/linux-translate/debug.log`

提交 Issue 至: https://github.com/peterlishihu/linux-translate/issues

---

## 许可证

MIT License - 详见 LICENSE 文件
