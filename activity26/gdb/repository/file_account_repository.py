import os
import threading
from typing import List, Optional
from gdb.domain.iaccount import IAccount
from gdb.repository.account_repository import AccountRepository
from gdb.file.atomic_file_writer import AtomicFileWriter
from gdb.file.csv_mapper import CsvMapper
from gdb.file.backup_manager import BackupManager

class FileAccountRepository(AccountRepository):
    """
    CSV-backed account repository providing crash-proof persistence using AtomicFileWriter
    and retention backups via BackupManager.
    """

    def __init__(self, file_path: str = "data/accounts.csv", backup_enabled: bool = True, max_backups: int = 5):
        self.file_path = file_path
        self.backup_enabled = backup_enabled
        self.max_backups = max_backups
        self._lock = threading.RLock()
        self._ensure_file_initialized()

    def _ensure_file_initialized(self) -> None:
        with self._lock:
            if not os.path.exists(self.file_path):
                AtomicFileWriter.write(self.file_path, [CsvMapper.ACCOUNT_HEADER])

    def _read_all(self) -> List[IAccount]:
        if not os.path.exists(self.file_path):
            return []
        accounts = []
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                acc = CsvMapper.from_csv_account(line)
                if acc is not None:
                    accounts.append(acc)
        return accounts

    def _write_all(self, accounts: List[IAccount]) -> None:
        if self.backup_enabled and os.path.exists(self.file_path):
            BackupManager.backup(self.file_path, self.max_backups)
        lines = [CsvMapper.ACCOUNT_HEADER]
        for acc in accounts:
            lines.append(CsvMapper.to_csv_account(acc))
        AtomicFileWriter.write(self.file_path, lines)

    def save(self, account: IAccount) -> None:
        # 📝 STEP 4: Save account to CSV
        with self._lock:
            accounts = self._read_all()
            updated = False
            for i, acc in enumerate(accounts):
                if acc.get_account_number() == account.get_account_number():
                    accounts[i] = account
                    updated = True
                    break
            if not updated:
                accounts.append(account)
            self._write_all(accounts)

    def find_by_id(self, account_number: int) -> Optional[IAccount]:
        # 📝 STEP 4: Find account by ID from CSV
        with self._lock:
            accounts = self._read_all()
            for acc in accounts:
                if acc.get_account_number() == account_number:
                    return acc
            return None

    def find_all(self) -> List[IAccount]:
        # 📝 STEP 4: Retrieve all accounts from CSV
        with self._lock:
            return self._read_all()

    def update(self, account: IAccount) -> None:
        # 📝 STEP 4: Update account in CSV
        with self._lock:
            accounts = self._read_all()
            found = False
            for i, acc in enumerate(accounts):
                if acc.get_account_number() == account.get_account_number():
                    accounts[i] = account
                    found = True
                    break
            if found:
                self._write_all(accounts)

    def delete(self, account_number: int) -> None:
        # 📝 STEP 4: Delete account from CSV
        with self._lock:
            accounts = self._read_all()
            filtered = [acc for acc in accounts if acc.get_account_number() != account_number]
            if len(filtered) != len(accounts):
                self._write_all(filtered)

    def exists(self, account_number: int) -> bool:
        # 📝 STEP 4: Check if account exists in CSV
        with self._lock:
            return self.find_by_id(account_number) is not None

    def next_account_number(self) -> int:
        # 📝 STEP 4: Generate next ID from CSV
        with self._lock:
            accounts = self._read_all()
            if not accounts:
                return 1001
            return max(acc.get_account_number() for acc in accounts) + 1
