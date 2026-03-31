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
