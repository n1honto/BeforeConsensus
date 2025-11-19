# gui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import random
import time
from pathlib import Path
import logging
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
plt.rcParams['font.family'] = 'DejaVu Sans'

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)

from core.central_bank import CentralBank

class DigitalRubleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Система Цифрового Рубля - Центральный Банк РФ")
        self.geometry("1200x800")

        # Инициализация центрального банка
        self.central_bank = CentralBank()

        # Инициализация атрибутов интерфейса
        self.users_data_tree = None
        self.transactions_data_tree = None
        self.offline_tx_tree = None
        self.smart_contracts_tree = None
        self.tx_hashes_tree = None
        self.blocks_tree = None
        self.ledger_tree = None
        self.metrics_tree = None
        self.fo_notifications_tree = None
        self.cb_emission_requests_tree = None
        self.cb_transactions_tree = None
        self.cb_pending_transactions_tree = None

        # Для визуализации
        self.consensus_canvas = None
        self.ledger_canvas = None
        self.metrics_figures = []

        # Списки для хранения транзакций
        self.user_transactions = []
        self.pending_transactions = []

        # Настройка стилей
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=('Arial', 10))
        self.style.configure("TButton", font=('Arial', 10))
        self.style.configure("Treeview", font=('Arial', 10))

        # Создание меню
        self._create_menu()

        # Создание основных вкладок
        self._create_notebook()

        # Обновление данных после инициализации интерфейса
        self.after(100, self.refresh_all_data)

    def show_about(self):
        """Показывает информацию о программе"""
        about_text = """Система Цифрового Рубля v1.0
Центральный Банк Российской Федерации

Функциональные возможности:
1. Управление пользователями (физ.лица, юр.лица, гос.учреждения)
2. Создание и управление банками (ФО)
3. Различные типы транзакций:
   - Онлайн транзакции между пользователями
   - Оффлайн транзакции с ограниченным сроком действия
   - Смарт-контракты с автоматическим исполнением
4. Эмиссия цифровых рублей через ФО
5. Мониторинг и обработка транзакций Центральным Банком
6. Визуализация блокчейна и консенсуса
7. Анализ метрик системы

© 2023 Банк России"""
        messagebox.showinfo("О программе", about_text)

    def _create_menu(self):
        """Создает главное меню"""
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Выход", command=self.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="О программе", command=self.show_about)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        self.config(menu=menubar)

    def _create_notebook(self):
        """Создает вкладки с интерфейсом"""
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 1. Вкладка "Управление"
        management_frame = ttk.Frame(notebook)
        self._create_management_tab(management_frame)
        notebook.add(management_frame, text="Управление")

        # 2. Вкладка "Пользователь"
        user_frame = ttk.Frame(notebook)
        self._create_user_tab(user_frame)
        notebook.add(user_frame, text="Пользователь")

        # 3. Вкладка "Финансовая организация"
        fo_frame = ttk.Frame(notebook)
        self._create_fo_tab(fo_frame)
        notebook.add(fo_frame, text="Финансовая организация")

        # 4. Вкладка "Центральный банк"
        cb_frame = ttk.Frame(notebook)
        self._create_cb_tab(cb_frame)
        notebook.add(cb_frame, text="Центральный банк")

        # 5. Вкладка "Данные о пользователях"
        users_data_frame = ttk.Frame(notebook)
        self._create_users_data_tab(users_data_frame)
        notebook.add(users_data_frame, text="Данные о пользователях")

        # 6. Вкладка "Данные о транзакциях"
        transactions_data_frame = ttk.Frame(notebook)
        self._create_transactions_data_tab(transactions_data_frame)
        notebook.add(transactions_data_frame, text="Данные о транзакциях")

        # 7. Вкладка "Оффлайн-транзакции"
        offline_tx_frame = ttk.Frame(notebook)
        self._create_offline_tx_tab(offline_tx_frame)
        notebook.add(offline_tx_frame, text="Оффлайн-транзакции")

        # 8. Вкладка "Смарт-контракты"
        smart_contracts_frame = ttk.Frame(notebook)
        self._create_smart_contracts_tab(smart_contracts_frame)
        notebook.add(smart_contracts_frame, text="Смарт-контракты")

        # 9. Вкладка "Консенсус"
        consensus_frame = ttk.Frame(notebook)
        self._create_consensus_tab(consensus_frame)
        notebook.add(consensus_frame, text="Консенсус")

        # 10. Вкладка "Распределенный реестр"
        ledger_frame = ttk.Frame(notebook)
        self._create_ledger_tab(ledger_frame)
        notebook.add(ledger_frame, text="Распределенный реестр")

        # 11. Вкладка "Анализ метрик"
        metrics_frame = ttk.Frame(notebook)
        self._create_metrics_tab(metrics_frame)
        notebook.add(metrics_frame, text="Анализ метрик")

    def _create_management_tab(self, frame):
        """Создает интерфейс для управления системой"""
        # Фрейм для создания пользователей
        users_frame = ttk.LabelFrame(frame, text="Создание пользователей")
        users_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(users_frame, text="Количество:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.user_count_entry = ttk.Entry(users_frame, width=10)
        self.user_count_entry.grid(row=0, column=1, padx=5, pady=5)

        self.user_type_var = tk.StringVar(value="physical")
        ttk.Radiobutton(users_frame, text="Физические лица", variable=self.user_type_var, value="physical").grid(row=0, column=2, padx=5, pady=5)
        ttk.Radiobutton(users_frame, text="Юридические лица", variable=self.user_type_var, value="legal").grid(row=0, column=3, padx=5, pady=5)
        ttk.Radiobutton(users_frame, text="Гос. учреждения", variable=self.user_type_var, value="government").grid(row=0, column=4, padx=5, pady=5)

        ttk.Button(users_frame, text="Создать пользователей",
                  command=self.create_users).grid(row=0, column=5, padx=5, pady=5)

        # Фрейм для создания банков
        banks_frame = ttk.LabelFrame(frame, text="Создание банков (ФО)")
        banks_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(banks_frame, text="Количество:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.bank_count_entry = ttk.Entry(banks_frame, width=10)
        self.bank_count_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(banks_frame, text="Создать банки",
                  command=self.create_banks).grid(row=0, column=2, padx=5, pady=5)

    def _create_user_tab(self, frame):
        """Создает интерфейс для пользователей"""
        # Фрейм для создания кошелька
        wallet_frame = ttk.LabelFrame(frame, text="Цифровой кошелек")
        wallet_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(wallet_frame, text="ID пользователя:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.wallet_user_entry = ttk.Combobox(wallet_frame, width=20, state="readonly")
        self.wallet_user_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(wallet_frame, text="Создать цифровой кошелек",
                  command=self.create_digital_wallet).grid(row=0, column=2, padx=5, pady=5)

        # Фрейм для обмена денег
        exchange_frame = ttk.LabelFrame(frame, text="Обмен безналичных на цифровые")
        exchange_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(exchange_frame, text="ID пользователя:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.exchange_user_entry = ttk.Combobox(exchange_frame, width=20, state="readonly")
        self.exchange_user_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(exchange_frame, text="Сумма:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.exchange_amount_entry = ttk.Entry(exchange_frame, width=10)
        self.exchange_amount_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(exchange_frame, text="Обменять",
                  command=self.exchange_money).grid(row=0, column=4, padx=5, pady=5)

        # Фрейм для онлайн транзакций
        online_tx_frame = ttk.LabelFrame(frame, text="Онлайн транзакции")
        online_tx_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(online_tx_frame, text="Отправитель:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.online_sender_entry = ttk.Combobox(online_tx_frame, width=15, state="readonly")
        self.online_sender_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(online_tx_frame, text="Получатель:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.online_receiver_entry = ttk.Combobox(online_tx_frame, width=15, state="readonly")
        self.online_receiver_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(online_tx_frame, text="Сумма:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.online_amount_entry = ttk.Entry(online_tx_frame, width=10)
        self.online_amount_entry.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(online_tx_frame, text="Отправить",
                  command=self.process_online_transaction).grid(row=0, column=6, padx=5, pady=5)

    def _create_fo_tab(self, frame):
        """Создает интерфейс для финансовых организаций"""
        # Фрейм для запросов на эмиссию
        emission_frame = ttk.LabelFrame(frame, text="Запрос на эмиссию")
        emission_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(emission_frame, text="Сумма эмиссии:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.fo_emission_amount_entry = ttk.Entry(emission_frame, width=15)
        self.fo_emission_amount_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(emission_frame, text="ID банка:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.fo_bank_entry = ttk.Combobox(emission_frame, width=15, state="readonly")
        self.fo_bank_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(emission_frame, text="Запросить эмиссию",
                  command=self.request_emission).grid(row=0, column=4, padx=5, pady=5)

        # Фрейм для уведомлений о транзакциях
        notifications_frame = ttk.LabelFrame(frame, text="Уведомления о транзакциях")
        notifications_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("type", "sender", "receiver", "amount", "timestamp", "status")
        self.fo_notifications_tree = ttk.Treeview(notifications_frame, columns=columns, show="headings")

        for col in columns:
            self.fo_notifications_tree.heading(col, text=col.capitalize())
            self.fo_notifications_tree.column(col, width=100, anchor=tk.W)

        self.fo_notifications_tree.column("amount", width=80, anchor=tk.E)
        self.fo_notifications_tree.pack(fill=tk.BOTH, expand=True)

    def _create_cb_tab(self, frame):
        """Создает интерфейс для Центрального Банка"""
        # Фрейм для транзакций в очереди
        pending_frame = ttk.LabelFrame(frame, text="Транзакции в очереди на отработку")
        pending_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("tx_id", "sender", "receiver", "amount", "type", "timestamp", "tx_hash")
        self.cb_pending_transactions_tree = ttk.Treeview(pending_frame, columns=columns, show="headings")

        for col in columns:
            self.cb_pending_transactions_tree.heading(col, text=col.replace("_", " ").title())
            self.cb_pending_transactions_tree.column(col, width=100, anchor=tk.W)

        self.cb_pending_transactions_tree.column("amount", width=80, anchor=tk.E)
        self.cb_pending_transactions_tree.pack(fill=tk.BOTH, expand=True)

        ttk.Button(pending_frame, text="Отработать транзакции",
                  command=self.process_pending_transactions).pack(pady=5)

        # Фрейм для обработки запросов на эмиссию
        emission_frame = ttk.LabelFrame(frame, text="Запросы на эмиссию")
        emission_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("fo_id", "cash_balance", "amount", "timestamp", "status")
        self.cb_emission_requests_tree = ttk.Treeview(emission_frame, columns=columns, show="headings")

        for col in columns:
            self.cb_emission_requests_tree.heading(col, text=col.replace("_", " ").title())
            self.cb_emission_requests_tree.column(col, width=120, anchor=tk.W)

        self.cb_emission_requests_tree.column("cash_balance", width=120, anchor=tk.E)
        self.cb_emission_requests_tree.column("amount", width=100, anchor=tk.E)
        self.cb_emission_requests_tree.pack(fill=tk.BOTH, expand=True)

        # Кнопки для обработки запросов
        button_frame = ttk.Frame(emission_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="Одобрить выбранный запрос",
                  command=self.approve_emission_request).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(button_frame, text="Отклонить выбранный запрос",
                  command=self.reject_emission_request).pack(side=tk.LEFT, padx=5, pady=5)

        # Фрейм для мониторинга транзакций
        monitoring_frame = ttk.LabelFrame(frame, text="Мониторинг транзакций")
        monitoring_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("tx_id", "sender", "receiver", "amount", "type", "timestamp", "tx_hash", "status")
        self.cb_transactions_tree = ttk.Treeview(monitoring_frame, columns=columns, show="headings")

        for col in columns:
            self.cb_transactions_tree.heading(col, text=col.replace("_", " ").title())
            self.cb_transactions_tree.column(col, width=100, anchor=tk.W)

        self.cb_transactions_tree.column("amount", width=80, anchor=tk.E)
        self.cb_transactions_tree.pack(fill=tk.BOTH, expand=True)

    def _create_users_data_tab(self, frame):
        """Создает интерфейс для данных о пользователях"""
        users_frame = ttk.LabelFrame(frame, text="Данные о пользователях")
        users_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("user_id", "user_type", "cash_balance", "digital_wallet_status",
                  "offline_wallet_status", "digital_balance", "offline_balance",
                  "offline_activation_time", "offline_deactivation_time")

        self.users_data_tree = ttk.Treeview(users_frame, columns=columns, show="headings")

        self.users_data_tree.heading("user_id", text="ID пользователя")
        self.users_data_tree.heading("user_type", text="Тип пользователя")
        self.users_data_tree.heading("cash_balance", text="Баланс безналичных (₽)")
        self.users_data_tree.heading("digital_wallet_status", text="Статус цифрового кошелька")
        self.users_data_tree.heading("offline_wallet_status", text="Статус оффлайн кошелька")
        self.users_data_tree.heading("digital_balance", text="Баланс цифрового кошелька (₽)")
        self.users_data_tree.heading("offline_balance", text="Баланс оффлайн кошелька (₽)")
        self.users_data_tree.heading("offline_activation_time", text="Время активации")
        self.users_data_tree.heading("offline_deactivation_time", text="Время деактивации")

        for col in columns:
            self.users_data_tree.column(col, width=120, anchor=tk.W)

        self.users_data_tree.column("cash_balance", width=120, anchor=tk.E)
        self.users_data_tree.column("digital_balance", width=120, anchor=tk.E)
        self.users_data_tree.column("offline_balance", width=120, anchor=tk.E)

        self.users_data_tree.pack(fill=tk.BOTH, expand=True)

        ttk.Button(users_frame, text="Обновить",
                  command=self.refresh_users_data).pack(pady=5)

    def _create_transactions_data_tab(self, frame):
        """Создает интерфейс для данных о транзакциях"""
        transactions_frame = ttk.LabelFrame(frame, text="Данные о транзакциях")
        transactions_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("tx_id", "sender", "receiver", "amount", "type", "timestamp", "tx_hash")
        self.transactions_data_tree = ttk.Treeview(transactions_frame, columns=columns, show="headings")

        self.transactions_data_tree.heading("tx_id", text="ID транзакции")
        self.transactions_data_tree.heading("sender", text="Отправитель")
        self.transactions_data_tree.heading("receiver", text="Получатель")
        self.transactions_data_tree.heading("amount", text="Сумма (₽)")
        self.transactions_data_tree.heading("type", text="Тип")
        self.transactions_data_tree.heading("timestamp", text="Время")
        self.transactions_data_tree.heading("tx_hash", text="Хеш транзакции")

        for col in columns:
            self.transactions_data_tree.column(col, width=120, anchor=tk.W)

        self.transactions_data_tree.column("amount", width=100, anchor=tk.E)
        self.transactions_data_tree.pack(fill=tk.BOTH, expand=True)

        ttk.Button(transactions_frame, text="Обновить",
                  command=self.refresh_transactions_data).pack(pady=5)

    def _create_offline_tx_tab(self, frame):
        """Создает интерфейс для оффлайн-транзакций"""
        offline_tx_frame = ttk.LabelFrame(frame, text="Оффлайн-транзакции")
        offline_tx_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("tx_id", "sender", "receiver", "amount", "bank", "timestamp", "status")
        self.offline_tx_tree = ttk.Treeview(offline_tx_frame, columns=columns, show="headings")

        self.offline_tx_tree.heading("tx_id", text="ID транзакции")
        self.offline_tx_tree.heading("sender", text="Отправитель")
        self.offline_tx_tree.heading("receiver", text="Получатель")
        self.offline_tx_tree.heading("amount", text="Сумма (₽)")
        self.offline_tx_tree.heading("bank", text="Банк")
        self.offline_tx_tree.heading("timestamp", text="Время")
        self.offline_tx_tree.heading("status", text="Статус")

        for col in columns:
            self.offline_tx_tree.column(col, width=120, anchor=tk.W)

        self.offline_tx_tree.column("amount", width=100, anchor=tk.E)
        self.offline_tx_tree.pack(fill=tk.BOTH, expand=True)

        ttk.Button(offline_tx_frame, text="Обновить",
                  command=self.refresh_offline_tx_data).pack(pady=5)

    def _create_smart_contracts_tab(self, frame):
        """Создает интерфейс для смарт-контрактов"""
        sc_frame = ttk.LabelFrame(frame, text="Смарт-контракты")
        sc_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("contract_id", "sender", "receiver", "amount", "bank", "functionality",
                  "execution_time", "required_amount", "status")
        self.smart_contracts_tree = ttk.Treeview(sc_frame, columns=columns, show="headings")

        self.smart_contracts_tree.heading("contract_id", text="ID контракта")
        self.smart_contracts_tree.heading("sender", text="Отправитель")
        self.smart_contracts_tree.heading("receiver", text="Получатель")
        self.smart_contracts_tree.heading("amount", text="Сумма (₽)")
        self.smart_contracts_tree.heading("bank", text="Банк")
        self.smart_contracts_tree.heading("functionality", text="Функционал")
        self.smart_contracts_tree.heading("execution_time", text="Время исполнения")
        self.smart_contracts_tree.heading("required_amount", text="Требуемая сумма (₽)")
        self.smart_contracts_tree.heading("status", text="Статус")

        for col in columns:
            self.smart_contracts_tree.column(col, width=100, anchor=tk.W)

        self.smart_contracts_tree.column("amount", width=80, anchor=tk.E)
        self.smart_contracts_tree.column("required_amount", width=100, anchor=tk.E)
        self.smart_contracts_tree.pack(fill=tk.BOTH, expand=True)

        ttk.Button(sc_frame, text="Обновить",
                  command=self.refresh_smart_contracts_data).pack(pady=5)

    def _create_consensus_tab(self, frame):
        """Создает интерфейс для консенсуса"""
        # Визуализация консенсуса
        visualization_frame = ttk.LabelFrame(frame, text="Визуализация консенсуса")
        visualization_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.consensus_canvas = tk.Canvas(visualization_frame, bg="white", width=800, height=400)
        self.consensus_canvas.pack(fill=tk.BOTH, expand=True)

        # Кнопка запуска симуляции
        ttk.Button(frame, text="Запустить симуляцию консенсуса",
                  command=self.start_consensus_simulation).pack(pady=5)

        # Фрейм для хешей транзакций
        tx_hashes_frame = ttk.LabelFrame(frame, text="Хеши транзакций")
        tx_hashes_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("tx_hash", "timestamp", "status")
        self.tx_hashes_tree = ttk.Treeview(tx_hashes_frame, columns=columns, show="headings")

        for col in columns:
            self.tx_hashes_tree.heading(col, text=col.replace("_", " ").title())
            self.tx_hashes_tree.column(col, width=150, anchor=tk.W)

        self.tx_hashes_tree.pack(fill=tk.BOTH, expand=True)

        # Фрейм для сформированных блоков
        blocks_frame = ttk.LabelFrame(frame, text="Сформированные блоки")
        blocks_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("block_index", "block_hash", "parent_hash", "tx_count", "mining_time")
        self.blocks_tree = ttk.Treeview(blocks_frame, columns=columns, show="headings")

        for col in columns:
            self.blocks_tree.heading(col, text=col.replace("_", " ").title())
            self.blocks_tree.column(col, width=120, anchor=tk.W)

        self.blocks_tree.pack(fill=tk.BOTH, expand=True)

    def _create_ledger_tab(self, frame):
        """Создает интерфейс для распределенного реестра"""
        # Визуализация блокчейна
        visualization_frame = ttk.LabelFrame(frame, text="Визуализация блокчейна")
        visualization_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.ledger_canvas = tk.Canvas(visualization_frame, bg="white", width=800, height=400)
        self.ledger_canvas.pack(fill=tk.BOTH, expand=True)

        # Кнопка запуска симуляции
        ttk.Button(frame, text="Запустить симуляцию распределенного реестра",
                  command=self.start_ledger_simulation).pack(pady=5)

        # Фрейм для детальной информации о блоках
        blocks_frame = ttk.LabelFrame(frame, text="Детальная информация о блоках")
        blocks_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("index", "hash", "parent_hash", "tx_count", "timestamp")
        self.ledger_tree = ttk.Treeview(blocks_frame, columns=columns, show="headings")

        for col in columns:
            self.ledger_tree.heading(col, text=col.replace("_", " ").title())
            self.ledger_tree.column(col, width=120, anchor=tk.W)

        self.ledger_tree.pack(fill=tk.BOTH, expand=True)

    def _create_metrics_tab(self, frame):
        """Создает интерфейс для анализа метрик"""
        # Фрейм для таблицы метрик
        table_frame = ttk.LabelFrame(frame, text="Таблица метрик")
        table_frame.pack(fill=tk.X, padx=5, pady=5)

        columns = ("metric", "value", "trend")
        self.metrics_tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.metrics_tree.heading("metric", text="Метрика")
        self.metrics_tree.heading("value", text="Значение")
        self.metrics_tree.heading("trend", text="Тренд")

        for col in columns:
            self.metrics_tree.column(col, width=120, anchor=tk.W)

        self.metrics_tree.pack(fill=tk.BOTH, expand=True)

        # Фрейм для графиков
        charts_frame = ttk.LabelFrame(frame, text="Графики метрик")
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Создаем три отдельных графика
        self.metrics_figures = []
        for i in range(3):
            fig = plt.Figure(figsize=(6, 2), dpi=100)
            ax = fig.add_subplot(111)
            canvas = FigureCanvasTkAgg(fig, master=charts_frame)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=5)
            self.metrics_figures.append((fig, ax, canvas))

        ttk.Button(frame, text="Обновить",
                  command=self.refresh_metrics_data).pack(pady=5)

    def _draw_consensus_visualization(self):
        """Отрисовывает визуализацию консенсуса"""
        if not hasattr(self, 'consensus_canvas') or not self.consensus_canvas:
            return

        self.consensus_canvas.delete("all")

        # Параметры визуализации
        node_radius = 30
        spacing = 120
        start_x = 100
        start_y = 200

        # Рисуем узлы консенсуса
        nodes = ["Лидер", "Узел 1", "Узел 2", "Узел 3", "Узел 4"]
        colors = ["red", "blue", "green", "orange", "purple"]

        for i, node in enumerate(nodes):
            x = start_x + i * spacing
            y = start_y

            # Рисуем узел
            self.consensus_canvas.create_oval(x, y, x + node_radius, y + node_radius,
                                           fill=colors[i], outline="black")

            # Пишем название узла
            self.consensus_canvas.create_text(x + node_radius/2, y + node_radius + 15, text=node)

            # Рисуем линии связи
            if i > 0:
                self.consensus_canvas.create_line(start_x + node_radius/2, start_y + node_radius/2,
                                               x + node_radius/2, y + node_radius/2,
                                               dash=(3, 3))

        # Рисуем транзакции
        tx_x = start_x + 2 * spacing
        tx_y = 50
        self.consensus_canvas.create_rectangle(tx_x, tx_y, tx_x + 100, tx_y + 30, fill="lightgray")
        self.consensus_canvas.create_text(tx_x + 50, tx_y + 15, text="Транзакция")

        # Рисуем стрелки от транзакции к узлам
        for i in range(len(nodes)):
            self.consensus_canvas.create_line(tx_x + 50, tx_y + 30,
                                           start_x + i * spacing + node_radius/2,
                                           start_y, arrow=tk.LAST)

        # Рисуем процесс подтверждения
        self.consensus_canvas.create_text(400, 350, text="Процесс достижения консенсуса", font=('Arial', 10, 'bold'))
        self.consensus_canvas.create_rectangle(300, 370, 500, 390, fill="lightyellow")
        self.consensus_canvas.create_text(400, 380, text="Подтверждение транзакции узлами")

    def _draw_blockchain_visualization(self):
        """Отрисовывает визуализацию блокчейна"""
        if not hasattr(self, 'ledger_canvas') or not self.ledger_canvas:
            return

        self.ledger_canvas.delete("all")

        # Параметры визуализации
        block_width = 120
        block_height = 80
        start_x = 50
        start_y = 100
        spacing = 150

        # Рисуем цепочку блоков
        for i, block in enumerate(self.central_bank.blockchain.chain[-5:]):
            x = start_x + i * spacing
            y = start_y

            # Рисуем блок
            self.ledger_canvas.create_rectangle(x, y, x + block_width, y + block_height,
                                               fill="lightblue", outline="black", width=2)

            # Информация о блоке
            self.ledger_canvas.create_text(x + block_width/2, y + 20,
                                          text=f"Блок {block.index}", font=('Arial', 10, 'bold'))
            self.ledger_canvas.create_text(x + block_width/2, y + 40,
                                          text=f"Хеш: {block.compute_hash()[:12]}...", font=('Arial', 8))
            self.ledger_canvas.create_text(x + block_width/2, y + 60,
                                          text=f"Транзакций: {len(block.transactions)}", font=('Arial', 8))

            # Предыдущий хеш
            if block.index > 0:
                self.ledger_canvas.create_text(x + block_width/2, y - 10,
                                              text=f"Prev: {block.previous_hash[:12]}...",
                                              font=('Arial', 8, 'italic'))

            # Стрелка к следующему блоку
            if i < len(self.central_bank.blockchain.chain[-5:]) - 1:
                next_x = start_x + (i + 1) * spacing
                self.ledger_canvas.create_line(x + block_width, y + block_height/2,
                                             next_x, y + block_height/2,
                                             arrow=tk.LAST, width=2)

    def _update_metrics_chart(self):
        """Обновляет графики метрик"""
        if not self.metrics_figures:
            return

        # Генерация тестовых данных
        x = [i for i in range(1, 11)]

        # Данные для первого графика (Количество транзакций)
        tx_count = [random.randint(1, 20) for _ in range(10)]
        fig, ax, canvas = self.metrics_figures[0]
        ax.clear()
        ax.plot(x, tx_count, marker='o', color='blue')
        ax.set_title("Количество транзакций")
        ax.set_xlabel("Время (мин)")
        ax.set_ylabel("Количество")
        canvas.draw()

        # Данные для второго графика (Время создания блока)
        block_time = [random.uniform(0.5, 2.0) for _ in range(10)]
        fig, ax, canvas = self.metrics_figures[1]
        ax.clear()
        ax.plot(x, block_time, marker='s', color='green')
        ax.set_title("Время создания блока (с)")
        ax.set_xlabel("Время (мин)")
        ax.set_ylabel("Время (с)")
        canvas.draw()

        # Данные для третьего графика (Время записи в реестр)
        ledger_time = [random.uniform(0.2, 1.0) for _ in range(10)]
        fig, ax, canvas = self.metrics_figures[2]
        ax.clear()
        ax.plot(x, ledger_time, marker='^', color='red')
        ax.set_title("Время записи в реестр (с)")
        ax.set_xlabel("Время (мин)")
        ax.set_ylabel("Время (с)")
        canvas.draw()

    def _update_comboboxes(self):
        """Обновляет выпадающие списки с ID пользователей и банков"""
        user_ids = list(self.central_bank.users.keys())
        for combobox in [self.wallet_user_entry, self.exchange_user_entry,
                        self.online_sender_entry, self.online_receiver_entry,
                        self.offline_sender_entry, self.offline_receiver_entry,
                        self.sc_sender_entry, self.sc_receiver_entry]:
            if combobox:
                combobox['values'] = user_ids
                if user_ids:
                    combobox.current(0)

        bank_ids = list(self.central_bank.banks.keys())
        if hasattr(self, 'fo_bank_entry'):
            self.fo_bank_entry['values'] = bank_ids
            if bank_ids:
                self.fo_bank_entry.current(0)

    def refresh_users_data(self):
        """Обновляет данные о пользователях"""
        if not hasattr(self, 'users_data_tree'):
            return

        for item in self.users_data_tree.get_children():
            self.users_data_tree.delete(item)

        for user_id, user in self.central_bank.users.items():
            activation_time = user["offline_activation_time"] or "Не активирован"
            deactivation_time = user["offline_deactivation_time"] or "Не активирован"

            self.users_data_tree.insert("", tk.END, values=(
                user_id,
                user["user_type"],
                f"{user['cash_balance']:,.2f} ₽",
                user["digital_wallet_status"],
                user["offline_wallet_status"],
                f"{user['digital_balance']:,.2f} ₽",
                f"{user['offline_balance']:,.2f} ₽",
                activation_time,
                deactivation_time
            ))

    def refresh_transactions_data(self):
        """Обновляет данные о транзакциях"""
        if not hasattr(self, 'transactions_data_tree'):
            return

        for item in self.transactions_data_tree.get_children():
            self.transactions_data_tree.delete(item)

        # Отображаем все транзакции пользователя (кроме эмиссии)
        for tx in self.central_bank.transactions:
            if tx["type"] != "эмиссия":
                self.transactions_data_tree.insert("", tk.END, values=(
                    tx.get("tx_id", "N/A"),
                    tx["sender"],
                    tx["receiver"],
                    f"{tx['amount']:,.2f} ₽",
                    tx.get("type", "неизвестно"),
                    tx["timestamp"],
                    tx.get("tx_hash", "N/A")
                ))

    def refresh_offline_tx_data(self):
        """Обновляет данные об оффлайн транзакциях"""
        if not hasattr(self, 'offline_tx_tree'):
            return

        for item in self.offline_tx_tree.get_children():
            self.offline_tx_tree.delete(item)

        for tx in self.central_bank.offline_transactions:
            self.offline_tx_tree.insert("", tk.END, values=(
                tx.get("tx_id", "N/A"),
                tx["sender"],
                tx["receiver"],
                f"{tx['amount']:,.2f} ₽",
                "BANK0001",
                tx["timestamp"],
                tx["status"]
            ))

    def refresh_smart_contracts_data(self):
        """Обновляет данные о смарт-контрактах"""
        if not hasattr(self, 'smart_contracts_tree'):
            return

        for item in self.smart_contracts_tree.get_children():
            self.smart_contracts_tree.delete(item)

        for contract_id, contract in self.central_bank.smart_contracts.items():
            self.smart_contracts_tree.insert("", tk.END, values=(
                contract_id,
                contract["sender"],
                contract["receiver"],
                f"{contract['amount']:,.2f} ₽",
                "BANK0001",
                contract["functionality"],
                contract["execution_time"],
                f"{contract['required_amount']:,.2f} ₽",
                contract["status"]
            ))

    def refresh_consensus_data(self):
        """Обновляет данные о консенсусе"""
        if not hasattr(self, 'tx_hashes_tree') or not hasattr(self, 'blocks_tree'):
            return

        for item in self.tx_hashes_tree.get_children():
            self.tx_hashes_tree.delete(item)

        for item in self.blocks_tree.get_children():
            self.blocks_tree.delete(item)

        # Тестовые данные для демонстрации
        test_hashes = [
            ("tx" + ''.join(random.choices('0123456789abcdef', k=16)), datetime.now().isoformat(), "ПОДТВЕРЖДЕНО"),
            ("tx" + ''.join(random.choices('0123456789abcdef', k=16)), datetime.now().isoformat(), "ОЖИДАНИЕ")
        ]

        for tx in test_hashes:
            self.tx_hashes_tree.insert("", tk.END, values=tx)

        # Данные о блоках из блокчейна
        for i, block in enumerate(self.central_bank.blockchain.chain[-5:]):
            mining_time = f"{random.uniform(0.5, 2.0):.2f}s"
            parent_hash = block.previous_hash[:12] + "..." if block.index > 0 else "000..."
            self.blocks_tree.insert("", tk.END, values=(
                block.index,
                block.compute_hash()[:12] + "...",
                parent_hash,
                len(block.transactions),
                mining_time
            ))

        # Обновляем визуализацию консенсуса
        self._draw_consensus_visualization()

    def refresh_ledger_data(self):
        """Обновляет данные о распределенном реестре"""
        if not hasattr(self, 'ledger_tree'):
            return

        for item in self.ledger_tree.get_children():
            self.ledger_tree.delete(item)

        # Данные о блоках из блокчейна
        for block in self.central_bank.blockchain.chain[-5:]:
            parent_hash = block.previous_hash[:12] + "..." if block.index > 0 else "000..."
            self.ledger_tree.insert("", tk.END, values=(
                block.index,
                block.compute_hash()[:12] + "...",
                parent_hash,
                len(block.transactions),
                datetime.fromtimestamp(block.timestamp).strftime('%H:%M:%S')
            ))

        # Обновляем визуализацию блокчейна
        self._draw_blockchain_visualization()

    def refresh_cb_emission_requests(self):
        """Обновляет запросы на эмиссию"""
        if not hasattr(self, 'cb_emission_requests_tree'):
            return

        for item in self.cb_emission_requests_tree.get_children():
            self.cb_emission_requests_tree.delete(item)

        for request in self.central_bank.emission_requests:
            self.cb_emission_requests_tree.insert("", tk.END, values=(
                request["fo_id"],
                f"{request['cash_balance']:,.2f} ₽",
                f"{request['amount']:,.2f} ₽",
                request["timestamp"],
                request["status"]
            ))

    def refresh_cb_pending_transactions(self):
        """Обновляет транзакции в очереди"""
        if not hasattr(self, 'cb_pending_transactions_tree'):
            return

        for item in self.cb_pending_transactions_tree.get_children():
            self.cb_pending_transactions_tree.delete(item)

        for tx in self.pending_transactions:
            self.cb_pending_transactions_tree.insert("", tk.END, values=(
                tx["tx_id"],
                tx["sender"],
                tx["receiver"],
                f"{tx['amount']:,.2f} ₽",
                tx["type"],
                tx["timestamp"],
                tx["tx_hash"]
            ))

    def refresh_cb_transactions(self):
        """Обновляет транзакции для ЦБ"""
        if not hasattr(self, 'cb_transactions_tree'):
            return

        for item in self.cb_transactions_tree.get_children():
            self.cb_transactions_tree.delete(item)

        for tx in self.central_bank.transactions:
            if tx.get("status") == "Выполнено":
                self.cb_transactions_tree.insert("", tk.END, values=(
                    tx.get("tx_id", "N/A"),
                    tx["sender"],
                    tx["receiver"],
                    f"{tx['amount']:,.2f} ₽",
                    tx.get("type", "неизвестно"),
                    tx["timestamp"],
                    tx.get("tx_hash", "N/A"),
                    tx.get("status", "неизвестно")
                ))

    def refresh_metrics_data(self):
        """Обновляет данные о метриках"""
        if not hasattr(self, 'metrics_tree'):
            return

        for item in self.metrics_tree.get_children():
            self.metrics_tree.delete(item)

        test_metrics = [
            ("Количество транзакций", f"{len(self.central_bank.transactions)}", "↑"),
            ("Время формирования транзакции", f"{random.uniform(0.1, 0.5):.2f}с", "→"),
            ("Время создания блока", f"{random.uniform(0.5, 2.0):.2f}с", "→"),
            ("Время записи блока в реестр", f"{random.uniform(0.2, 1.0):.2f}с", "→")
        ]

        for metric in test_metrics:
            self.metrics_tree.insert("", tk.END, values=metric)

        # Обновляем графики метрик
        self._update_metrics_chart()

    def refresh_all_data(self):
        """Обновляет все данные в интерфейсе"""
        self._update_comboboxes()

        if hasattr(self, 'users_data_tree'):
            self.refresh_users_data()
        if hasattr(self, 'transactions_data_tree'):
            self.refresh_transactions_data()
        if hasattr(self, 'cb_emission_requests_tree'):
            self.refresh_cb_emission_requests()
        if hasattr(self, 'cb_pending_transactions_tree'):
            self.refresh_cb_pending_transactions()
        if hasattr(self, 'cb_transactions_tree'):
            self.refresh_cb_transactions()
        if hasattr(self, 'metrics_tree'):
            self.refresh_metrics_data()
        if hasattr(self, 'tx_hashes_tree') and hasattr(self, 'blocks_tree'):
            self.refresh_consensus_data()
        if hasattr(self, 'ledger_tree'):
            self.refresh_ledger_data()

    def create_users(self):
        """Создает заданное количество пользователей"""
        try:
            count = int(self.user_count_entry.get())
            user_type = self.user_type_var.get()

            for i in range(count):
                if user_type == "physical":
                    user_id = f"FL{len(self.central_bank.users) + 1:06d}"
                    user_type_text = "Физическое лицо"
                elif user_type == "legal":
                    user_id = f"UL{len(self.central_bank.users) + 1:06d}"
                    user_type_text = "Юридическое лицо"
                else:  # government
                    user_id = f"GOV{len(self.central_bank.users) + 1:06d}"
                    user_type_text = "Гос. учреждение"

                user = {
                    "user_id": user_id,
                    "user_type": user_type_text,
                    "cash_balance": 10000,
                    "digital_wallet_status": "Закрыт",
                    "offline_wallet_status": "Закрыт",
                    "digital_balance": 0,
                    "offline_balance": 0,
                    "offline_activation_time": None,
                    "offline_deactivation_time": None
                }
                self.central_bank.users[user_id] = user

            self._update_comboboxes()
            messagebox.showinfo("Успех", f"Создано {count} пользователей типа {user_type_text}")
            self.refresh_all_data()
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректное количество пользователей")

    def create_banks(self):
        """Создает заданное количество банков"""
        try:
            count = int(self.bank_count_entry.get())

            for i in range(count):
                bank_id = f"BANK{len(self.central_bank.banks) + 1:04d}"
                bank = {
                    "bank_id": bank_id,
                    "name": f"Банк {len(self.central_bank.banks) + 1}",
                    "bic": f"044525{random.randint(1000, 9999)}",
                    "status": "активен",
                    "balance": 0.0,
                    "cash_balance": 10000000,
                    "registration_date": datetime.now().isoformat()
                }
                self.central_bank.banks[bank_id] = bank

            self._update_comboboxes()
            messagebox.showinfo("Успех", f"Создано {count} банков")
            self.refresh_all_data()
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректное количество банков")

    def create_digital_wallet(self):
        """Создает цифровой кошелек для пользователя"""
        user_id = self.wallet_user_entry.get()
        if not user_id:
            messagebox.showerror("Ошибка", "Выберите пользователя")
            return

        if user_id not in self.central_bank.users:
            messagebox.showerror("Ошибка", "Пользователь не найден")
            return

        user = self.central_bank.users[user_id]
        if user["digital_wallet_status"] == "Открыт":
            messagebox.showinfo("Информация", "Цифровой кошелек уже открыт")
            return

        user["digital_wallet_status"] = "Открыт"
        messagebox.showinfo("Успех", f"Цифровой кошелек пользователя {user_id} открыт")
        self.refresh_all_data()

    def exchange_money(self):
        """Обмен безналичных денег на цифровые"""
        try:
            user_id = self.exchange_user_entry.get()
            amount = float(self.exchange_amount_entry.get())

            if not user_id:
                messagebox.showerror("Ошибка", "Выберите пользователя")
                return

            if user_id not in self.central_bank.users:
                messagebox.showerror("Ошибка", "Пользователь не найден")
                return

            user = self.central_bank.users[user_id]
            if user["digital_wallet_status"] != "Открыт":
                messagebox.showerror("Ошибка", "Цифровой кошелек не открыт")
                return

            if user["cash_balance"] < amount:
                messagebox.showerror("Ошибка", "Недостаточно средств на безналичном счете")
                return

            tx_id = f"TX{len(self.central_bank.transactions) + 1:06d}"
            tx_hash = f"hash{random.randint(100000, 999999)}"

            user["cash_balance"] -= amount
            user["digital_balance"] += amount

            transaction = {
                "tx_id": tx_id,
                "sender": user_id,
                "receiver": user_id,
                "amount": amount,
                "type": "обмен",
                "timestamp": datetime.now().isoformat(),
                "tx_hash": tx_hash,
                "status": "Выполнено"
            }

            self.central_bank.transactions.append(transaction)
            self.user_transactions.append(transaction)

            messagebox.showinfo("Успех", f"Обмен выполнен. Новый баланс цифрового кошелька: {user['digital_balance']:,.2f} ₽")
            self.refresh_all_data()
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректная сумма")

    def process_online_transaction(self):
        """Обрабатывает онлайн транзакцию"""
        try:
            sender = self.online_sender_entry.get()
            receiver = self.online_receiver_entry.get()
            amount = float(self.online_amount_entry.get())

            if not sender or not receiver:
                messagebox.showerror("Ошибка", "Выберите отправителя и получателя")
                return

            if sender not in self.central_bank.users or receiver not in self.central_bank.users:
                messagebox.showerror("Ошибка", "Отправитель или получатель не найдены")
                return

            sender_user = self.central_bank.users[sender]
            receiver_user = self.central_bank.users[receiver]

            if sender_user["digital_balance"] < amount:
                messagebox.showerror("Ошибка", "Недостаточно средств на цифровом кошельке отправителя")
                return

            tx_id = f"TX{len(self.central_bank.transactions) + 1:06d}"
            tx_hash = f"hash{random.randint(100000, 999999)}"

            # Выполняем транзакцию
            sender_user["digital_balance"] -= amount
            receiver_user["digital_balance"] += amount

            # Создаем транзакцию
            transaction = {
                "tx_id": tx_id,
                "sender": sender,
                "receiver": receiver,
                "amount": amount,
                "type": "онлайн",
                "timestamp": datetime.now().isoformat(),
                "tx_hash": tx_hash,
                "status": "В очереди"
            }

            # Добавляем в очередь транзакций
            self.pending_transactions.append(transaction)
            self.central_bank.transactions.append(transaction)

            messagebox.showinfo("Успех", f"Онлайн транзакция {tx_id} создана и добавлена в очередь")
            self.refresh_all_data()
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректная сумма")

    def open_offline_wallet(self):
        """Открывает оффлайн кошелек"""
        user_id = self.offline_user_entry.get()
        if not user_id:
            messagebox.showerror("Ошибка", "Выберите пользователя")
            return

        if user_id not in self.central_bank.users:
            messagebox.showerror("Ошибка", "Пользователь не найден")
            return

        user = self.central_bank.users[user_id]
        if user["offline_wallet_status"] == "Открыт":
            messagebox.showinfo("Информация", "Оффлайн кошелек уже открыт")
            return

        user["offline_wallet_status"] = "Открыт"
        user["offline_activation_time"] = datetime.now().isoformat()
        user["offline_deactivation_time"] = (datetime.now() + timedelta(days=14)).isoformat()

        messagebox.showinfo("Успех", f"Оффлайн кошелек открыт до {user['offline_deactivation_time']}")
        self.refresh_all_data()

    def topup_offline_wallet(self):
        """Пополняет оффлайн кошелек"""
        try:
            user_id = self.offline_user_entry.get()
            amount = float(self.offline_topup_entry.get())

            if not user_id:
                messagebox.showerror("Ошибка", "Выберите пользователя")
                return

            if user_id not in self.central_bank.users:
                messagebox.showerror("Ошибка", "Пользователь не найден")
                return

            user = self.central_bank.users[user_id]
            if user["offline_wallet_status"] != "Открыт":
                messagebox.showerror("Ошибка", "Оффлайн кошелек не открыт")
                return

            if user["digital_balance"] < amount:
                messagebox.showerror("Ошибка", "Недостаточно средств на цифровом кошельке")
                return

            user["digital_balance"] -= amount
            user["offline_balance"] += amount

            messagebox.showinfo("Успех", f"Оффлайн кошелек пополнен. Новый баланс: {user['offline_balance']:,.2f} ₽")
            self.refresh_all_data()
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректная сумма")

    def create_offline_transaction(self):
        """Создает оффлайн транзакцию"""
        try:
            sender = self.offline_sender_entry.get()
            receiver = self.offline_receiver_entry.get()
            amount = float(self.offline_amount_entry.get())

            if not sender or not receiver:
                messagebox.showerror("Ошибка", "Выберите отправителя и получателя")
                return

            if sender not in self.central_bank.users or receiver not in self.central_bank.users:
                messagebox.showerror("Ошибка", "Отправитель или получатель не найдены")
                return

            sender_user = self.central_bank.users[sender]
            receiver_user = self.central_bank.users[receiver]

            if sender_user["offline_wallet_status"] != "Открыт":
                messagebox.showerror("Ошибка", "Оффлайн кошелек отправителя не открыт")
                return

            if sender_user["offline_balance"] < amount:
                messagebox.showerror("Ошибка", "Недостаточно средств на оффлайн кошельке отправителя")
                return

            tx_id = f"TX{len(self.central_bank.offline_transactions) + 1:06d}"
            tx_hash = f"hash{random.randint(100000, 999999)}"

            offline_tx = {
                "tx_id": tx_id,
                "sender": sender,
                "receiver": receiver,
                "amount": amount,
                "timestamp": datetime.now().isoformat(),
                "tx_hash": tx_hash,
                "status": "ОФФЛАЙН"
            }
            self.central_bank.offline_transactions.append(offline_tx)
            sender_user["offline_balance"] -= amount

            messagebox.showinfo("Успех", "Оффлайн транзакция создана и будет обработана при восстановлении соединения")
            self.refresh_all_data()
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректная сумма")

    def create_smart_contract(self):
        """Создает смарт-контракт"""
        try:
            sender = self.sc_sender_entry.get()
            receiver = self.sc_receiver_entry.get()
            amount = float(self.sc_amount_entry.get())

            if not sender or not receiver:
                messagebox.showerror("Ошибка", "Выберите отправителя и получателя")
                return

            if sender not in self.central_bank.users or receiver not in self.central_bank.users:
                messagebox.showerror("Ошибка", "Отправитель или получатель не найдены")
                return

            sender_user = self.central_bank.users[sender]
            if sender_user["digital_balance"] < amount:
                messagebox.showerror("Ошибка", "Недостаточно средств на цифровом кошельке отправителя")
                return

            contract_id = f"SC{len(self.central_bank.smart_contracts) + 1:06d}"
            tx_hash = f"hash{random.randint(100000, 999999)}"

            smart_contract = {
                "contract_id": contract_id,
                "sender": sender,
                "receiver": receiver,
                "amount": amount,
                "tx_hash": tx_hash,
                "functionality": "Оплата коммунальных платежей",
                "required_amount": 1000,
                "execution_time": (datetime.now() + timedelta(days=1)).isoformat(),
                "status": "СОЗДАН"
            }
            self.central_bank.smart_contracts[contract_id] = smart_contract
            sender_user["digital_balance"] -= amount

            messagebox.showinfo("Успех", f"Смарт-контракт {contract_id} создан")
            self.refresh_all_data()
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные данные")

    def request_emission(self):
        """Запрашивает эмиссию цифровых рублей"""
        try:
            amount = float(self.fo_emission_amount_entry.get())
            bank_id = self.fo_bank_entry.get()

            if not bank_id:
                messagebox.showerror("Ошибка", "Выберите банк")
                return

            if bank_id not in self.central_bank.banks:
                messagebox.showerror("Ошибка", "Банк не найден")
                return

            bank = self.central_bank.banks[bank_id]
            if bank["cash_balance"] < amount:
                messagebox.showerror("Ошибка", "Недостаточно средств на безналичном счете банка")
                return

            emission_request = {
                "fo_id": bank_id,
                "cash_balance": bank["cash_balance"],
                "amount": amount,
                "timestamp": datetime.now().isoformat(),
                "status": "Ожидание"
            }
            self.central_bank.emission_requests.append(emission_request)

            messagebox.showinfo("Успех", "Запрос на эмиссию отправлен в Центральный Банк")
            self.refresh_all_data()
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректная сумма")

    def approve_emission_request(self):
        """Одобряет запрос на эмиссию"""
        selected_item = self.cb_emission_requests_tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите запрос для одобрения")
            return

        request_index = self.cb_emission_requests_tree.index(selected_item)
        request = self.central_bank.emission_requests[request_index]

        if request["status"] != "Ожидание":
            messagebox.showinfo("Информация", "Этот запрос уже обработан")
            return

        bank_id = request["fo_id"]
        amount = request["amount"]

        try:
            bank = self.central_bank.banks[bank_id]
            if bank["cash_balance"] < amount:
                messagebox.showerror("Ошибка", "Недостаточно средств на безналичном счете банка")
                return

            # Обновляем балансы
            bank["cash_balance"] -= amount
            bank["balance"] += amount
            self.central_bank.current_balance -= amount
            self.central_bank.total_emitted += amount

            # Обновляем статус запроса
            request["status"] = "Одобрено"
            self.cb_emission_requests_tree.set(selected_item, "status", "Одобрено")
            self.cb_emission_requests_tree.set(selected_item, "cash_balance",
                                             f"{bank['cash_balance']:,.2f} ₽")

            # Добавляем транзакцию эмиссии
            tx_id = f"TX{len(self.central_bank.transactions) + 1:06d}"
            tx_hash = f"hash{random.randint(100000, 999999)}"
            emission_tx = {
                "tx_id": tx_id,
                "sender": "CENTRAL_BANK",
                "receiver": bank_id,
                "amount": amount,
                "type": "эмиссия",
                "timestamp": datetime.now().isoformat(),
                "tx_hash": tx_hash,
                "status": "Выполнено"
            }
            self.central_bank.transactions.append(emission_tx)

            messagebox.showinfo("Успех", "Запрос на эмиссию одобрен и обработан")
            self.refresh_all_data()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def reject_emission_request(self):
        """Отклоняет запрос на эмиссию"""
        selected_item = self.cb_emission_requests_tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите запрос для отклонения")
            return

        request_index = self.cb_emission_requests_tree.index(selected_item)
        request = self.central_bank.emission_requests[request_index]

        if request["status"] != "Ожидание":
            messagebox.showinfo("Информация", "Этот запрос уже обработан")
            return

        request["status"] = "Отклонено"
        self.cb_emission_requests_tree.set(selected_item, "status", "Отклонено")

        messagebox.showinfo("Успех", "Запрос на эмиссию отклонен")
        self.refresh_all_data()

    def process_pending_transactions(self):
        """Обрабатывает транзакции в очереди"""
        if not self.pending_transactions:
            messagebox.showinfo("Информация", "Нет транзакций в очереди")
            return

        processed_count = 0
        for tx in self.pending_transactions:
            tx["status"] = "Выполнено"
            processed_count += 1

            # Добавляем в мониторинг транзакций ЦБ
            self.cb_transactions_tree.insert("", tk.END, values=(
                tx["tx_id"],
                tx["sender"],
                tx["receiver"],
                f"{tx['amount']:,.2f} ₽",
                tx["type"],
                tx["timestamp"],
                tx["tx_hash"],
                tx["status"]
            ))

        # Очищаем очередь
        self.pending_transactions = []

        messagebox.showinfo("Успех", f"Отработано {processed_count} транзакций")
        self.refresh_all_data()

    def start_consensus_simulation(self):
        """Запускает симуляцию консенсуса"""
        # Очищаем предыдущие данные
        for item in self.tx_hashes_tree.get_children():
            self.tx_hashes_tree.delete(item)
        for item in self.blocks_tree.get_children():
            self.blocks_tree.delete(item)

        # Добавляем тестовые транзакции
        test_tx = [
            ("tx" + ''.join(random.choices('0123456789abcdef', k=16)), datetime.now().isoformat(), "ПОДТВЕРЖДЕНО"),
            ("tx" + ''.join(random.choices('0123456789abcdef', k=16)), datetime.now().isoformat(), "ОЖИДАНИЕ"),
            ("tx" + ''.join(random.choices('0123456789abcdef', k=16)), datetime.now().isoformat(), "ПОДТВЕРЖДЕНО")
        ]

        for tx in test_tx:
            self.tx_hashes_tree.insert("", tk.END, values=tx)

        # Добавляем тестовые блоки
        test_blocks = []
        for i in range(1, 4):
            current_hash = "block" + ''.join(random.choices('0123456789abcdef', k=16))
            parent_hash = "block" + ''.join(random.choices('0123456789abcdef', k=16)) if i > 1 else "000..."
            tx_count = random.randint(1, 5)
            mining_time = f"{random.uniform(0.5, 2.0):.2f}s"

            test_blocks.append((
                i,
                current_hash[:12] + "...",
                parent_hash[:12] + "...",
                tx_count,
                mining_time
            ))

        for block in test_blocks:
            self.blocks_tree.insert("", tk.END, values=block)

        # Обновляем визуализацию консенсуса
        self._draw_consensus_visualization()
        messagebox.showinfo("Информация", "Симуляция консенсуса запущена")

    def start_ledger_simulation(self):
        """Запускает симуляцию распределенного реестра"""
        # Очищаем предыдущие данные
        for item in self.ledger_tree.get_children():
            self.ledger_tree.delete(item)

        # Добавляем тестовые блоки
        test_blocks = []
        for i in range(1, 6):
            prev_hash = "0" * 64 if i == 1 else "block" + ''.join(random.choices('0123456789abcdef', k=16))
            current_hash = "block" + ''.join(random.choices('0123456789abcdef', k=16))
            tx_count = random.randint(1, 5)
            timestamp = datetime.now().strftime('%H:%M:%S')

            test_blocks.append((
                i,
                current_hash[:12] + "...",
                prev_hash[:12] + "...",
                tx_count,
                timestamp
            ))

        for block in test_blocks:
            self.ledger_tree.insert("", tk.END, values=block)

        # Обновляем визуализацию блокчейна
        self._draw_blockchain_visualization()
        messagebox.showinfo("Информация", "Симуляция распределенного реестра запущена")

if __name__ == "__main__":
    app = DigitalRubleApp()
    app.mainloop()
