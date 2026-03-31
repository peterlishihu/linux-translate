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
