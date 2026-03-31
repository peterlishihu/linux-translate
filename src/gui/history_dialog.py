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

    record_selected = pyqtSignal(str)

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
