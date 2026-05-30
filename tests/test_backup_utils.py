import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("TOMTOM_API_KEY", "test-key")

import backup_utils


class TestBackupUtils(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db_file = Path(self.tmp) / "traffic.db"
        self.backup_dir = Path(self.tmp) / "backups"

        # Tworzymy fałszywą bazę danych
        self.db_file.write_bytes(b"SQLITE3_FAKE_DB")

        # Przekierowujemy ścieżki w module na katalog tymczasowy
        self._patch_db = patch.object(backup_utils, "__builtins__", backup_utils.__builtins__)
        patch("backup_utils.DB_PATH", self.db_file).start()
        patch("backup_utils.BACKUP_DIR", self.backup_dir).start()

    def tearDown(self):
        patch.stopall()
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_backup_creates_file(self):
        """perform_backup tworzy plik w katalogu backupów."""
        backup_utils.perform_backup()
        backups = list(self.backup_dir.glob("*.db"))
        self.assertEqual(len(backups), 1)

    def test_backup_filename_pattern(self):
        """Nazwa pliku zawiera prefiks 'traffic_backup_'."""
        backup_utils.perform_backup()
        name = list(self.backup_dir.glob("*.db"))[0].name
        self.assertTrue(name.startswith("traffic_backup_"))

    def test_backup_content_matches(self):
        """Skopiowany plik ma tę samą zawartość co oryginał."""
        backup_utils.perform_backup()
        backup_file = list(self.backup_dir.glob("*.db"))[0]
        self.assertEqual(backup_file.read_bytes(), self.db_file.read_bytes())

    def test_retention_removes_oldest(self):
        """Po przekroczeniu limitu najstarszy backup zostaje usunięty."""
        limit = backup_utils.BACKUP_RETENTION_LIMIT
        self.backup_dir.mkdir(exist_ok=True)

        # Tworzymy (limit) plików ręcznie
        for i in range(limit):
            f = self.backup_dir / f"traffic_backup_2024-01-0{i+1}_00-00.db"
            f.write_bytes(b"old")
            # Ustawiamy mtime żeby kolejność była jednoznaczna
            os.utime(f, (i, i))

        backup_utils.perform_backup()

        remaining = sorted(self.backup_dir.glob("*.db"), key=os.path.getmtime)
        self.assertEqual(len(remaining), limit)
        # Najstarszy (mtime=0) powinien być usunięty
        self.assertFalse((self.backup_dir / "traffic_backup_2024-01-01_00-00.db").exists())

    def test_no_backup_when_db_missing(self):
        """Brak pliku bazy → brak backupu, brak wyjątku."""
        self.db_file.unlink()
        backup_utils.perform_backup()
        self.assertFalse(self.backup_dir.exists() and any(self.backup_dir.glob("*.db")))


if __name__ == "__main__":
    unittest.main()
