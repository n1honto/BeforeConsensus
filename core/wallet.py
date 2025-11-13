# core/wallet.py
from datetime import datetime, timedelta
import uuid
from typing import List, Dict, Optional
from config import WALLET_CONFIG
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/app.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

class Wallet:
    def __init__(self, owner_id: str):
        self.wallet_id = str(uuid.uuid4())
        self.owner_id = owner_id
        self.open_time = datetime.now()
        self.expiry_time = self.open_time + timedelta(days=WALLET_CONFIG['expiry_days'])
        self.balance = 0.0
        self.pending_transactions: List = []
        self.transaction_history: List[Dict] = []
        self.is_active = True
        self.block_hashes: List[str] = []
        self.max_balance = WALLET_CONFIG['max_balance']

    def add_funds(self, amount: float) -> bool:
        """Добавляет средства на баланс кошелька"""
        if not self.is_active:
            logger.warning(f"Попытка пополнения неактивного кошелька {self.wallet_id}")
            return False

        if amount <= 0:
            logger.warning(f"Попытка пополнения кошелька {self.wallet_id} на невалидную сумму {amount}")
            return False

        if self.balance + amount > self.max_balance:
            logger.warning(f"Превышен максимальный баланс кошелька {self.wallet_id}")
            return False

        self.balance += amount
        self.transaction_history.append({
            'type': 'deposit',
            'amount': amount,
            'timestamp': datetime.now(),
            'status': 'completed',
            'block_hash': None
        })
        logger.info(f"Кошелёк {self.wallet_id} пополнен на {amount}. Новый баланс: {self.balance}")
        return True

    def withdraw_funds(self, amount: float) -> bool:
        """Списывает средства с баланса кошелька"""
        if not self.is_active:
            logger.warning(f"Попытка списания с неактивного кошелька {self.wallet_id}")
            return False

        if amount <= 0:
            logger.warning(f"Попытка списания невалидной суммы {amount} с кошелька {self.wallet_id}")
            return False

        if self.balance < amount:
            logger.warning(f"Недостаточно средств в кошельке {self.wallet_id} для списания {amount}")
            return False

        self.balance -= amount
        self.transaction_history.append({
            'type': 'withdrawal',
            'amount': amount,
            'timestamp': datetime.now(),
            'status': 'pending',
            'block_hash': None
        })
        logger.info(f"С кошелька {self.wallet_id} списано {amount}. Новый баланс: {self.balance}")
        return True

    def add_offline_transaction(self, transaction) -> bool:
        """Добавляет оффлайн-транзакцию в очередь ожидания"""
        if not self.is_active:
            logger.warning(f"Попытка добавления транзакции в неактивный кошелёк {self.wallet_id}")
            return False

        if self.balance < transaction.amount:
            logger.warning(f"Недостаточно средств в кошельке {self.wallet_id} для транзакции на {transaction.amount}")
            return False

        self.pending_transactions.append(transaction)
        self.transaction_history.append({
            'type': 'offline_transaction',
            'transaction_id': transaction.id,
            'amount': transaction.amount,
            'timestamp': datetime.now(),
            'status': 'pending',
            'block_hash': None
        })
        logger.info(f"В кошелёк {self.wallet_id} добавлена транзакция {transaction.id} на сумму {transaction.amount}")
        return True

    def confirm_transaction(self, transaction_id: str, block_hash: str) -> bool:
        """Подтверждает транзакцию после включения в блок"""
        for tx in self.transaction_history:
            if tx.get('transaction_id') == transaction_id:
                tx['status'] = 'confirmed'
                tx['block_hash'] = block_hash
                self.block_hashes.append(block_hash)

                if tx['type'] == 'offline_transaction':
                    self.pending_transactions = [
                        t for t in self.pending_transactions if t.id != transaction_id
                    ]

                logger.info(f"Транзакция {transaction_id} в кошельке {self.wallet_id} подтверждена в блоке {block_hash}")
                return True

        logger.warning(f"Транзакция {transaction_id} не найдена в кошельке {self.wallet_id}")
        return False

    def check_expiry(self) -> bool:
        """Проверяет, не истёк ли срок действия кошелька"""
        if datetime.now() > self.expiry_time:
            self.is_active = False
            logger.warning(f"Срок действия кошелька {self.wallet_id} истёк")
            return False
        return True

    def get_balance(self) -> float:
        """Возвращает текущий баланс кошелька"""
        return self.balance

    def get_transaction_history(self) -> list:
        """Возвращает историю транзакций"""
        return self.transaction_history.copy()

    def get_block_hashes(self) -> list:
        """Возвращает хеши блоков, содержащих транзакции кошелька"""
        return self.block_hashes.copy()
