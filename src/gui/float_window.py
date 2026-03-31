from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QApplication
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QFont


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
