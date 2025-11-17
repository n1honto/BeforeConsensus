# api/dependencies.py
from core.central_bank import CentralBank
from core.blockchain.blockchain import Blockchain
from api.handlers.blockchain_handler import BlockchainHandler

central_bank = CentralBank()

def get_blockchain_handler():
    """Get blockchain handler dependency"""
    return BlockchainHandler(central_bank)
