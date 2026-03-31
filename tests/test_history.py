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
