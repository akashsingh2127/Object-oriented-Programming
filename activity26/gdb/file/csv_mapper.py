from datetime import datetime
from typing import Optional
from gdb.domain.iaccount import IAccount
from gdb.domain.account_factory import AccountFactory
from gdb.domain.transaction import Transaction
from gdb.domain.transaction_type import TransactionType

class CsvMapper:
    """
    CSV serialization and deserialization utility for Account and Transaction domain entities.
    """
    ACCOUNT_HEADER = "account_number,account_holder_name,age,balance,account_type,status,pin,opening_date,overdraft_used,interest_earned"
    TRANSACTION_HEADER = "transaction_id,timestamp,account_number,type,amount,balance_after,status,from_account,to_account,description"

    @staticmethod
    def to_csv_account(account: IAccount) -> str:
        """Serializes an IAccount instance into a CSV string."""
        pin_val = getattr(account, "_pin", None)
        pin_str = str(pin_val) if pin_val is not None else ""
        age = getattr(account, "_age", 18)
        overdraft_used = getattr(account, "_overdraft_used", 0.0)
        interest_earned = getattr(account, "_interest_earned", 0.0)
        status = "Active" if account.is_active() else "Inactive"

        return (
            f"{account.get_account_number()},"
            f"{account.get_account_holder_name()},"
            f"{age},"
            f"{account.get_balance()},"
            f"{account.get_account_type()},"
            f"{status},"
            f"{pin_str},"
            f"{account.get_opening_date()},"
            f"{overdraft_used},"
            f"{interest_earned}"
        )

    @staticmethod
    def from_csv_account(line: str) -> Optional[IAccount]:
        """Deserializes a CSV line into an IAccount domain object."""
        if not line or not line.strip():
            return None
        line = line.strip()
        if line.startswith("account_number") or line.startswith("#"):
            return None

        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 6:
            return None

        acc_num = int(parts[0])
        name = parts[1]
        age = int(parts[2])
        balance = float(parts[3])
        acc_type = parts[4]
        status = parts[5]
        pin = int(parts[6]) if len(parts) > 6 and parts[6] else None
        opening_date = parts[7] if len(parts) > 7 and parts[7] else "2026-08-28"

        try:
            acc = AccountFactory.create_account(acc_type, acc_num, name, age, balance)
        except Exception:
            # Fallback if balance is below initial threshold during reload
            acc = AccountFactory.create_account(acc_type, acc_num, name, age, 50000.0)
            acc._balance = balance

        acc._opening_date = opening_date
        if pin is not None:
            acc.set_pin(pin)
        if status.lower() == "inactive":
            acc.close_account()
        return acc

    @staticmethod
    def to_csv_transaction(txn: Transaction) -> str:
        """Serializes a Transaction instance into a CSV string."""
        ts = txn.get_timestamp().isoformat() if hasattr(txn.get_timestamp(), "isoformat") else str(txn.get_timestamp())
        txn_type = txn.get_type().value if hasattr(txn.get_type(), "value") else str(txn.get_type())
        from_acc = str(txn.get_from_account()) if txn.get_from_account() is not None else ""
        to_acc = str(txn.get_to_account()) if txn.get_to_account() is not None else ""

        return (
            f"{txn.get_id()},"
            f"{ts},"
            f"{txn.get_account_number()},"
            f"{txn_type},"
            f"{txn.get_amount()},"
            f"{txn.get_balance_after()},"
            f"{txn.get_status()},"
            f"{from_acc},"
            f"{to_acc},"
            f"{txn.get_description()}"
        )

    @staticmethod
    def from_csv_transaction(line: str) -> Optional[Transaction]:
        """Deserializes a CSV line into a Transaction domain object."""
        if not line or not line.strip():
            return None
        line = line.strip()
        if line.startswith("transaction_id") or line.startswith("#"):
            return None

        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 7:
            return None

        txn_id = int(parts[0])
        try:
            timestamp = datetime.fromisoformat(parts[1])
        except Exception:
            timestamp = datetime.now()

        acc_num = int(parts[2])
        type_str = parts[3].upper()
        try:
            txn_type = TransactionType[type_str]
        except KeyError:
            txn_type = TransactionType(type_str)

        amount = float(parts[4])
        balance_after = float(parts[5])
        status = parts[6]
        from_acc = int(parts[7]) if len(parts) > 7 and parts[7] else None
        to_acc = int(parts[8]) if len(parts) > 8 and parts[8] else None
        desc = parts[9] if len(parts) > 9 else ""

        return Transaction(
            transaction_id=txn_id,
            timestamp=timestamp,
            account_number=acc_num,
            transaction_type=txn_type,
            amount=amount,
            balance_after=balance_after,
            status=status,
            description=desc,
            from_account=from_acc,
            to_account=to_acc,
        )

    # General aliases
    @staticmethod
    def to_csv(entity) -> str:
        if isinstance(entity, Transaction):
            return CsvMapper.to_csv_transaction(entity)
        return CsvMapper.to_csv_account(entity)

    @staticmethod
    def from_csv(line: str):
        if "DEPOSIT" in line or "WITHDRAW" in line or "TRANSFER" in line:
            return CsvMapper.from_csv_transaction(line)
        return CsvMapper.from_csv_account(line)
