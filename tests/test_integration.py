# tests/test_integration.py
import sys
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from core.central_bank import CentralBank
from core.blockchain.blockchain import Blockchain

def test_blockchain_integration():
    """Тест интеграции блокчейна"""
    cb = CentralBank()

    # Регистрируем банк
    result = cb.register_bank({
        "name": "Test Bank",
        "bic": "044525225"
    })
    assert result["status"] == "success"

    # Проверяем информацию о блокчейне
    info = cb.blockchain.get_blockchain_info()
    assert info["length"] == 2  # Genesis block + registration transaction
    assert info["pending_transactions"] == 0

def test_emission_processing():
    """Тест обработки эмиссии"""
    cb = CentralBank()

    # Регистрируем банк
    bank_result = cb.register_bank({
        "name": "Test Bank",
        "bic": "044525225"
    })
    bank_id = bank_result["bank_id"]

    # Активируем банк
    cb.banks[bank_id]["status"] = "active"

    # Выполняем эмиссию
    emission_result = cb.process_emission(bank_id, 1000000000, "test")
    assert emission_result["status"] == "success"
    assert cb.banks[bank_id]["balance"] == 1000000000
