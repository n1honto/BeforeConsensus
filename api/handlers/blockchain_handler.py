# api/handlers/blockchain_handler.py
from typing import Dict, List, Any
import json

class BlockchainHandler:
    def __init__(self, central_bank):
        self.central_bank = central_bank

    def get_blockchain_info(self) -> Dict:
        """Returns blockchain information"""
        return self.central_bank.get_blockchain_info()

    def get_transaction_history(self, bank_id: str = None) -> List[Dict]:
        """Returns transaction history"""
        return self.central_bank.get_transaction_history(bank_id)

    def create_smart_contract(self, contract_id: str, creator: str, storage: Dict) -> Dict:
        """Creates new smart contract"""
        from core.blockchain.smart_contract import SmartContract

        contract = SmartContract(
            contract_id=contract_id,
            code="",  # В реальной системе здесь был бы код контракта
            creator=creator
        )
        contract.storage = storage
        self.central_bank.smart_contracts[contract_id] = contract

        return contract.to_dict()

    def execute_smart_contract(self, contract_id: str, method: str,
                               args: List[Any], caller: str) -> Dict:
        """Executes smart contract method"""
        if contract_id not in self.central_bank.smart_contracts:
            raise Exception("Contract not found")

        contract = self.central_bank.smart_contracts[contract_id]
        result = contract.execute(method, args, {
            "timestamp": datetime.now().timestamp(),
            "caller": caller,
            "contract": contract_id
        })

        return {
            "contract_id": contract_id,
            "method": method,
            "result": result,
            "events": contract.events[-1] if contract.events else None
        }
