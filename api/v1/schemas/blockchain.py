# api/v1/schemas/blockchain.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class BlockchainTransactionSchema(BaseModel):
    sender: str = Field(..., example="CENTRAL_BANK")
    recipient: str = Field(..., example="BANK001")
    amount: float = Field(..., example=1000000000.0)
    transaction_type: str = Field(..., example="emission")
    timestamp: float = Field(..., example=1634567890.123)
    metadata: Dict = Field(..., example={"purpose": "liquidity_provision"})
    hash: str = Field(..., example="a1b2c3d4e5f6...")

class BlockSchema(BaseModel):
    index: int = Field(..., example=1)
    transactions: List[BlockchainTransactionSchema] = Field(..., example=[])
    timestamp: float = Field(..., example=1634567890.123)
    previous_hash: str = Field(..., example="000...000")
    nonce: int = Field(..., example=12345)
    hash: str = Field(..., example="a1b2c3d4e5f6...")

class BlockchainInfoSchema(BaseModel):
    length: int = Field(..., example=5)
    last_block: Optional[BlockSchema] = None
    pending_transactions: int = Field(..., example=2)
    difficulty: int = Field(..., example=2)
    valid: bool = Field(..., example=True)

class SmartContractSchema(BaseModel):
    contract_id: str = Field(..., example="CONTRACT20231115123456")
    code_hash: str = Field(..., example="a1b2c3...")
    creator: str = Field(..., example="SYSTEM")
    storage: Dict = Field(..., example={"balances": {"BANK001": 1000}})
    events: List[Dict] = Field(..., example=[{
        "type": "transfer",
        "from": "BANK001",
        "to": "BANK002",
        "amount": 100
    }])

class TransactionHistorySchema(BaseModel):
    transactions: List[Dict] = Field(..., example=[{
        "block_index": 1,
        "transaction_hash": "a1b2c3...",
        "sender": "CENTRAL_BANK",
        "recipient": "BANK001",
        "amount": 1000000000.0,
        "transaction_type": "emission",
        "timestamp": 1634567890.123
    }])
