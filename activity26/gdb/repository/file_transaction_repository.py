import os
import threading
from datetime import datetime
from typing import List
from gdb.domain.transaction import Transaction
from gdb.domain.transaction_type import TransactionType
from gdb.repository.transaction_repository import TransactionRepository
from gdb.repository.file_account_repository import FileAccountRepository
from gdb.file.atomic_file_writer import AtomicFileWriter
from gdb.file.csv_mapper import CsvMapper
from gdb.file.backup_manager import BackupManager

class FileTransactionRepository(TransactionRepository):
    """
    CSV-backed transaction repository providing crash-proof persistence using AtomicFileWriter
    and atomic funds transfers.
    """

    def __init__(self, file_path: str = "data/transactions.csv", backup_enabled: bool = True, max_backups: int = 5):
        self.file_path = file_path
        self.backup_enabled = backup_enabled
        self.max_backups = max_backups
        self._lock = threading.RLock()
        self._ensure_file_initialized()

    def _ensure_file_initialized(self) -> None:
        with self._lock:
            if not os.path.exists(self.file_path):
                AtomicFileWriter.write(self.file_path, [CsvMapper.TRANSACTION_HEADER])

    def _read_all(self) -> List[Transaction]:
        if not os.path.exists(self.file_path):
            return []
        txns = []
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                txn = CsvMapper.from_csv_transaction(line)
                if txn is not None:
                    txns.append(txn)
        return txns

    def _write_all(self, txns: List[Transaction]) -> None:
        if self.backup_enabled and os.path.exists(self.file_path):
            BackupManager.backup(self.file_path, self.max_backups)
        lines = [CsvMapper.TRANSACTION_HEADER]
        for t in txns:
            lines.append(CsvMapper.to_csv_transaction(t))
        AtomicFileWriter.write(self.file_path, lines)

    def save(self, transaction: Transaction) -> None:
        # 📝 STEP 5: Save transaction
        with self._lock:
            txns = self._read_all()
            txns.append(transaction)
            self._write_all(txns)

    def find_by_account(self, account_number: int) -> List[Transaction]:
        # 📝 STEP 5: Find transactions by account
        with self._lock:
            txns = self._read_all()
            return [
                t for t in txns
                if t.get_account_number() == account_number
                or t.get_from_account() == account_number
                or t.get_to_account() == account_number
            ]

    def find_all(self) -> List[Transaction]:
        # 📝 STEP 5: Retrieve all transactions
        with self._lock:
            return self._read_all()

    def clear(self) -> None:
        # 📝 STEP 5: Clear transactions
        with self._lock:
            if self.backup_enabled and os.path.exists(self.file_path):
                BackupManager.backup(self.file_path, self.max_backups)
            AtomicFileWriter.write(self.file_path, [CsvMapper.TRANSACTION_HEADER])

    def transfer(self, from_account_number: int, to_account_number: int, amount: float) -> None:
        # 📝 STEP 5: Perform atomic file transfer
        with self._lock:
            dir_name = os.path.dirname(os.path.abspath(self.file_path))
            acc_file = os.path.join(dir_name, "accounts.csv")
            acc_repo = FileAccountRepository(acc_file, backup_enabled=self.backup_enabled, max_backups=self.max_backups)

            src = acc_repo.find_by_id(from_account_number)
            dst = acc_repo.find_by_id(to_account_number)

            if src is None or dst is None:
                raise ValueError(f"Account not found: src={src}, dst={dst}")

            # Debit source and credit destination
            src._balance -= amount
            dst._balance += amount

            # Persist updated accounts
            acc_repo.update(src)
            acc_repo.update(dst)

            # Record transfer transaction
            txn = Transaction(
                transaction_id=Transaction.generate_id(),
                timestamp=datetime.now(),
                account_number=from_account_number,
                transaction_type=TransactionType.TRANSFER,
                amount=amount,
                balance_after=src.get_balance(),
                status="SUCCESS",
                description=f"Transfer of Rs. {amount} to #{to_account_number}",
                from_account=from_account_number,
                to_account=to_account_number,
            )
            self.save(txn)
