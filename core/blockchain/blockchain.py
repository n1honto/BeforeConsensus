# core/blockchain/blockchain.py
import hashlib
import json
import time
from typing import List, Dict, Optional, Any
from .block import Block
from .transaction import BlockchainTransaction

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.current_transactions: List[Dict] = []
        self.difficulty = 2  # Количество ведущих нулей в хэше
        self.create_genesis_block()

    def create_genesis_block(self):
        """Создает начальный блок (genesis block)"""
        genesis_block = Block(
            index=0,
            transactions=[],
            timestamp=time.time(),
            previous_hash="0"
        )
        genesis_block.nonce = self.proof_of_work(genesis_block)
        self.chain.append(genesis_block)

    def add_transaction(self, sender: str, recipient: str, amount: float,
                       transaction_type: str, metadata: Dict = None) -> int:
        """Добавляет новую транзакцию"""
        transaction = {
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
            "transaction_type": transaction_type,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        self.current_transactions.append(transaction)
        return len(self.chain)  # Индекс следующего блока

    def mine_block(self) -> Block:
        """Создает новый блок"""
        if not self.current_transactions:
            return None

        last_block = self.last_block

        new_block = Block(
            index=len(self.chain),
            transactions=self.current_transactions.copy(),
            timestamp=time.time(),
            previous_hash=last_block.compute_hash()
        )

        # Добыча блока
        new_block.nonce = self.proof_of_work(new_block)

        self.chain.append(new_block)
        self.current_transactions = []
        return new_block

    def proof_of_work(self, block: Block) -> int:
        """Простой алгоритм proof-of-work"""
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * self.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return block.nonce

    @property
    def last_block(self) -> Block:
        """Возвращает последний блок"""
        return self.chain[-1]

    def get_blockchain_info(self) -> Dict:
        """Возвращает информацию о блокчейне"""
        return {
            "length": len(self.chain),
            "last_block": self.last_block.to_dict() if self.chain else None,
            "pending_transactions": len(self.current_transactions),
            "difficulty": self.difficulty,
            "valid": self.validate_chain()
        }

    def validate_chain(self) -> bool:
        """Проверяет валидность цепочки блоков"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            # Проверка хэша блока
            if current_block.compute_hash() != current_block.compute_hash():
                return False

            # Проверка связи с предыдущим блоком
            if current_block.previous_hash != previous_block.compute_hash():
                return False

        return True
