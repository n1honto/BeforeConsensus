# api/v1/endpoints/blockchain.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List, Dict, Any
import json

from ..schemas.blockchain import (
    BlockchainInfoSchema,
    TransactionHistorySchema,
    SmartContractSchema
)
from ...handlers.blockchain_handler import BlockchainHandler
from ...dependencies import get_blockchain_handler

router = APIRouter(prefix="/blockchain", tags=["Blockchain"])

@router.get("/info", response_model=BlockchainInfoSchema)
async def get_blockchain_info(
    handler: BlockchainHandler = Depends(get_blockchain_handler)
):
    """Get blockchain information"""
    return handler.get_blockchain_info()

@router.get("/transactions", response_model=TransactionHistorySchema)
async def get_transaction_history(
    bank_id: Optional[str] = None,
    handler: BlockchainHandler = Depends(get_blockchain_handler)
):
    """Get transaction history"""
    return {"transactions": handler.get_transaction_history(bank_id)}

@router.post("/contracts", response_model=SmartContractSchema)
async def create_smart_contract(
    contract_data: Dict,
    handler: BlockchainHandler = Depends(get_blockchain_handler)
):
    """Create new smart contract"""
    try:
        return handler.create_smart_contract(
            contract_id=contract_data["contract_id"],
            creator=contract_data["creator"],
            storage=contract_data.get("storage", {})
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/contracts/{contract_id}/execute")
async def execute_smart_contract(
    contract_id: str,
    execution_data: Dict,
    handler: BlockchainHandler = Depends(get_blockchain_handler)
):
    """Execute smart contract method"""
    try:
        return handler.execute_smart_contract(
            contract_id=contract_id,
            method=execution_data["method"],
            args=execution_data.get("args", []),
            caller=execution_data.get("caller", "API_USER")
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
