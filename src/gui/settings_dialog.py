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
