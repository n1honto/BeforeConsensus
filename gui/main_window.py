# gui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import json
import random
import time
from pathlib import Path
import logging
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
        self.title("Digital Ruble System - Центральный Банк РФ")
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
        self.figure = None
        self.canvas = None
        self.consensus_canvas = None

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

    def _create_menu(self):
        """Создает главное меню"""
        menubar = tk.Menu(self)

        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Выход", command=self.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)

        # Меню "Помощь"
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

        ttk.Button(users_frame, text="Создать пользователей",
                  command=self.create_users).grid(row=0, column=4, padx=5, pady=5)

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
        self.wallet_user_entry = ttk.Combobox(wallet_frame, width=20)
        self.wallet_user_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(wallet_frame, text="Создать цифровой кошелек",
                  command=self.create_digital_wallet).grid(row=0, column=2, padx=5, pady=5)

        # Фрейм для обмена денег
        exchange_frame = ttk.LabelFrame(frame, text="Обмен безналичных на цифровые")
        exchange_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(exchange_frame, text="ID пользователя:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.exchange_user_entry = ttk.Combobox(exchange_frame, width=20)
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
        self.online_sender_entry = ttk.Combobox(online_tx_frame, width=15)
        self.online_sender_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(online_tx_frame, text="Получатель:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.online_receiver_entry = ttk.Combobox(online_tx_frame, width=15)
        self.online_receiver_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(online_tx_frame, text="Сумма:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.online_amount_entry = ttk.Entry(online_tx_frame, width=10)
        self.online_amount_entry.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(online_tx_frame, text="Отправить",
                  command=self.process_online_transaction).grid(row=0, column=6, padx=5, pady=5)

        # Фрейм для оффлайн кошелька
        offline_wallet_frame = ttk.LabelFrame(frame, text="Оффлайн кошелек")
        offline_wallet_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(offline_wallet_frame, text="ID пользователя:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.offline_user_entry = ttk.Combobox(offline_wallet_frame, width=15)
        self.offline_user_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(offline_wallet_frame, text="Открыть оффлайн кошелек",
                  command=self.open_offline_wallet).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(offline_wallet_frame, text="Сумма пополнения:").grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        self.offline_topup_entry = ttk.Entry(offline_wallet_frame, width=10)
        self.offline_topup_entry.grid(row=0, column=4, padx=5, pady=5)

        ttk.Button(offline_wallet_frame, text="Пополнить оффлайн кошелек",
                  command=self.topup_offline_wallet).grid(row=0, column=5, padx=5, pady=5)

        # Фрейм для оффлайн транзакций
        offline_tx_frame = ttk.LabelFrame(frame, text="Оффлайн транзакции")
        offline_tx_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(offline_tx_frame, text="Отправитель:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.offline_sender_entry = ttk.Combobox(offline_tx_frame, width=15)
        self.offline_sender_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(offline_tx_frame, text="Получатель:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.offline_receiver_entry = ttk.Combobox(offline_tx_frame, width=15)
        self.offline_receiver_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(offline_tx_frame, text="Сумма:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.offline_amount_entry = ttk.Entry(offline_tx_frame, width=10)
        self.offline_amount_entry.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(offline_tx_frame, text="Создать оффлайн транзакцию",
                  command=self.create_offline_transaction).grid(row=0, column=6, padx=5, pady=5)

        # Фрейм для смарт-контрактов
        smart_contract_frame = ttk.LabelFrame(frame, text="Смарт-контракты")
        smart_contract_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(smart_contract_frame, text="Отправитель:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.sc_sender_entry = ttk.Combobox(smart_contract_frame, width=15)
        self.sc_sender_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(smart_contract_frame, text="Получатель:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.sc_receiver_entry = ttk.Combobox(smart_contract_frame, width=15)
        self.sc_receiver_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(smart_contract_frame, text="Сумма:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.sc_amount_entry = ttk.Entry(smart_contract_frame, width=10)
        self.sc_amount_entry.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(smart_contract_frame, text="Создать смарт-контракт",
                  command=self.create_smart_contract).grid(row=0, column=6, padx=5, pady=5)

    def _create_fo_tab(self, frame):
        """Создает интерфейс для финансовых организаций"""
        # Фрейм для запросов на эмиссию
        emission_frame = ttk.LabelFrame(frame, text="Запрос на эмиссию")
        emission_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(emission_frame, text="Сумма эмиссии:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.fo_emission_amount_entry = ttk.Entry(emission_frame, width=15)
        self.fo_emission_amount_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(emission_frame, text="ID банка:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.fo_bank_entry = ttk.Combobox(emission_frame, width=15)
        self.fo_bank_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(emission_frame, text="Запросить эмиссию",
                  command=self.request_emission).grid(row=0, column=4, padx=5, pady=5)

        # Фрейм для уведомлений
        notifications_frame = ttk.LabelFrame(frame, text="Уведомления о транзакциях")
        notifications_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("type", "sender", "receiver", "amount", "timestamp", "status")
        self.fo_notifications_tree = ttk.Treeview(notifications_frame, columns=columns, show="headings")

        self.fo_notifications_tree.heading("type", text="Тип")
        self.fo_notifications_tree.heading("sender", text="Отправитель")
        self.fo_notifications_tree.heading("receiver", text="Получатель")
        self.fo_notifications_tree.heading("amount", text="Сумма")
        self.fo_notifications_tree.heading("timestamp", text="Время")
        self.fo_notifications_tree.heading("status", text="Статус")

        for col in columns:
            self.fo_notifications_tree.column(col, width=100, anchor=tk.W)

        self.fo_notifications_tree.column("amount", width=80, anchor=tk.E)
        self.fo_notifications_tree.pack(fill=tk.BOTH, expand=True)

    def _create_cb_tab(self, frame):
        """Создает интерфейс для Центрального Банка"""
        # Фрейм для обработки запросов на эмиссию
        emission_frame = ttk.LabelFrame(frame, text="Запросы на эмиссию")
        emission_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("fo_id", "cash_balance", "amount", "timestamp", "status")
        self.cb_emission_requests_tree = ttk.Treeview(emission_frame, columns=columns, show="headings")

        self.cb_emission_requests_tree.heading("fo_id", text="ID ФО")
        self.cb_emission_requests_tree.heading("cash_balance", text="Баланс безналичных")
        self.cb_emission_requests_tree.heading("amount", text="Сумма эмиссии")
        self.cb_emission_requests_tree.heading("timestamp", text="Время запроса")
        self.cb_emission_requests_tree.heading("status", text="Статус")

        for col in columns:
            self.cb_emission_requests_tree.column(col, width=120, anchor=tk.W)

        self.cb_emission_requests_tree.column("cash_balance", width=120, anchor=tk.E)
        self.cb_emission_requests_tree.column("amount", width=100, anchor=tk.E)
        self.cb_emission_requests_tree.pack(fill=tk.BOTH, expand=True)

        # Кнопки для обработки запросов
        button_frame = ttk.Frame(emission_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="Одобрить",
                  command=self.approve_emission_request).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(button_frame, text="Отклонить",
                  command=self.reject_emission_request).pack(side=tk.LEFT, padx=5, pady=5)

        # Фрейм для мониторинга транзакций
        monitoring_frame = ttk.LabelFrame(frame, text="Мониторинг транзакций")
        monitoring_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("tx_id", "sender", "receiver", "amount", "type", "timestamp", "status")
        self.cb_transactions_tree = ttk.Treeview(monitoring_frame, columns=columns, show="headings")

        self.cb_transactions_tree.heading("tx_id", text="ID транзакции")
        self.cb_transactions_tree.heading("sender", text="Отправитель")
        self.cb_transactions_tree.heading("receiver", text="Получатель")
        self.cb_transactions_tree.heading("amount", text="Сумма")
        self.cb_transactions_tree.heading("type", text="Тип")
        self.cb_transactions_tree.heading("timestamp", text="Время")
        self.cb_transactions_tree.heading("status", text="Статус")

        for col in columns:
            self.cb_transactions_tree.column(col, width=100, anchor=tk.W)

        self.cb_transactions_tree.column("amount", width=80, anchor=tk.E)
        self.cb_transactions_tree.pack(fill=tk.BOTH, expand=True)

    def _create_users_data_tab(self, frame):
        """Создает интерфейс для данных о пользователях"""
        # Фрейм для таблицы пользователей
        users_frame = ttk.LabelFrame(frame, text="Данные о пользователях")
        users_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("user_id", "user_type", "cash_balance", "digital_wallet_status",
                  "offline_wallet_status", "digital_balance", "offline_balance",
                  "offline_activation_time", "offline_deactivation_time")

        self.users_data_tree = ttk.Treeview(users_frame, columns=columns, show="headings")

        self.users_data_tree.heading("user_id", text="ID пользователя")
        self.users_data_tree.heading("user_type", text="Тип пользователя")
        self.users_data_tree.heading("cash_balance", text="Баланс безналичных")
        self.users_data_tree.heading("digital_wallet_status", text="Статус цифрового кошелька")
        self.users_data_tree.heading("offline_wallet_status", text="Статус оффлайн кошелька")
        self.users_data_tree.heading("digital_balance", text="Баланс цифрового кошелька")
        self.users_data_tree.heading("offline_balance", text="Баланс оффлайн кошелька")
        self.users_data_tree.heading("offline_activation_time", text="Время активации")
        self.users_data_tree.heading("offline_deactivation_time", text="Время деактивации")

        for col in columns:
            self.users_data_tree.column(col, width=120, anchor=tk.W)

        self.users_data_tree.column("cash_balance", width=120, anchor=tk.E)
        self.users_data_tree.column("digital_balance", width=120, anchor=tk.E)
        self.users_data_tree.column("offline_balance", width=120, anchor=tk.E)

        self.users_data_tree.pack(fill=tk.BOTH, expand=True)

        # Кнопка обновления
        ttk.Button(users_frame, text="Обновить",
                  command=self.refresh_users_data).pack(pady=5)

    def _create_transactions_data_tab(self, frame):
        """Создает интерфейс для данных о транзакциях"""
        # Фрейм для таблицы транзакций
        transactions_frame = ttk.LabelFrame(frame, text="Данные о транзакциях")
        transactions_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("sender", "receiver", "tx_type", "amount", "timestamp", "bank")

        self.transactions_data_tree = ttk.Treeview(transactions_frame, columns=columns, show="headings")

        self.transactions_data_tree.heading("sender", text="Отправитель")
        self.transactions_data_tree.heading("receiver", text="Получатель")
        self.transactions_data_tree.heading("tx_type", text="Тип")
        self.transactions_data_tree.heading("amount", text="Сумма")
        self.transactions_data_tree.heading("timestamp", text="Время")
        self.transactions_data_tree.heading("bank", text="Банк")

        for col in columns:
            self.transactions_data_tree.column(col, width=120, anchor=tk.W)

        self.transactions_data_tree.column("amount", width=100, anchor=tk.E)
        self.transactions_data_tree.pack(fill=tk.BOTH, expand=True)

        # Кнопка обновления
        ttk.Button(transactions_frame, text="Обновить",
                  command=self.refresh_transactions_data).pack(pady=5)

    def _create_offline_tx_tab(self, frame):
        """Создает интерфейс для оффлайн-транзакций"""
        # Фрейм для таблицы оффлайн транзакций
        offline_tx_frame = ttk.LabelFrame(frame, text="Оффлайн-транзакции")
        offline_tx_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("sender", "receiver", "amount", "bank", "timestamp", "status")

        self.offline_tx_tree = ttk.Treeview(offline_tx_frame, columns=columns, show="headings")

        self.offline_tx_tree.heading("sender", text="Отправитель")
        self.offline_tx_tree.heading("receiver", text="Получатель")
        self.offline_tx_tree.heading("amount", text="Сумма")
        self.offline_tx_tree.heading("bank", text="Банк")
        self.offline_tx_tree.heading("timestamp", text="Время")
        self.offline_tx_tree.heading("status", text="Статус")

        for col in columns:
            self.offline_tx_tree.column(col, width=120, anchor=tk.W)

        self.offline_tx_tree.column("amount", width=100, anchor=tk.E)
        self.offline_tx_tree.pack(fill=tk.BOTH, expand=True)

        # Кнопка обновления
        ttk.Button(offline_tx_frame, text="Обновить",
                  command=self.refresh_offline_tx_data).pack(pady=5)

    def _create_smart_contracts_tab(self, frame):
        """Создает интерфейс для смарт-контрактов"""
        # Фрейм для таблицы смарт-контрактов
        sc_frame = ttk.LabelFrame(frame, text="Смарт-контракты")
        sc_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("sender", "receiver", "amount", "bank", "functionality", "execution_time", "required_amount")

        self.smart_contracts_tree = ttk.Treeview(sc_frame, columns=columns, show="headings")

        self.smart_contracts_tree.heading("sender", text="Отправитель")
        self.smart_contracts_tree.heading("receiver", text="Получатель")
        self.smart_contracts_tree.heading("amount", text="Сумма")
        self.smart_contracts_tree.heading("bank", text="Банк")
        self.smart_contracts_tree.heading("functionality", text="Функционал")
        self.smart_contracts_tree.heading("execution_time", text="Время исполнения")
        self.smart_contracts_tree.heading("required_amount", text="Требуемая сумма")

        for col in columns:
            self.smart_contracts_tree.column(col, width=120, anchor=tk.W)

        self.smart_contracts_tree.column("amount", width=100, anchor=tk.E)
        self.smart_contracts_tree.column("required_amount", width=120, anchor=tk.E)
        self.smart_contracts_tree.pack(fill=tk.BOTH, expand=True)

        # Кнопка обновления
        ttk.Button(sc_frame, text="Обновить",
                  command=self.refresh_smart_contracts_data).pack(pady=5)

    def _create_consensus_tab(self, frame):
        """Создает интерфейс для консенсуса"""
        # Визуальное представление консенсуса
        visualization_frame = ttk.LabelFrame(frame, text="Визуализация консенсуса")
        visualization_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Создаем канвас для визуализации
        self.consensus_canvas = tk.Canvas(visualization_frame, bg="white", width=800, height=300)
        self.consensus_canvas.pack(fill=tk.BOTH, expand=True)

        # Рисуем визуализацию консенсуса
        self._draw_consensus_visualization()

        # Фрейм для хешей транзакций
        tx_hashes_frame = ttk.LabelFrame(frame, text="Хеши транзакций")
        tx_hashes_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("tx_hash", "timestamp", "status")
        self.tx_hashes_tree = ttk.Treeview(tx_hashes_frame, columns=columns, show="headings")

        self.tx_hashes_tree.heading("tx_hash", text="Хеш транзакции")
        self.tx_hashes_tree.heading("timestamp", text="Время")
        self.tx_hashes_tree.heading("status", text="Статус")

        for col in columns:
            self.tx_hashes_tree.column(col, width=150, anchor=tk.W)

        self.tx_hashes_tree.pack(fill=tk.BOTH, expand=True)

        # Фрейм для сформированных блоков
        blocks_frame = ttk.LabelFrame(frame, text="Сформированные блоки")
        blocks_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("block_index", "block_hash", "tx_count", "mining_time")
        self.blocks_tree = ttk.Treeview(blocks_frame, columns=columns, show="headings")

        self.blocks_tree.heading("block_index", text="Индекс блока")
        self.blocks_tree.heading("block_hash", text="Хеш блока")
        self.blocks_tree.heading("tx_count", text="Кол-во транзакций")
        self.blocks_tree.heading("mining_time", text="Время майнинга")

        for col in columns:
            self.blocks_tree.column(col, width=120, anchor=tk.W)

        self.blocks_tree.pack(fill=tk.BOTH, expand=True)

        # Кнопка обновления
        ttk.Button(frame, text="Обновить",
                  command=self.refresh_consensus_data).pack(pady=5)

    def _create_ledger_tab(self, frame):
        """Создает интерфейс для распределенного реестра"""
        # Фрейм для визуализации блокчейна
        visualization_frame = ttk.LabelFrame(frame, text="Визуализация блокчейна")
        visualization_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Создаем холст для визуализации
        self.canvas = tk.Canvas(visualization_frame, bg="white", width=800, height=400)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Фрейм для детальной информации о блоках
        blocks_frame = ttk.LabelFrame(frame, text="Детальная информация о блоках")
        blocks_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("index", "hash", "prev_hash", "tx_count", "timestamp")
        self.ledger_tree = ttk.Treeview(blocks_frame, columns=columns, show="headings")

        self.ledger_tree.heading("index", text="Индекс")
        self.ledger_tree.heading("hash", text="Хеш")
        self.ledger_tree.heading("prev_hash", text="Предыдущий хеш")
        self.ledger_tree.heading("tx_count", text="Кол-во транзакций")
        self.ledger_tree.heading("timestamp", text="Время")

        for col in columns:
            self.ledger_tree.column(col, width=120, anchor=tk.W)

        self.ledger_tree.pack(fill=tk.BOTH, expand=True)

        # Кнопка обновления
        ttk.Button(frame, text="Обновить",
                  command=self.refresh_ledger_data).pack(pady=5)

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

        # Создаем фигуру для графиков
        self.figure = plt.Figure(figsize=(6, 4), dpi=100)
        self.plot = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=charts_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Кнопка обновления
        ttk.Button(frame, text="Обновить",
                  command=self.refresh_metrics_data).pack(pady=5)

    def _draw_consensus_visualization(self):
        """Отрисовывает визуализацию консенсуса"""
        self.consensus_canvas.delete("all")

        # Параметры визуализации
        node_radius = 30
        spacing = 120
        start_x = 100
        start_y = 150

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

    def create_users(self):
        """Создает заданное количество пользователей"""
        try:
            count = int(self.user_count_entry.get())
            user_type = self.user_type_var.get()

            for i in range(count):
                user_id = f"USER{len(self.central_bank.users) + 1:04d}"
                user = {
                    "user_id": user_id,
                    "user_type": "Юридическое лицо" if user_type == "legal" else "Физическое лицо",
                    "cash_balance": 10000,
                    "digital_wallet_status": "Закрыт",
                    "offline_wallet_status": "Закрыт",
                    "digital_balance": 0,
                    "offline_balance": 0,
                    "offline_activation_time": None,
                    "offline_deactivation_time": None
                }
                self.central_bank.users[user_id] = user

            # Обновляем выпадающие списки
            self._update_comboboxes()

            messagebox.showinfo("Успех", f"Создано {count} пользователей типа {user_type}")
            self.refresh_users_data()
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
                    "status": "pending",
                    "balance": 0.0,
                    "cash_balance": 10000000,  # Баланс безналичных денег по умолчанию
                    "registration_date": datetime.now().isoformat()
                }
                self.central_bank.banks[bank_id] = bank

            # Обновляем выпадающие списки
            self._update_comboboxes()

            messagebox.showinfo("Успех", f"Создано {count} банков")
            self.refresh_fo_list()
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректное количество банков")

    def _update_comboboxes(self):
        """Обновляет выпадающие списки с ID пользователей и банков"""
        # Обновляем списки пользователей
        user_ids = list(self.central_bank.users.keys())
        for combobox in [self.wallet_user_entry, self.exchange_user_entry,
                        self.online_sender_entry, self.online_receiver_entry,
                        self.offline_user_entry, self.offline_sender_entry,
                        self.offline_receiver_entry, self.sc_sender_entry,
                        self.sc_receiver_entry]:
            if combobox:
                combobox['values'] = user_ids

        # Обновляем списки банков
        bank_ids = list(self.central_bank.banks.keys())
        if hasattr(self, 'fo_bank_entry'):
            self.fo_bank_entry['values'] = bank_ids

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
        self.refresh_users_data()

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

            user["cash_balance"] -= amount
            user["digital_balance"] += amount

            messagebox.showinfo("Успех", f"Обмен выполнен. Новый баланс цифрового кошелька: {user['digital_balance']}")
            self.refresh_users_data()
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

            # Выполняем транзакцию
            sender_user["digital_balance"] -= amount
            receiver_user["digital_balance"] += amount

            # Добавляем транзакцию в блокчейн
            self.central_bank.blockchain.add_transaction(
                sender=sender,
                recipient=receiver,
                amount=amount,
                transaction_type="online",
                metadata={"description": "Online transaction"}
            )

            messagebox.showinfo("Успех", "Онлайн транзакция выполнена успешно")
            self.refresh_users_data()
            self.refresh_transactions_data()
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
        self.refresh_users_data()

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

            messagebox.showinfo("Успех", f"Оффлайн кошелек пополнен. Новый баланс: {user['offline_balance']}")
            self.refresh_users_data()
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

            # Создаем оффлайн транзакцию
            offline_tx = {
                "sender": sender,
                "receiver": receiver,
                "amount": amount,
                "timestamp": datetime.now().isoformat(),
                "status": "ОФФЛАЙН"
            }
            self.central_bank.offline_transactions.append(offline_tx)

            # Обновляем балансы (в реальной системе это будет после обработки ЦБ)
            sender_user["offline_balance"] -= amount

            messagebox.showinfo("Успех", "Оффлайн транзакция создана и будет обработана при восстановлении соединения")
            self.refresh_offline_tx_data()
            self.refresh_users_data()
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

            # Создаем смарт-контракт
            smart_contract = {
                "contract_id": f"SC{len(self.central_bank.smart_contracts) + 1:04d}",
                "sender": sender,
                "receiver": receiver,
                "amount": amount,
                "functionality": "Оплата коммунальных платежей",
                "required_amount": 1000,
                "execution_time": (datetime.now() + timedelta(days=1)).isoformat(),
                "status": "СОЗДАН"
            }
            self.central_bank.smart_contracts[smart_contract["contract_id"]] = smart_contract

            # Обновляем баланс отправителя
            sender_user["digital_balance"] -= amount

            messagebox.showinfo("Успех", f"Смарт-контракт {smart_contract['contract_id']} создан")
            self.refresh_smart_contracts_data()
            self.refresh_users_data()
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

            # Создаем запрос на эмиссию
            emission_request = {
                "fo_id": bank_id,
                "cash_balance": bank["cash_balance"],
                "amount": amount,
                "timestamp": datetime.now().isoformat(),
                "status": "ОЖИДАНИЕ"
            }
            self.central_bank.emission_requests.append(emission_request)

            # Добавляем уведомление
            self.fo_notifications_tree.insert("", tk.END, values=(
                "emission_request",
                bank_id,
                "CENTRAL_BANK",
                amount,
                emission_request["timestamp"],
                "ОТПРАВЛЕНО"
            ))

            # Обновляем таблицу запросов на эмиссию
            self.refresh_cb_emission_requests()

            messagebox.showinfo("Успех", "Запрос на эмиссию отправлен в Центральный Банк")
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректная сумма")

    def approve_emission_request(self):
        """Одобряет запрос на эмиссию"""
        selected_item = self.cb_emission_requests_tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите запрос для одобрения")
            return

        request_values = self.cb_emission_requests_tree.item(selected_item)["values"]
        request_index = self.cb_emission_requests_tree.index(selected_item)

        # Обновляем статус запроса
        self.central_bank.emission_requests[request_index]["status"] = "ОДОБРЕНО"

        # Обновляем отображение
        self.cb_emission_requests_tree.set(selected_item, "status", "ОДОБРЕНО")

        # В реальной системе здесь будет выполнение эмиссии
        messagebox.showinfo("Успех", "Запрос на эмиссию одобрен")

    def reject_emission_request(self):
        """Отклоняет запрос на эмиссию"""
        selected_item = self.cb_emission_requests_tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите запрос для отклонения")
            return

        request_values = self.cb_emission_requests_tree.item(selected_item)["values"]
        request_index = self.cb_emission_requests_tree.index(selected_item)

        # Обновляем статус запроса
        self.central_bank.emission_requests[request_index]["status"] = "ОТКЛОНЕНО"

        # Обновляем отображение
        self.cb_emission_requests_tree.set(selected_item, "status", "ОТКЛОНЕНО")

        messagebox.showinfo("Успех", "Запрос на эмиссию отклонен")

    def refresh_users_data(self):
        """Обновляет данные о пользователях"""
        if not hasattr(self, 'users_data_tree'):
            return

        for item in self.users_data_tree.get_children():
            self.users_data_tree.delete(item)

        for user_id, user in self.central_bank.users.items():
            self.users_data_tree.insert("", tk.END, values=(
                user_id,
                user["user_type"],
                f"{user['cash_balance']:,.2f}",
                user["digital_wallet_status"],
                user["offline_wallet_status"],
                f"{user['digital_balance']:,.2f}",
                f"{user['offline_balance']:,.2f}",
                user["offline_activation_time"],
                user["offline_deactivation_time"]
            ))

    def refresh_transactions_data(self):
        """Обновляет данные о транзакциях"""
        if not hasattr(self, 'transactions_data_tree'):
            return

        for item in self.transactions_data_tree.get_children():
            self.transactions_data_tree.delete(item)

        # В реальной системе здесь будут данные из блокчейна
        # Для демонстрации добавим тестовые данные
        test_transactions = [
            ("USER0001", "USER0002", "онлайн", 1000, datetime.now().isoformat(), "BANK0001"),
            ("USER0002", "USER0003", "смарт-контракт", 500, datetime.now().isoformat(), "BANK0002")
        ]

        for tx in test_transactions:
            self.transactions_data_tree.insert("", tk.END, values=tx)

    def refresh_offline_tx_data(self):
        """Обновляет данные об оффлайн транзакциях"""
        if not hasattr(self, 'offline_tx_tree'):
            return

        for item in self.offline_tx_tree.get_children():
            self.offline_tx_tree.delete(item)

        for tx in self.central_bank.offline_transactions:
            self.offline_tx_tree.insert("", tk.END, values=(
                tx["sender"],
                tx["receiver"],
                f"{tx['amount']:,.2f}",
                "BANK0001",  # В реальной системе будет банк отправителя
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
                contract["sender"],
                contract["receiver"],
                f"{contract['amount']:,.2f}",
                "BANK0001",  # В реальной системе будет банк отправителя
                contract["functionality"],
                contract["execution_time"],
                f"{contract['required_amount']:,.2f}"
            ))

    def refresh_consensus_data(self):
        """Обновляет данные о консенсусе"""
        if not hasattr(self, 'tx_hashes_tree') or not hasattr(self, 'blocks_tree'):
            return

        # Очищаем таблицы
        for item in self.tx_hashes_tree.get_children():
            self.tx_hashes_tree.delete(item)

        for item in self.blocks_tree.get_children():
            self.blocks_tree.delete(item)

        # В реальной системе здесь будут данные из консенсуса
        # Для демонстрации добавим тестовые данные
        test_hashes = [
            ("tx123456", datetime.now().isoformat(), "ОЖИДАНИЕ"),
            ("tx789012", datetime.now().isoformat(), "ПОДТВЕРЖДЕНО")
        ]

        for tx in test_hashes:
            self.tx_hashes_tree.insert("", tk.END, values=tx)

        test_blocks = [
            (1, "block123456", 5, "1.2s"),
            (2, "block789012", 3, "0.8s")
        ]

        for block in test_blocks:
            self.blocks_tree.insert("", tk.END, values=block)

        # Обновляем визуализацию консенсуса
        self._draw_consensus_visualization()

    def refresh_ledger_data(self):
        """Обновляет данные о распределенном реестре"""
        if not hasattr(self, 'ledger_tree'):
            return

        for item in self.ledger_tree.get_children():
            self.ledger_tree.delete(item)

        # Очищаем канвас
        self.canvas.delete("all")

        # В реальной системе здесь будет визуализация блокчейна
        # Для демонстрации добавим тестовые данные
        test_blocks = [
            (1, "block123456", "block000000", 5, datetime.now().isoformat()),
            (2, "block789012", "block123456", 3, datetime.now().isoformat())
        ]

        for block in test_blocks:
            self.ledger_tree.insert("", tk.END, values=block)

        # Визуализация блокчейна
        self._draw_blockchain_visualization()

    def refresh_metrics_data(self):
        """Обновляет данные о метриках"""
        if not hasattr(self, 'metrics_tree'):
            return

        for item in self.metrics_tree.get_children():
            self.metrics_tree.delete(item)

        # В реальной системе здесь будут реальные метрики
        # Для демонстрации добавим тестовые данные
        test_metrics = [
            ("Транзакций в секунду", "15.2", "↑"),
            ("Время майнинга блока", "1.2s", "↓"),
            ("Задержка сети", "0.5s", "→")
        ]

        for metric in test_metrics:
            self.metrics_tree.insert("", tk.END, values=metric)

        # Обновляем график
        self._update_metrics_chart()

    def _update_metrics_chart(self):
        """Обновляет график метрик"""
        self.plot.clear()

        # В реальной системе здесь будут реальные данные
        # Для демонстрации создадим тестовые данные
        x = [1, 2, 3, 4, 5]
        y = [10, 15, 13, 17, 20]

        self.plot.plot(x, y, marker='o')
        self.plot.set_title("Транзакций в секунду")
        self.plot.set_xlabel("Время")
        self.plot.set_ylabel("TPS")

        self.canvas.draw()

    def _draw_blockchain_visualization(self):
        """Отрисовывает визуализацию блокчейна"""
        # Очищаем канвас
        self.canvas.delete("all")

        # Параметры визуализации
        block_width = 80
        block_height = 60
        start_x = 50
        start_y = 200
        spacing = 100

        # Рисуем блоки
        for i, block in enumerate(self.central_bank.blockchain.chain[-5:]):
            x = start_x + i * spacing
            y = start_y

            # Рисуем блок
            self.canvas.create_rectangle(x, y, x + block_width, y + block_height,
                                        fill="lightblue", outline="black", width=2)

            # Пишем информацию о блоке
            self.canvas.create_text(x + block_width/2, y + 10, text=f"Блок {block.index}", font=('Arial', 8, 'bold'))
            self.canvas.create_text(x + block_width/2, y + 30, text=block.compute_hash()[:8] + "...", font=('Arial', 7))
            self.canvas.create_text(x + block_width/2, y + 50, text=f"Транзакций: {len(block.transactions)}", font=('Arial', 7))

            # Рисуем стрелку к следующему блоку
            if i < len(self.central_bank.blockchain.chain[-5:]) - 1:
                next_x = start_x + (i + 1) * spacing
                self.canvas.create_line(x + block_width, y + block_height/2,
                                       next_x, y + block_height/2,
                                       arrow=tk.LAST, width=2)

            # Рисуем хеш предыдущего блока (если есть)
            if block.index > 0:
                self.canvas.create_text(x + block_width/2, y - 10,
                                        text=f"Prev: {block.previous_hash[:8]}...",
                                        font=('Arial', 7, 'italic'))

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

    def refresh_all_data(self):
        """Обновляет все данные в интерфейсе"""
        # Обновляем выпадающие списки
        self._update_comboboxes()

        if hasattr(self, 'users_data_tree'):
            self.refresh_users_data()
        if hasattr(self, 'transactions_data_tree'):
            self.refresh_transactions_data()
        if hasattr(self, 'offline_tx_tree'):
            self.refresh_offline_tx_data()
        if hasattr(self, 'smart_contracts_tree'):
            self.refresh_smart_contracts_data()
        if hasattr(self, 'tx_hashes_tree') and hasattr(self, 'blocks_tree'):
            self.refresh_consensus_data()
        if hasattr(self, 'ledger_tree'):
            self.refresh_ledger_data()
        if hasattr(self, 'metrics_tree'):
            self.refresh_metrics_data()
        if hasattr(self, 'fo_notifications_tree'):
            self.refresh_fo_notifications()
        if hasattr(self, 'cb_emission_requests_tree'):
            self.refresh_cb_emission_requests()
        if hasattr(self, 'cb_transactions_tree'):
            self.refresh_cb_transactions()

    def refresh_fo_notifications(self):
        """Обновляет уведомления финансовых организаций"""
        if not hasattr(self, 'fo_notifications_tree'):
            return

        for item in self.fo_notifications_tree.get_children():
            self.fo_notifications_tree.delete(item)

        # Тестовые данные уведомлений
        test_notifications = [
            ("emission_request", "BANK0001", "CENTRAL_BANK", 1000000, datetime.now().isoformat(), "ОТПРАВЛЕНО"),
            ("transaction", "USER0001", "USER0002", 500, datetime.now().isoformat(), "ОБРАБОТАНО")
        ]

        for notification in test_notifications:
            self.fo_notifications_tree.insert("", tk.END, values=notification)

    def refresh_cb_transactions(self):
        """Обновляет транзакции для ЦБ"""
        if not hasattr(self, 'cb_transactions_tree'):
            return

        for item in self.cb_transactions_tree.get_children():
            self.cb_transactions_tree.delete(item)

        # Тестовые данные транзакций
        test_transactions = [
            ("TX0001", "USER0001", "USER0002", 1000, "онлайн", datetime.now().isoformat(), "ВЫПОЛНЕНО"),
            ("TX0002", "BANK0001", "USER0003", 500000, "эмиссия", datetime.now().isoformat(), "ВЫПОЛНЕНО")
        ]

        for tx in test_transactions:
            self.cb_transactions_tree.insert("", tk.END, values=tx)

    def show_about(self):
        """Показывает информацию о программе"""
        about_text = """Система Цифрового Рубля v1.0
Центральный Банк Российской Федерации

Эта программа моделирует работу системы цифрового рубля, включая:
- Создание и управление пользователями (физические и юридические лица)
- Работу финансовых организаций (банков)
- Функционал центрального банка
- Различные типы транзакций (онлайн, оффлайн, смарт-контракты)
- Механизмы консенсуса и распределенного реестра

© 2023 Банк России"""
        messagebox.showinfo("О программе", about_text)
