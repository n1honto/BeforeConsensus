# core/blockchain/transaction.py
import hashlib
import json
from datetime import datetime
from typing import Dict, Any

class BlockchainTransaction:
    def __init__(self, sender: str, recipient: str, amount: float,
                 transaction_type: str, timestamp: float = None,
                 metadata: Dict = None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.transaction_type = transaction_type
        self.timestamp = timestamp or datetime.now().timestamp()
        self.metadata = metadata or {}

    def compute_hash(self) -> str:
        """Вычисляет хэш транзакции"""
        transaction_string = json.dumps({
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "transaction_type": self.transaction_type,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }, sort_keys=True).encode()
        return hashlib.sha256(transaction_string).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует транзакцию в словарь"""
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "transaction_type": self.transaction_type,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "hash": self.compute_hash()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BlockchainTransaction':
        """Создает транзакцию из словаря"""
        return cls(
            sender=data["sender"],
            recipient=data["recipient"],
            amount=data["amount"],
            transaction_type=data["transaction_type"],
            timestamp=data.get("timestamp", datetime.now().timestamp()),
            metadata=data.get("metadata", {})
        )
