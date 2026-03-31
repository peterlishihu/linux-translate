from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QApplication
)
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt6.QtGui import QFont


class ResultPopup(QWidget):
    """Popup window to display translation results near mouse"""

    copy_requested = pyqtSignal(str)
    speak_requested = pyqtSignal(str, str)

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
        # Main container
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

        # Header
        header_layout = QHBoxLayout()
        self.source_label = QLabel("原文")
        self.source_label.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))
        header_layout.addWidget(self.source_label)
        header_layout.addStretch()

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

        # Source text
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

        # Pin button
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
        display_source = source[:100] + "..." if len(source) > 100 else source
        self.source_text.setText(display_source)
        self.result_text.setPlainText(result)
        self._current_lang = lang

        if pos is None:
            from PyQt6.QtGui import QCursor
            pos = QCursor.pos()

        # Adjust position to keep on screen
        screen = QApplication.primaryScreen().geometry()
        x = min(pos.x(), screen.width() - 400)
        y = min(pos.y() + 20, screen.height() - 200)

        self.move(x, y)
        self.show()

        if not self.pin_btn.isChecked():
            self._close_timer.start(self._auto_close_delay)

    def _on_copy(self):
        text = self.result_text.toPlainText()
        if text:
            self.copy_requested.emit(text)
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
        if not self.pin_btn.isChecked():
            self._close_timer.stop()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.pin_btn.isChecked() and self.isVisible():
            self._close_timer.start(self._auto_close_delay)
        super().leaveEvent(event)
