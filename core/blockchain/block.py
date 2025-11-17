# core/blockchain/block.py
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any

class Block:
    def __init__(self, index: int, transactions: List[Dict], timestamp: float,
                 previous_hash: str, nonce: int = 0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self) -> str:
        """Вычисляет хэш блока"""
        block_string = json.dumps({
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует блок в словарь"""
        return {
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.compute_hash()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Block':
        """Создает блок из словаря"""
        return cls(
            index=data["index"],
            transactions=data["transactions"],
            timestamp=data["timestamp"],
            previous_hash=data["previous_hash"],
            nonce=data.get("nonce", 0)
        )
