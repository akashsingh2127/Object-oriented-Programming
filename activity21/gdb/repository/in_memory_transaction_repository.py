# gdb/repository/in_memory_transaction_repository.py
from datetime import datetime
from typing import List
import threading
from gdb.domain.transaction import Transaction
from gdb.domain.transaction_type import TransactionType
from gdb.repository.transaction_repository import TransactionRepository

class InMemoryTransactionRepository(TransactionRepository):
    """
    Thread-safe in-memory repository for Transaction audit ledgers.
    """

    # ============================================================
    # 📝 STEP 9: Initialize Transaction Storage & Lock
    #
    # INSTRUCTIONS:
    #   1. Initialize an empty list self._transactions: List[Transaction] = []
    #   2. Initialize a re-entrant lock self._lock = threading.RLock()
    # ============================================================
    def __init__(self):
        self._transactions: List[Transaction] = []
        self._lock = threading.RLock()

    # ============================================================
    # 📝 STEP 10: Implement save(transaction)
    #
    # INSTRUCTIONS:
    #   1. Acquire self._lock.
    #   2. Append transaction to self._transactions.
    # ============================================================
    def save(self, transaction: Transaction) -> None:
        with self._lock:
            self._transactions.append(transaction)

    # ============================================================
    # 📝 STEP 11: Implement find_by_account(account_number)
    #
    # INSTRUCTIONS:
    #   1. Acquire self._lock.
    #   2. Return all transactions where account_number matches primary, from, or to account.
    # ============================================================
    def find_by_account(self, account_number: int) -> List[Transaction]:
        with self._lock:
            return [
                t for t in self._transactions
                if t.get_account_number() == account_number
                or t.get_from_account() == account_number
                or t.get_to_account() == account_number
            ]

    # ============================================================
    # 📝 STEP 12: Implement find_all()
    #
    # INSTRUCTIONS:
    #   1. Acquire self._lock.
    #   2. Return a shallow copy list of all stored transactions.
    # ============================================================
    def find_all(self) -> List[Transaction]:
        with self._lock:
            return list(self._transactions)

    def clear(self) -> None:
        with self._lock:
            self._transactions.clear()

    # ============================================================
    # 📝 STEP 14: Implement transfer(from_account, to_account, amount)
    #
    # INSTRUCTIONS:
    #   1. Record transfer transaction between accounts.
    # ============================================================
    def transfer(self, from_account_number: int, to_account_number: int, amount: float) -> None:
        with self._lock:
            txn = Transaction(
                transaction_id=Transaction.generate_id(),
                timestamp=datetime.now(),
                account_number=from_account_number,
                transaction_type=TransactionType.TRANSFER,
                amount=amount,
                balance_after=0.0,
                status="SUCCESS",
                description=f"Transfer from {from_account_number} to {to_account_number}",
                from_account=from_account_number,
                to_account=to_account_number,
            )
            self._transactions.append(txn)
