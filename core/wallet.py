from datetime import datetime, timedelta
import uuid

class Wallet:
    def __init__(self, owner_id: str):
        self.wallet_id = str(uuid.uuid4())
        self.owner_id = owner_id
        self.open_time = datetime.now()
        self.expiry_time = self.open_time + timedelta(days=14)
        self.balance = 0.0
        self.pending_transactions = []
        self.transaction_history = []
        self.is_active = True

    def add_funds(self, amount: float) -> bool:
        """Добавляет средства на баланс кошелька"""
        if amount <= 0:
            return False
        self.balance += amount
        self.transaction_history.append({
            'type': 'deposit',
            'amount': amount,
            'timestamp': datetime.now(),
            'status': 'completed'
        })
        return True

    def withdraw_funds(self, amount: float) -> bool:
        """Списывает средства с баланса кошелька"""
        if amount <= 0 or self.balance < amount:
            return False
        self.balance -= amount
        self.transaction_history.append({
            'type': 'withdrawal',
            'amount': amount,
            'timestamp': datetime.now(),
            'status': 'completed'
        })
        return True

    def add_offline_transaction(self, transaction) -> bool:
        """Добавляет оффлайн-транзакцию в очередь ожидания"""
        if not self.is_active:
            return False

        self.pending_transactions.append(transaction)
        self.transaction_history.append({
            'type': 'offline_transaction',
            'transaction_id': transaction.id,
            'amount': transaction.amount,
            'timestamp': datetime.now(),
            'status': 'pending'
        })
        return True

    def sync_transactions(self, central_bank) -> bool:
        """Синхронизирует ожидающие транзакции с центральным банком"""
        if not self.pending_transactions:
            return False

        for transaction in self.pending_transactions:
            # Логика синхронизации с центральным банком
            transaction.status = "processed"
            self.transaction_history.append({
                'type': 'sync',
                'transaction_id': transaction.id,
                'timestamp': datetime.now(),
                'status': 'completed'
            })

        self.pending_transactions = []
        return True

    def check_expiry(self) -> bool:
        """Проверяет, не истек ли срок действия кошелька"""
        if datetime.now() > self.expiry_time:
            self.is_active = False
            return False
        return True

    def get_balance(self) -> float:
        """Возвращает текущий баланс кошелька"""
        return self.balance

    def get_transaction_history(self) -> list:
        """Возвращает историю транзакций"""
        return self.transaction_history
