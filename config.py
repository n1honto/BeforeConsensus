# config.py
from datetime import timedelta

# Настройки оффлайн-кошельков
WALLET_CONFIG = {
    'expiry_days': 14,  # Срок действия оффлайн-кошелька (дней)
    'max_balance': 1000000,  # Максимальный баланс оффлайн-кошелька
    'min_transaction': 0.01,  # Минимальная сумма транзакции
}

# Настройки HotStuff консенсуса
HOTSTUFF_CONFIG = {
    'node_count': 4,  # Количество узлов в сети
    'timeout': 5,  # Таймаут для ответа узлов (секунды)
    'block_size_limit': 1000,  # Максимальное количество транзакций в блоке
    'rotation_interval': 10,  # Интервал ротации лидеров (в блоках)
}

# Пути к файлам
FILE_PATHS = {
    'transaction_hashes': 'data/transaction_hashes.txt',
    'block_info': 'data/block_info.txt',
    'blockchain_info': 'data/blockchain_info.txt',
    'logs': 'logs/app.log'
}

# Настройки логирования
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': FILE_PATHS['logs'],
    'max_size': 10 * 1024 * 1024,  # 10 MB
    'backup_count': 5
}

# Настройки интерфейса
GUI_CONFIG = {
    'window_title': 'Цифровой рубль - Симулятор с HotStuff консенсусом',
    'min_window_size': (1000, 700),
    'default_font_size': 12,
}
