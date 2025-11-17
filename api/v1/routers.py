# api/v1/routers.py
from fastapi import APIRouter
from .endpoints import banks, emissions, blockchain

router = APIRouter(prefix="/v1")

# Подключаем все эндпоинты
router.include_router(banks.router)
router.include_router(emissions.router)
router.include_router(blockchain.router)
