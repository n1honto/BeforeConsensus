import tkinter as tk
from tkinter import ttk, messagebox, font
import hashlib
import os
import logging
from datetime import datetime, timedelta
import threading
import time
import random

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/app.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

# Импорты из core
from core.central_bank import CentralBank
from core.financial_organization import FinancialOrganization
from core.user import User
from core.transaction import Transaction
from core.wallet import Wallet

# Импорты HotStuff
from hotstuff_consensus.hotstuff import HotStuff
from hotstuff_consensus.node import Node
from hotstuff_consensus.block import Block

class DigitalRubleApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Цифровой рубль — Симулятор с HotStuff консенсусом")

        # Увеличиваем шрифт по умолчанию
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=12)

        # Создаем стили для виджетов
        self.style = ttk.Style()
        self.style.configure("TButton", font=('Arial', 12))
        self.style.configure("TLabel", font=('Arial', 12))
        self.style.configure("TCombobox", font=('Arial', 12))
        self.style.configure("TEntry", font=('Arial', 12))

        # Создаём директории для логов и данных если их нет
        os.makedirs('data', exist_ok=True)
        os.makedirs('logs', exist_ok=True)

        # Очистка файла с хешами транзакций при запуске программы
        with open("data/transaction_hashes.txt", "w", encoding="utf-8") as file:
            file.write("")

        # Инициализация системы
        self.cb = CentralBank()

        # Создание нескольких банков
        self.banks = {
            "Сбербанк": FinancialOrganization("Сбербанк", self.cb),
            "ВТБ": FinancialOrganization("ВТБ", self.cb),
            "Тинькофф": FinancialOrganization("Тинькофф", self.cb)
        }

        # Пользователи
        self.users = {}

        # Инициализация HotStuff консенсуса
        self.hotstuff_nodes = [Node(i, is_leader=(i==0)) for i in range(4)]
        self.hotstuff = HotStuff(self.hotstuff_nodes)

        # Создание вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(padx=10, pady=10, fill="both", expand=True)

        # Вкладка для управления системой
        self.control_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.control_tab, text="Управление")

        # Вкладка для вывода данных о пользователях
        self.users_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.users_tab, text="Пользователи")

        # Вкладка для вывода работы ЦБ
        self.cb_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.cb_tab, text="Центральный Банк")

        # Вкладка для информации об оффлайн-транзакциях
        self.offline_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.offline_tab, text="Оффлайн-транзакции")

        # Вкладка для процессов оффлайн-транзакций
        self.offline_process_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.offline_process_tab, text="Процессы оффлайн-транзакций")

        # Вкладка для информации о блоках HotStuff
        self.blocks_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.blocks_tab, text="Блоки HotStuff")

        # Вкладка для визуализации консенсуса
        self.consensus_visual_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.consensus_visual_tab, text="Визуализация консенсуса")

        # Виджеты на вкладке управления
        self.create_control_widgets()

        # Таблица пользователей
        self.create_users_table()

        # Таблица ЦБ
        self.create_cb_table()

        # Таблица оффлайн-транзакций
        self.create_offline_transactions_table()

        # Таблица процессов оффлайн-транзакций
        self.create_offline_process_table()

        # Таблица блоков HotStuff
        self.create_blocks_table()

        # Визуализация консенсуса
        self.create_consensus_visualization()

        # Настройка минимального размера окна
        self.root.minsize(1000, 700)

        # Флаг для анимации консенсуса
        self.consensus_animation_running = False
        self.consensus_animation_thread = None

    def _on_mousewheel(self, event):
        """Обработчик прокрутки колесиком мыши"""
        if hasattr(self, 'canvas'):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_visual_mousewheel(self, event):
        """Обработчик прокрутки колесиком мыши для канваса визуализации"""
        if event.num == 5 or event.delta < 0:  # Прокрутка вниз или назад
            self.visual_canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:  # Прокрутка вверх или вперед
            self.visual_canvas.yview_scroll(-1, "units")
        return "break"

    def _on_state_mousewheel(self, event):
        """Обработчик прокрутки колесиком мыши для вкладки текущего состояния"""
        self.current_state_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_history_mousewheel(self, event):
        """Обработчик прокрутки колесиком мыши для вкладки истории блоков"""
        self.block_history_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def create_control_widgets(self):
        """Создаёт виджеты на вкладке управления"""
        # Блок для выбора банка
        self.bank_frame = ttk.LabelFrame(self.control_tab, text="Выбор банка")
        self.bank_frame.pack(padx=10, pady=10, fill="x")

        self.bank_label = ttk.Label(self.bank_frame, text="Банк:")
        self.bank_label.grid(row=0, column=0, padx=10, pady=10)

        self.bank_combobox = ttk.Combobox(self.bank_frame, values=list(self.banks.keys()), state="readonly", width=20)
        self.bank_combobox.grid(row=0, column=1, padx=10, pady=10)

        # Блок для запроса эмиссии
        self.emission_frame = ttk.LabelFrame(self.control_tab, text="Запрос эмиссии")
        self.emission_frame.pack(padx=10, pady=10, fill="x")

        self.emission_amount_label = ttk.Label(self.emission_frame, text="Сумма эмиссии:")
        self.emission_amount_label.grid(row=0, column=0, padx=10, pady=10)

        self.emission_amount_entry = ttk.Entry(self.emission_frame, width=15)
        self.emission_amount_entry.grid(row=0, column=1, padx=10, pady=10)

        self.request_emission_button = ttk.Button(self.emission_frame, text="Запросить эмиссию", command=self.request_emission)
        self.request_emission_button.grid(row=0, column=2, padx=10, pady=10)

        # Блок для создания пользователей
        self.user_frame = ttk.LabelFrame(self.control_tab, text="Создание пользователей")
        self.user_frame.pack(padx=10, pady=10, fill="x")

        self.user_count_label = ttk.Label(self.user_frame, text="Количество пользователей:")
        self.user_count_label.grid(row=0, column=0, padx=10, pady=10)

        self.user_count_entry = ttk.Entry(self.user_frame, width=15)
        self.user_count_entry.grid(row=0, column=1, padx=10, pady=10)

        self.user_type_label = ttk.Label(self.user_frame, text="Тип пользователей:")
        self.user_type_label.grid(row=1, column=0, padx=10, pady=10)

        self.user_type_combobox = ttk.Combobox(self.user_frame, values=["Физические лица", "Юридические лица"], state="readonly", width=20)
        self.user_type_combobox.grid(row=1, column=1, padx=10, pady=10)
        self.user_type_combobox.set("Физические лица")

        self.create_users_button = ttk.Button(self.user_frame, text="Создать пользователей", command=self.create_users)
        self.create_users_button.grid(row=1, column=2, padx=10, pady=10)

        # Блок для обмена безналичных на цифровые
        self.exchange_frame = ttk.LabelFrame(self.control_tab, text="Обмен безналичных на цифровые")
        self.exchange_frame.pack(padx=10, pady=10, fill="x")

        self.exchange_user_label = ttk.Label(self.exchange_frame, text="Пользователь:")
        self.exchange_user_label.grid(row=0, column=0, padx=10, pady=10)

        self.exchange_user_combobox = ttk.Combobox(self.exchange_frame, state="readonly", width=20)
        self.exchange_user_combobox.grid(row=0, column=1, padx=10, pady=10)

        self.exchange_bank_label = ttk.Label(self.exchange_frame, text="Банк:")
        self.exchange_bank_label.grid(row=0, column=2, padx=10, pady=10)

        self.exchange_bank_combobox = ttk.Combobox(self.exchange_frame, values=list(self.banks.keys()), state="readonly", width=20)
        self.exchange_bank_combobox.grid(row=0, column=3, padx=10, pady=10)
        self.exchange_bank_combobox.set(list(self.banks.keys())[0])

        self.exchange_amount_label = ttk.Label(self.exchange_frame, text="Сумма:")
        self.exchange_amount_label.grid(row=0, column=4, padx=10, pady=10)

        self.exchange_amount_entry = ttk.Entry(self.exchange_frame, width=15)
        self.exchange_amount_entry.grid(row=0, column=5, padx=10, pady=10)

        self.exchange_button = ttk.Button(self.exchange_frame, text="Обменять", command=self.exchange_cash_to_digital)
        self.exchange_button.grid(row=0, column=6, padx=10, pady=10)

        # Блок для работы с оффлайн-кошельками
        self.offline_wallet_frame = ttk.LabelFrame(self.control_tab, text="Оффлайн-кошельки")
        self.offline_wallet_frame.pack(padx=10, pady=10, fill="x")

        self.offline_wallet_user_label = ttk.Label(self.offline_wallet_frame, text="Пользователь:")
        self.offline_wallet_user_label.grid(row=0, column=0, padx=10, pady=10)

        self.offline_wallet_user_combobox = ttk.Combobox(self.offline_wallet_frame, state="readonly", width=20)
        self.offline_wallet_user_combobox.grid(row=0, column=1, padx=10, pady=10)

        self.create_offline_wallet_button = ttk.Button(
            self.offline_wallet_frame, text="Создать оффлайн-кошелёк", command=self.create_offline_wallet
        )
        self.create_offline_wallet_button.grid(row=0, column=2, padx=10, pady=10)

        self.topup_amount_label = ttk.Label(self.offline_wallet_frame, text="Сумма пополнения:")
        self.topup_amount_label.grid(row=1, column=0, padx=10, pady=10)

        self.topup_amount_entry = ttk.Entry(self.offline_wallet_frame, width=15)
        self.topup_amount_entry.grid(row=1, column=1, padx=10, pady=10)

        self.topup_wallet_button = ttk.Button(
            self.offline_wallet_frame, text="Пополнить оффлайн-кошелёк", command=self.topup_offline_wallet
        )
        self.topup_wallet_button.grid(row=1, column=2, padx=10, pady=10)

        # Блок для создания онлайн-транзакций
        self.transaction_frame = ttk.LabelFrame(self.control_tab, text="Создание онлайн-транзакций")
        self.transaction_frame.pack(padx=10, pady=10, fill="x")

        self.sender_label = ttk.Label(self.transaction_frame, text="Отправитель:")
        self.sender_label.grid(row=0, column=0, padx=10, pady=10)

        self.sender_combobox = ttk.Combobox(self.transaction_frame, state="readonly", width=20)
        self.sender_combobox.grid(row=0, column=1, padx=10, pady=10)

        self.recipient_label = ttk.Label(self.transaction_frame, text="Получатель:")
        self.recipient_label.grid(row=0, column=2, padx=10, pady=10)

        self.recipient_combobox = ttk.Combobox(self.transaction_frame, state="readonly", width=20)
        self.recipient_combobox.grid(row=0, column=3, padx=10, pady=10)

        self.amount_label = ttk.Label(self.transaction_frame, text="Сумма:")
        self.amount_label.grid(row=0, column=4, padx=10, pady=10)

        self.amount_entry = ttk.Entry(self.transaction_frame, width=15)
        self.amount_entry.grid(row=0, column=5, padx=10, pady=10)

        self.create_online_transaction_button = ttk.Button(
            self.transaction_frame, text="Создать онлайн-транзакцию", command=self.create_online_transaction
        )
        self.create_online_transaction_button.grid(row=0, column=6, padx=10, pady=10)

        # Блок для создания оффлайн-транзакций
        self.offline_transaction_frame = ttk.LabelFrame(self.control_tab, text="Создание оффлайн-транзакций")
        self.offline_transaction_frame.pack(padx=10, pady=10, fill="x")

        self.offline_sender_label = ttk.Label(self.offline_transaction_frame, text="Отправитель:")
        self.offline_sender_label.grid(row=0, column=0, padx=10, pady=10)

        self.offline_sender_combobox = ttk.Combobox(self.offline_transaction_frame, state="readonly", width=20)
        self.offline_sender_combobox.grid(row=0, column=1, padx=10, pady=10)

        self.offline_recipient_label = ttk.Label(self.offline_transaction_frame, text="Получатель:")
        self.offline_recipient_label.grid(row=0, column=2, padx=10, pady=10)

        self.offline_recipient_combobox = ttk.Combobox(self.offline_transaction_frame, state="readonly", width=20)
        self.offline_recipient_combobox.grid(row=0, column=3, padx=10, pady=10)

        self.offline_amount_label = ttk.Label(self.offline_transaction_frame, text="Сумма:")
        self.offline_amount_label.grid(row=0, column=4, padx=10, pady=10)

        self.offline_amount_entry = ttk.Entry(self.offline_transaction_frame, width=15)
        self.offline_amount_entry.grid(row=0, column=5, padx=10, pady=10)

        self.create_offline_transaction_button = ttk.Button(
            self.offline_transaction_frame, text="Создать оффлайн-транзакцию", command=self.create_offline_transaction
        )
        self.create_offline_transaction_button.grid(row=0, column=6, padx=10, pady=10)

        # Кнопка для синхронизации оффлайн-транзакций
        self.sync_offline_button = ttk.Button(self.control_tab, text="Синхронизировать оффлайн-транзакции", command=self.sync_offline_transactions)
        self.sync_offline_button.pack(pady=20)

        # Кнопка для обработки очереди ЦБ
        self.process_queue_button = ttk.Button(self.control_tab, text="Обработать очередь ЦБ", command=self.process_queue)
        self.process_queue_button.pack(pady=20)

    def create_users_table(self):
        """Создаёт таблицу пользователей"""
        self.users_tree = ttk.Treeview(self.users_tab, columns=(
            "system_name", "type", "digital_wallet", "offline_wallet",
            "offline_wallet_balance", "cash_balance", "digital_balance",
            "wallet_activation", "wallet_expiry"), show="headings", height=20)

        self.users_tree.heading("system_name", text="Наименование в системе")
        self.users_tree.heading("type", text="Тип")
        self.users_tree.heading("digital_wallet", text="Цифровой кошелёк")
        self.users_tree.heading("offline_wallet", text="Оффлайн кошелёк")
        self.users_tree.heading("offline_wallet_balance", text="Баланс оффлайн кошелька")
        self.users_tree.heading("cash_balance", text="Безналичный баланс (РУБ)")
        self.users_tree.heading("digital_balance", text="Цифровой баланс (ЦР)")
        self.users_tree.heading("wallet_activation", text="Дата активации")
        self.users_tree.heading("wallet_expiry", text="Дата истечения")

        self.users_tree.column("system_name", width=150)
        self.users_tree.column("type", width=120)
        self.users_tree.column("digital_wallet", width=120)
        self.users_tree.column("offline_wallet", width=120)
        self.users_tree.column("offline_wallet_balance", width=150)
        self.users_tree.column("cash_balance", width=150)
        self.users_tree.column("digital_balance", width=150)
        self.users_tree.column("wallet_activation", width=150)
        self.users_tree.column("wallet_expiry", width=150)

        self.users_tree.pack(fill="both", expand=True)

    def create_cb_table(self):
        """Создаёт таблицу ЦБ"""
        self.banks_label = ttk.Label(self.cb_tab, text="Балансы банков:", font=('Arial', 12, 'bold'))
        self.banks_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.banks_tree = ttk.Treeview(self.cb_tab, columns=("bank_name", "cash_balance", "digital_balance"), show="headings", height=10)
        self.banks_tree.heading("bank_name", text="Название банка")
        self.banks_tree.heading("cash_balance", text="Безналичный баланс (РУБ)")
        self.banks_tree.heading("digital_balance", text="Цифровой баланс (ЦР)")
        self.banks_tree.column("bank_name", width=150)
        self.banks_tree.column("cash_balance", width=150)
        self.banks_tree.column("digital_balance", width=150)
        self.banks_tree.pack(fill="both", expand=True, pady=(0, 10))

        self.queue_label = ttk.Label(self.cb_tab, text="Очередь транзакций на обработку:", font=('Arial', 12, 'bold'))
        self.queue_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.transactions_tree = ttk.Treeview(self.cb_tab, columns=("sender", "recipient", "amount", "bank", "status"), show="headings", height=10)
        self.transactions_tree.heading("sender", text="Отправитель")
        self.transactions_tree.heading("recipient", text="Получатель")
        self.transactions_tree.heading("amount", text="Сумма (ЦР)")
        self.transactions_tree.heading("bank", text="Банк")
        self.transactions_tree.heading("status", text="Статус")
        self.transactions_tree.heading("#0", text="ID транзакции")
        self.transactions_tree.column("#0", width=150)
        self.transactions_tree.column("sender", width=150)
        self.transactions_tree.column("recipient", width=150)
        self.transactions_tree.column("amount", width=100)
        self.transactions_tree.column("bank", width=100)
        self.transactions_tree.column("status", width=100)
        self.transactions_tree.pack(fill="both", expand=True, pady=(0, 10))

        self.hash_label = ttk.Label(self.cb_tab, text="Хеши обработанных транзакций:", font=('Arial', 12, 'bold'))
        self.hash_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.hash_tree = ttk.Treeview(self.cb_tab, columns=("hash",), show="headings", height=10)
        self.hash_tree.heading("hash", text="Хеш")
        self.hash_tree.heading("#0", text="ID транзакции")
        self.hash_tree.column("#0", width=150)
        self.hash_tree.column("hash", width=400)
        self.hash_tree.pack(fill="both", expand=True, pady=(0, 0))

        self.cb_balance_label = ttk.Label(self.cb_tab, text=f"Общий баланс цифровых рублей ЦБ: {self.cb.total_balance} ЦР", font=('Arial', 12))
        self.cb_balance_label.pack(pady=(10, 0))

    def create_offline_transactions_table(self):
        """Создаёт таблицу оффлайн-транзакций"""
        self.offline_label = ttk.Label(self.offline_tab, text="Оффлайн-транзакции:", font=('Arial', 12, 'bold'))
        self.offline_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.offline_transactions_tree = ttk.Treeview(
            self.offline_tab,
            columns=("sender", "recipient", "amount", "transaction_time",
                    "wallet_open_time", "wallet_expiry_time", "status", "action_time"),
            show="headings",
            height=20
        )

        self.offline_transactions_tree.heading("sender", text="Отправитель")
        self.offline_transactions_tree.heading("recipient", text="Получатель")
        self.offline_transactions_tree.heading("amount", text="Сумма (ЦР)")
        self.offline_transactions_tree.heading("transaction_time", text="Время транзакции")
        self.offline_transactions_tree.heading("wallet_open_time", text="Время открытия кошелька")
        self.offline_transactions_tree.heading("wallet_expiry_time", text="Время истечения")
        self.offline_transactions_tree.heading("status", text="Статус")
        self.offline_transactions_tree.heading("action_time", text="Время действия")

        self.offline_transactions_tree.column("#0", width=200)
        self.offline_transactions_tree.column("sender", width=150)
        self.offline_transactions_tree.column("recipient", width=150)
        self.offline_transactions_tree.column("amount", width=100)
        self.offline_transactions_tree.column("transaction_time", width=150)
        self.offline_transactions_tree.column("wallet_open_time", width=150)
        self.offline_transactions_tree.column("wallet_expiry_time", width=150)
        self.offline_transactions_tree.column("status", width=100)
        self.offline_transactions_tree.column("action_time", width=150)

        self.offline_transactions_tree.pack(fill="both", expand=True, pady=(0, 10))

    def create_offline_process_table(self):
        """Создаёт таблицу процессов оффлайн-транзакций"""
        self.offline_process_label = ttk.Label(self.offline_process_tab, text="Процессы оффлайн-транзакций:", font=('Arial', 12, 'bold'))
        self.offline_process_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.offline_process_tree = ttk.Treeview(
            self.offline_process_tab,
            columns=("sender", "recipient", "amount", "action", "transaction_id", "status", "timestamp"),
            show="headings",
            height=20
        )

        self.offline_process_tree.heading("sender", text="Отправитель")
        self.offline_process_tree.heading("recipient", text="Получатель")
        self.offline_process_tree.heading("amount", text="Сумма (ЦР)")
        self.offline_process_tree.heading("action", text="Действие")
        self.offline_process_tree.heading("transaction_id", text="ID транзакции")
        self.offline_process_tree.heading("status", text="Статус")
        self.offline_process_tree.heading("timestamp", text="Время")

        self.offline_process_tree.column("sender", width=120)
        self.offline_process_tree.column("recipient", width=120)
        self.offline_process_tree.column("amount", width=100)
        self.offline_process_tree.column("action", width=150)
        self.offline_process_tree.column("transaction_id", width=200)
        self.offline_process_tree.column("status", width=100)
        self.offline_process_tree.column("timestamp", width=150)

        self.offline_process_tree.pack(fill="both", expand=True, pady=(0, 10))

    def create_blocks_table(self):
        """Создаёт таблицу блоков HotStuff"""
        self.blocks_label = ttk.Label(self.blocks_tab, text="Информация о блоках HotStuff:", font=('Arial', 12, 'bold'))
        self.blocks_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.blocks_tree = ttk.Treeview(
            self.blocks_tab,
            columns=("height", "hash", "parent_hash", "tx_count", "timestamp", "status"),
            show="headings",
            height=20
        )

        self.blocks_tree.heading("height", text="Высота")
        self.blocks_tree.heading("hash", text="Хеш блока")
        self.blocks_tree.heading("parent_hash", text="Хеш родителя")
        self.blocks_tree.heading("tx_count", text="Кол-во транзакций")
        self.blocks_tree.heading("timestamp", text="Время создания")
        self.blocks_tree.heading("status", text="Статус")

        self.blocks_tree.column("height", width=80)
        self.blocks_tree.column("hash", width=200)
        self.blocks_tree.column("parent_hash", width=200)
        self.blocks_tree.column("tx_count", width=100)
        self.blocks_tree.column("timestamp", width=150)
        self.blocks_tree.column("status", width=100)

        self.blocks_tree.pack(fill="both", expand=True, pady=(0, 10))

    def create_consensus_visualization(self):
        """Создаёт визуализацию процесса консенсуса"""
        # Основной фрейм для визуализации
        self.visual_frame = ttk.LabelFrame(self.consensus_visual_tab, text="Визуализация консенсуса HotStuff")
        self.visual_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Канвас для рисования
        self.visual_canvas = tk.Canvas(self.visual_frame, width=800, height=600, bg="white", highlightthickness=0)
        self.visual_canvas.pack(fill="both", expand=True)

        # Привязка колесика мыши к канвасу визуализации
        self.visual_canvas.bind("<MouseWheel>", self._on_visual_mousewheel)
        self.visual_canvas.bind("<Button-4>", self._on_visual_mousewheel)
        self.visual_canvas.bind("<Button-5>", self._on_visual_mousewheel)

        # Легенда
        legend_frame = ttk.Frame(self.consensus_visual_tab)
        legend_frame.pack(padx=10, pady=5, fill="x")

        ttk.Label(legend_frame, text="Легенда:", font=('Arial', 10, 'bold')).pack(side="left", padx=5)
        ttk.Label(legend_frame, text="🔴 - Лидер", foreground="red").pack(side="left", padx=10)
        ttk.Label(legend_frame, text="🔵 - Узел", foreground="blue").pack(side="left", padx=10)
        ttk.Label(legend_frame, text="🟢 - Голосование", foreground="green").pack(side="left", padx=10)
        ttk.Label(legend_frame, text="🟣 - Предложение", foreground="purple").pack(side="left", padx=10)
        ttk.Label(legend_frame, text="🔴 - Подтверждение", foreground="red").pack(side="left", padx=10)

        # Кнопки управления
        control_frame = ttk.Frame(self.consensus_visual_tab)
        control_frame.pack(padx=10, pady=10, fill="x")

        self.start_animation_button = ttk.Button(
            control_frame,
            text="🔄 Запустить анимацию консенсуса",
            command=self.start_consensus_animation
        )
        self.start_animation_button.pack(side="left", padx=5, pady=5)

        self.stop_animation_button = ttk.Button(
            control_frame,
            text="⏹ Остановить анимацию",
            command=self.stop_consensus_animation,
            state="disabled"
        )
        self.stop_animation_button.pack(side="left", padx=5, pady=5)

        self.clear_canvas_button = ttk.Button(
            control_frame,
            text="🧹 Очистить",
            command=self.clear_visual_canvas
        )
        self.clear_canvas_button.pack(side="left", padx=5, pady=5)

        # Информационная панель с вкладками
        self.info_notebook = ttk.Notebook(self.consensus_visual_tab)
        self.info_notebook.pack(padx=10, pady=10, fill="both", expand=True)

        # Вкладка с текущим состоянием
        self.current_state_tab = ttk.Frame(self.info_notebook)
        self.info_notebook.add(self.current_state_tab, text="Текущее состояние")

        # Создаем контейнер с канвасом для скролла
        self.current_state_container = ttk.Frame(self.current_state_tab)
        self.current_state_container.pack(fill="both", expand=True)

        self.current_state_canvas = tk.Canvas(self.current_state_container)
        self.current_state_scrollbar = ttk.Scrollbar(self.current_state_container, orient="vertical", command=self.current_state_canvas.yview)
        self.current_state_scrollable_frame = ttk.Frame(self.current_state_canvas)

        self.current_state_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.current_state_canvas.configure(
                scrollregion=self.current_state_canvas.bbox("all")
            )
        )

        self.current_state_canvas.create_window((0, 0), window=self.current_state_scrollable_frame, anchor="nw")
        self.current_state_canvas.configure(yscrollcommand=self.current_state_scrollbar.set)

        self.current_state_canvas.pack(side="left", fill="both", expand=True)
        self.current_state_scrollbar.pack(side="right", fill="y")

        # Привязка колесика мыши
        self.current_state_scrollable_frame.bind("<MouseWheel>", lambda event: self._on_state_mousewheel(event))
        self.current_state_canvas.bind("<MouseWheel>", lambda event: self._on_state_mousewheel(event))

        self.consensus_info = tk.StringVar()
        self.consensus_info_label = ttk.Label(
            self.current_state_scrollable_frame,
            textvariable=self.consensus_info,
            wraplength=700,
            justify="left"
        )
        self.consensus_info_label.pack(padx=10, pady=10, fill="both", expand=True)

        # Вкладка с историей блоков
        self.block_history_tab = ttk.Frame(self.info_notebook)
        self.info_notebook.add(self.block_history_tab, text="История блоков")

        # Создаем контейнер с канвасом для скролла
        self.block_history_container = ttk.Frame(self.block_history_tab)
        self.block_history_container.pack(fill="both", expand=True)

        self.block_history_canvas = tk.Canvas(self.block_history_container)
        self.block_history_scrollbar = ttk.Scrollbar(self.block_history_container, orient="vertical", command=self.block_history_canvas.yview)
        self.block_history_scrollable_frame = ttk.Frame(self.block_history_canvas)

        self.block_history_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.block_history_canvas.configure(
                scrollregion=self.block_history_canvas.bbox("all")
            )
        )

        self.block_history_canvas.create_window((0, 0), window=self.block_history_scrollable_frame, anchor="nw")
        self.block_history_canvas.configure(yscrollcommand=self.block_history_scrollbar.set)

        self.block_history_canvas.pack(side="left", fill="both", expand=True)
        self.block_history_scrollbar.pack(side="right", fill="y")

        # Привязка колесика мыши
        self.block_history_scrollable_frame.bind("<MouseWheel>", lambda event: self._on_history_mousewheel(event))
        self.block_history_canvas.bind("<MouseWheel>", lambda event: self._on_history_mousewheel(event))

        self.block_history_tree = ttk.Treeview(
            self.block_history_scrollable_frame,
            columns=("height", "hash", "tx_count", "timestamp"),
            show="headings",
            height=20
        )

        self.block_history_tree.heading("height", text="Высота")
        self.block_history_tree.heading("hash", text="Хеш блока")
        self.block_history_tree.heading("tx_count", text="Транзакций")
        self.block_history_tree.heading("timestamp", text="Время создания")

        self.block_history_tree.column("height", width=80)
        self.block_history_tree.column("hash", width=200)
        self.block_history_tree.column("tx_count", width=100)
        self.block_history_tree.column("timestamp", width=150)

        self.block_history_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Начальные параметры визуализации
        self.node_positions = {
            0: (200, 150),  # Лидер
            1: (500, 100),
            2: (200, 300),
            3: (500, 300)
        }
        self.node_colors = {
            0: "#FF6B6B",  # Лидер - красный
            1: "#4ECDC4",  # Узел 1 - бирюзовый
            2: "#45B7D1",  # Узел 2 - голубой
            3: "#FFA07A"   # Узел 3 - лососевый
        }
        self.node_radius = 40
        self.connection_width = 2

        # Рисуем начальное состояние
        self.draw_consensus_network()

        # Обновляем историю блоков
        self.update_block_history()

    def draw_consensus_network(self):
        """Рисует сеть узлов консенсуса"""
        self.visual_canvas.delete("all")

        # Рисуем фон
        self.visual_canvas.create_rectangle(0, 0, 800, 600, fill="#F8F9FA", outline="")

        # Рисуем соединения между узлами
        nodes = list(self.node_positions.keys())
        for i in range(len(nodes)):
            for j in range(i+1, len(nodes)):
                x1, y1 = self.node_positions[nodes[i]]
                x2, y2 = self.node_positions[nodes[j]]
                self.visual_canvas.create_line(x1, y1, x2, y2, width=self.connection_width, fill="#E0E0E0", dash=(3, 3))

        # Рисуем узлы
        for node_id, pos in self.node_positions.items():
            x, y = pos
            color = self.node_colors[node_id]

            # Основной круг узла
            self.visual_canvas.create_oval(
                x - self.node_radius, y - self.node_radius,
                x + self.node_radius, y + self.node_radius,
                fill=color, outline="#333333", width=2
            )

            # Внутренний круг для эффекта
            self.visual_canvas.create_oval(
                x - self.node_radius + 5, y - self.node_radius + 5,
                x + self.node_radius - 5, y + self.node_radius - 5,
                fill=color, outline="#333333", width=1
            )

            # Текст с номером узла
            self.visual_canvas.create_text(x, y, text=f"Node {node_id}", fill="white", font=('Arial', 10, 'bold'))

        # Подписываем лидера
        leader_x, leader_y = self.node_positions[self.hotstuff.current_leader]
        self.visual_canvas.create_text(
            leader_x, leader_y - 50,
            text="👑 ЛИДЕР", fill="#333333", font=('Arial', 12, 'bold')
        )

        # Рисуем легенду на канвасе
        self.visual_canvas.create_text(400, 570, text="HotStuff Консенсус Визуализация", font=('Arial', 12, 'bold'), fill="#555555")

        # Обновляем информационную панель
        self.update_consensus_info()

    def update_consensus_info(self):
        """Обновляет информацию о текущем состоянии консенсуса"""
        info = (
            f"📊 ТЕКУЩЕЕ СОСТОЯНИЕ КОНСЕНСУСА HotStuff\n\n"
            f"👑 Текущий лидер: Node {self.hotstuff.current_leader}\n"
            f"🖥 Количество узлов: {len(self.hotstuff.nodes)}\n"
            f"✅ Минимальный кворум: {((len(self.hotstuff.nodes) * 2) // 3) + 1} голосов\n"
            f"📦 Высота цепочки: {len(self.hotstuff.blockchain)}\n"
            f"⏳ Ожидающих блоков: {len(self.hotstuff.pending_blocks)}\n\n"
            f"🔄 Последний блок: {len(self.hotstuff.blockchain) or 'нет'}\n"
        )

        if self.hotstuff.blockchain:
            last_block = self.hotstuff.blockchain[-1]
            info += (
                f"   - Высота: {last_block.height}\n"
                f"   - Хеш: {last_block.hash[:20]}...\n"
                f"   - Время: {last_block.timestamp.strftime('%H:%M:%S')}\n"
                f"   - Транзакций: {len(last_block.transactions)}\n"
            )

        self.consensus_info.set(info)
        self.update_block_history()

    def update_block_history(self):
        """Обновляет историю блоков в визуализации"""
        # Очистка таблицы
        for item in self.block_history_tree.get_children():
            self.block_history_tree.delete(item)

        # Заполнение таблицы
        for block in reversed(self.hotstuff.blockchain):  # Отображаем в обратном порядке (новые сверху)
            self.block_history_tree.insert("", "end", values=(
                block.height,
                block.hash[:20] + "..." if block.hash else "N/A",
                len(block.transactions),
                block.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            ))

    def start_consensus_animation(self):
        """Запускает анимацию процесса консенсуса"""
        if self.consensus_animation_running:
            return

        self.consensus_animation_running = True
        self.start_animation_button.config(state="disabled")
        self.stop_animation_button.config(state="normal")

        # Запускаем анимацию в отдельном потоке
        self.consensus_animation_thread = threading.Thread(
            target=self.run_consensus_animation,
            daemon=True
        )
        self.consensus_animation_thread.start()

    def stop_consensus_animation(self):
        """Останавливает анимацию процесса консенсуса"""
        self.consensus_animation_running = False
        self.start_animation_button.config(state="normal")
        self.stop_animation_button.config(state="disabled")

    def run_consensus_animation(self):
        """Анимация процесса консенсуса"""
        try:
            # Симулируем несколько раундов консенсуса
            for round_num in range(1, 6):
                if not self.consensus_animation_running:
                    break

                # Обновляем информацию
                self.visual_canvas.after(0, lambda: self.consensus_info.set(
                    f"Раунд {round_num}: Начало процесса консенсуса\n"
                    f"Текущий лидер: Node {self.hotstuff.current_leader}"
                ))

                # Анимация предложения блока
                self.animate_proposal_phase(round_num)

                # Анимация голосования
                self.animate_voting_phase(round_num)

                # Анимация подтверждения
                self.animate_commit_phase(round_num)

                # Ротация лидера
                self.hotstuff.rotate_leader()
                self.visual_canvas.after(0, self.draw_consensus_network)

                # Пауза между раундами
                time.sleep(2)

        except Exception as e:
            logger.error(f"Ошибка в анимации консенсуса: {str(e)}")
        finally:
            self.consensus_animation_running = False
            self.visual_canvas.after(0, lambda: self.start_animation_button.config(state="normal"))
            self.visual_canvas.after(0, lambda: self.stop_animation_button.config(state="disabled"))

    def animate_proposal_phase(self, round_num: int):
        """Анимация фазы предложения блока"""
        leader_id = self.hotstuff.current_leader
        leader_pos = self.node_positions[leader_id]

        # Рисуем предложение блока
        for node_id in self.node_positions:
            if node_id == leader_id:
                continue

            target_pos = self.node_positions[node_id]

            # Анимация отправки предложения
            for i in range(5):
                if not self.consensus_animation_running:
                    return

                # Рисуем линию от лидера к узлу
                self.visual_canvas.after(0, lambda: self.visual_canvas.create_line(
                    leader_pos[0], leader_pos[1],
                    target_pos[0], target_pos[1],
                    arrow=tk.LAST, fill="#9B59B6", width=2, tags=f"proposal_{round_num}"
                ))

                time.sleep(0.2)

                # Удаляем линию
                self.visual_canvas.after(0, lambda: self.visual_canvas.delete(f"proposal_{round_num}"))

        # Обновляем информацию
        self.visual_canvas.after(0, lambda: self.consensus_info.set(
            self.consensus_info.get() + "\nЛидер отправил предложение блока всем узлам"
        ))

    def animate_voting_phase(self, round_num: int):
        """Анимация фазы голосования"""
        leader_id = self.hotstuff.current_leader

        # Каждый узел отправляет голос лидеру
        for node_id in self.node_positions:
            if node_id == leader_id:
                continue

            node_pos = self.node_positions[node_id]
            leader_pos = self.node_positions[leader_id]

            # Анимация отправки голоса
            for i in range(3):
                if not self.consensus_animation_running:
                    return

                # Рисуем линию от узла к лидеру
                self.visual_canvas.after(0, lambda n=node_id: self.visual_canvas.create_line(
                    node_pos[0], node_pos[1],
                    leader_pos[0], leader_pos[1],
                    arrow=tk.LAST, fill="#27AE60", width=2, tags=f"vote_{round_num}_{n}"
                ))

                time.sleep(0.15)

                # Удаляем линию
                self.visual_canvas.after(0, lambda n=node_id: self.visual_canvas.delete(f"vote_{round_num}_{n}"))

        # Обновляем информацию
        self.visual_canvas.after(0, lambda: self.consensus_info.set(
            self.consensus_info.get() + "\nУзлы отправили свои голоса лидеру"
        ))

    def animate_commit_phase(self, round_num: int):
        """Анимация фазы подтверждения блока"""
        leader_id = self.hotstuff.current_leader
        leader_pos = self.node_positions[leader_id]

        # Лидер отправляет подтверждение всем узлам
        for node_id in self.node_positions:
            if node_id == leader_id:
                continue

            target_pos = self.node_positions[node_id]

            # Анимация отправки подтверждения
            for i in range(3):
                if not self.consensus_animation_running:
                    return

                # Рисуем линию от лидера к узлу
                self.visual_canvas.after(0, lambda n=node_id: self.visual_canvas.create_line(
                    leader_pos[0], leader_pos[1],
                    target_pos[0], target_pos[1],
                    arrow=tk.LAST, fill="#E74C3C", width=2, tags=f"commit_{round_num}_{n}"
                ))

                time.sleep(0.15)

                # Удаляем линию
                self.visual_canvas.after(0, lambda n=node_id: self.visual_canvas.delete(f"commit_{round_num}_{n}"))

        # Обновляем информацию
        self.visual_canvas.after(0, lambda: self.consensus_info.set(
            self.consensus_info.get() + "\nЛидер подтвердил блок и отправил подтверждение всем узлам"
        ))

        # Добавляем блок в цепочку (симуляция)
        self.visual_canvas.after(0, lambda: self.consensus_info.set(
            self.consensus_info.get() + f"\nБлок #{len(self.hotstuff.blockchain)+1} добавлен в цепочку!"
        ))

    def clear_visual_canvas(self):
        """Очищает канвас визуализации"""
        self.visual_canvas.delete("all")
        self.draw_consensus_network()

    def on_consensus_state_changed(self):
        """Обновляет визуализацию при изменении состояния консенсуса"""
        self.visual_canvas.after(100, self.draw_consensus_network)
        self.visual_canvas.after(100, self.update_consensus_info)

    def sync_offline_transactions(self):
        """Синхронизирует оффлайн-транзакции"""
        processed_transactions = []

        for user_id, user in self.users.items():
            if user.wallet is not None and user.wallet.pending_transactions:
                for transaction in user.wallet.pending_transactions:
                    # Добавляем каждую транзакцию отдельно в очередь ЦБ
                    self.cb.transaction_queue.append(transaction)

                    # Обновляем таблицу процессов
                    self.update_offline_process_table(
                        transaction.sender_id,
                        transaction.recipient_id,
                        transaction.amount,
                        "Синхронизация оффлайн-транзакции",
                        transaction.id,
                        "В очереди на обработку"
                    )

                    # Обновляем таблицу оффлайн-транзакций
                    self.update_offline_transactions_table(transaction.id, "В очереди на обработку")

                    processed_transactions.append(transaction)

                # Очищаем список ожидающих транзакций после синхронизации
                user.wallet.pending_transactions = []

        if processed_transactions:
            messagebox.showinfo("Успех", f"Синхронизировано {len(processed_transactions)} транзакций.\nОни добавлены в очередь на обработку.")
            self.update_cb_table()
        else:
            messagebox.showinfo("Информация", "Нет транзакций для синхронизации.")

    def process_queue(self):
        """Обрабатывает очередь транзакций по одной транзакции в блоке"""
        if not self.cb.transaction_queue:
            messagebox.showinfo("Информация", "Очередь транзакций пуста.")
            return

        processed_count = 0
        total_transactions = len(self.cb.transaction_queue)

        while self.cb.transaction_queue:
            # Берем первую транзакцию из очереди
            transaction = self.cb.transaction_queue[0]

            # Создаем блок с одной транзакцией
            parent_hash = "genesis" if not self.hotstuff.blockchain else self.hotstuff.blockchain[-1].hash
            new_block = Block(
                height=len(self.hotstuff.blockchain) + 1,
                transactions=[transaction],
                parent_hash=parent_hash
            )

            # Предлагаем блок через HotStuff
            self.hotstuff.propose_block(new_block)

            # Симулируем процесс голосования
            for node in self.hotstuff.nodes:
                node.receive_proposal(new_block)

            votes = sum(1 for node in self.hotstuff.nodes if node.vote(new_block))

            # Проверяем кворум
            if votes >= (len(self.hotstuff.nodes) * 2 // 3) + 1:
                # Блок подтверждён - добавляем в цепочку
                self.hotstuff.commit_block(new_block)

                # Обновляем статус транзакции
                transaction.status = "confirmed"

                # Обновляем балансы пользователей
                if transaction.sender_id in self.users:
                    # Для онлайн-транзакций балансы уже обновлены при создании
                    pass

                if transaction.recipient_id in self.users and self.users[transaction.recipient_id].wallet:
                    self.users[transaction.recipient_id].wallet.confirm_transaction(transaction.id, new_block.hash)

                # Удаляем обработанную транзакцию из очереди
                self.cb.transaction_queue.pop(0)

                # Создаем хеш транзакции
                transaction_hash = hashlib.sha256(
                    f"{transaction.id}{transaction.sender_id}{transaction.recipient_id}{transaction.amount}{transaction.timestamp}".encode()
                ).hexdigest()

                # Записываем хеш в файл
                with open("data/transaction_hashes.txt", "a", encoding="utf-8") as file:
                    file.write(f"Транзакция: {transaction.id}, Хеш: {transaction_hash}\n")

                processed_count += 1

                # Обновляем интерфейс
                self.update_cb_table([{"id": transaction.id, "hash": transaction_hash}])
                self.update_blocks_table()
                self.on_consensus_state_changed()
            else:
                messagebox.showwarning("Предупреждение", f"Консенсус не достигнут для транзакции {transaction.id}. Получено {votes} из {len(self.hotstuff.nodes)} голосов.")
                break

        if processed_count > 0:
            messagebox.showinfo("Успех", f"Обработано {processed_count} из {total_transactions} транзакций.\nКаждая транзакция в отдельном блоке.")
        else:
            messagebox.showinfo("Информация", "Не удалось обработать транзакции.")

    def update_users_table(self):
        """Обновляет таблицу пользователей"""
        # Очистка таблицы
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)

        # Заполнение таблицы
        for user_id, user in self.users.items():
            user_type = "Юридическое лицо" if hasattr(user, 'user_type') and user.user_type == "legal" else "Физическое лицо"
            digital_wallet_status = "Открыт" if hasattr(user, 'has_digital_wallet') and user.has_digital_wallet else "Закрыт"
            offline_wallet_status = "Открыт" if user.wallet is not None else "Закрыт"

            wallet_activation = ""
            wallet_expiry = ""
            offline_wallet_balance = 0

            if user.wallet is not None:
                offline_wallet_balance = user.wallet.get_balance()
                wallet_activation = user.wallet.open_time.strftime("%Y-%m-%d %H:%M:%S")
                wallet_expiry = user.wallet.expiry_time.strftime("%Y-%m-%d %H:%M:%S")

            cash_balance = getattr(user, 'cash_balance', 0)
            digital_balance = getattr(user, 'digital_balance', 0)

            self.users_tree.insert("", "end", values=(
                user_id, user_type, digital_wallet_status, offline_wallet_status,
                offline_wallet_balance, cash_balance, digital_balance,
                wallet_activation, wallet_expiry
            ))

    def update_cb_table(self, transaction_hashes=None):
        """Обновляет таблицу ЦБ"""
        # Очистка таблицы банков
        for item in self.banks_tree.get_children():
            self.banks_tree.delete(item)

        # Заполнение таблицы банков
        for bank_name, bank in self.banks.items():
            self.banks_tree.insert("", "end", values=(bank_name, bank.cash_balance, bank.digital_balance))

        # Обновление метки общего баланса ЦБ
        self.cb_balance_label.config(text=f"Общий баланс цифровых рублей ЦБ: {self.cb.total_balance} ЦР")

        # Очистка таблицы транзакций
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)

        # Заполнение таблицы транзакций
        for transaction in self.cb.transaction_queue:
            self.transactions_tree.insert("", "end", text=transaction.id, values=(
                transaction.sender_id, transaction.recipient_id, transaction.amount,
                getattr(transaction, 'bank', 'Неизвестно'), transaction.status
            ))

        # Обновление таблицы хешей транзакций
        if transaction_hashes:
            for hash_info in transaction_hashes:
                exists = False
                for item in self.hash_tree.get_children():
                    if self.hash_tree.item(item)["text"] == hash_info["id"]:
                        exists = True
                        break
                if not exists:
                    self.hash_tree.insert("", "end", text=hash_info["id"], values=(hash_info["hash"],))

    def update_offline_transactions_table(self, transaction_id=None, status=None):
        """Обновляет таблицу оффлайн-транзакций"""
        if transaction_id and status:
            for item in self.offline_transactions_tree.get_children():
                if self.offline_transactions_tree.item(item)["text"] == transaction_id:
                    self.offline_transactions_tree.set(item, "status", status)
                    self.offline_transactions_tree.set(item, "action_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    break
        else:
            # Очистка таблицы
            for item in self.offline_transactions_tree.get_children():
                self.offline_transactions_tree.delete(item)

            # Заполнение таблицы оффлайн-транзакций
            for user_id, user in self.users.items():
                if user.wallet is not None:
                    wallet_open_time = user.wallet.open_time.strftime("%Y-%m-%d %H:%M:%S")
                    wallet_expiry_time = user.wallet.expiry_time.strftime("%Y-%m-%d %H:%M:%S")

                    for transaction in user.wallet.pending_transactions:
                        transaction_time = transaction.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        action_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        self.offline_transactions_tree.insert("", "end", text=transaction.id, values=(
                            transaction.sender_id, transaction.recipient_id, transaction.amount,
                            transaction_time, wallet_open_time, wallet_expiry_time,
                            "Не обработана", action_time
                        ))

    def update_offline_process_table(self, sender: str, recipient: str, amount: float,
                                    action: str, transaction_id: str, status: str):
        """Обновляет таблицу процессов оффлайн-транзакций"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.offline_process_tree.insert("", "end", values=(
            sender, recipient, amount, action, transaction_id, status, timestamp
        ))

    def update_blocks_table(self):
        """Обновляет таблицу блоков HotStuff"""
        # Очистка таблицы
        for item in self.blocks_tree.get_children():
            self.blocks_tree.delete(item)

        # Заполнение таблицы
        for block in self.hotstuff.blockchain:
            self.blocks_tree.insert("", "end", values=(
                block.height,
                block.hash[:20] + "..." if block.hash else "",
                block.parent_hash[:20] + "..." if block.parent_hash else "",
                len(block.transactions),
                block.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "Подтверждён"
            ))

    def request_emission(self):
        """Запрашивает эмиссию цифровых рублей"""
        bank = self.get_selected_bank()
        try:
            amount = float(self.emission_amount_entry.get())
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма эмиссии должна быть положительной.")
                return
            if bank.cash_balance < amount:
                messagebox.showerror("Ошибка", f"Недостаточно безналичных рублей на счете банка {bank.name}.")
                return
            if bank.request_emission(amount):
                self.update_cb_table()
                messagebox.showinfo("Успех", f"Эмиссия на сумму {amount} ЦР успешно выполнена для банка {bank.name}.")
            else:
                messagebox.showerror("Ошибка", "Не удалось выполнить эмиссию.")
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректная сумма.")

    def get_selected_bank(self):
        """Возвращает выбранный банк"""
        return self.banks[self.bank_combobox.get()]

    def create_users(self):
        """Создаёт новых пользователей"""
        try:
            count = int(self.user_count_entry.get())
            if count <= 0:
                messagebox.showerror("Ошибка", "Количество пользователей должно быть положительным числом.")
                return
            user_type = "legal" if self.user_type_combobox.get() == "Юридические лица" else "individual"
            for i in range(1, count + 1):
                user_id = f"{'legal_' if user_type == 'legal' else 'user'}{i}"
                self.users[user_id] = User(user_id, user_type)
            self.update_users_table()
            # Обновляем списки отправителей, получателей и пользователей
            user_ids = list(self.users.keys())
            self.sender_combobox["values"] = user_ids
            self.recipient_combobox["values"] = user_ids
            self.offline_sender_combobox["values"] = user_ids
            self.offline_recipient_combobox["values"] = user_ids
            self.exchange_user_combobox["values"] = user_ids
            self.offline_wallet_user_combobox["values"] = user_ids
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректное количество пользователей.")

    def create_offline_wallet(self):
        """Создаёт оффлайн-кошелёк для пользователя"""
        user_id = self.offline_wallet_user_combobox.get()
        if not user_id:
            messagebox.showerror("Ошибка", "Выберите пользователя.")
            return
        if user_id not in self.users:
            messagebox.showerror("Ошибка", "Некорректный пользователь.")
            return

        if self.users[user_id].wallet is None:
            self.users[user_id].wallet = Wallet(user_id)
            self.update_offline_process_table(user_id, user_id, 0, "Создание оффлайн-кошелька", "-", "Успешно")
            messagebox.showinfo("Успех", f"Оффлайн-кошелёк создан для пользователя {user_id}.")
        else:
            messagebox.showinfo("Информация", f"У пользователя {user_id} уже есть оффлайн-кошелёк.")
        self.update_users_table()

    def topup_offline_wallet(self):
        """Пополняет оффлайн-кошелёк"""
        user_id = self.offline_wallet_user_combobox.get()
        if not user_id:
            messagebox.showerror("Ошибка", "Выберите пользователя.")
            return
        if user_id not in self.users:
            messagebox.showerror("Ошибка", "Некорректный пользователь.")
            return
        if self.users[user_id].wallet is None:
            messagebox.showerror("Ошибка", f"У пользователя {user_id} нет оффлайн-кошелька.")
            return

        try:
            amount = float(self.topup_amount_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректная сумма.")
            return
        if amount <= 0:
            messagebox.showerror("Ошибка", "Сумма должна быть положительной.")
            return
        if self.users[user_id].digital_balance < amount:
            messagebox.showerror("Ошибка", f"Недостаточно цифровых рублей на кошельке пользователя {user_id}.")
            return

        if self.users[user_id].wallet.add_funds(amount):
            self.users[user_id].digital_balance -= amount
            self.update_offline_process_table(user_id, user_id, amount, "Пополнение оффлайн-кошелька", "-", f"Пополнено на {amount} ЦР")
            messagebox.showinfo("Успех", f"Оффлайн-кошелёк пользователя {user_id} пополнен на {amount} ЦР.")
            self.update_users_table()
        else:
            messagebox.showerror("Ошибка", "Не удалось пополнить оффлайн-кошелёк.")

    def exchange_cash_to_digital(self):
        """Обменивает безналичные рубли на цифровые"""
        user_id = self.exchange_user_combobox.get()
        bank = self.banks[self.exchange_bank_combobox.get()]
        if not user_id:
            messagebox.showerror("Ошибка", "Выберите пользователя.")
            return
        if user_id not in self.users:
            messagebox.showerror("Ошибка", "Некорректный пользователь.")
            return
        try:
            amount = float(self.exchange_amount_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректная сумма.")
            return
        if amount <= 0:
            messagebox.showerror("Ошибка", "Сумма должна быть положительной.")
            return
        if self.users[user_id].cash_balance < amount:
            messagebox.showerror("Ошибка", f"Недостаточно безналичных рублей у пользователя {user_id}.")
            return
        if bank.digital_balance < amount:
            messagebox.showerror("Ошибка", f"Недостаточно цифровых рублей у банка {bank.name}.")
            return
        if bank.exchange_cash_to_digital(user_id, amount):
            self.users[user_id].cash_balance -= amount
            self.users[user_id].digital_balance += amount
            self.users[user_id].has_digital_wallet = True
            self.update_users_table()
            self.update_cb_table()
            messagebox.showinfo("Успех", f"Обмен безналичных рублей на цифровые для пользователя {user_id} на сумму {amount} ЦР выполнен.")
        else:
            messagebox.showerror("Ошибка", "Не удалось выполнить обмен.")

    def create_online_transaction(self):
        """Создаёт онлайн-транзакцию"""
        sender = self.sender_combobox.get()
        recipient = self.recipient_combobox.get()
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректная сумма.")
            return
        if not sender or not recipient:
            messagebox.showerror("Ошибка", "Выберите отправителя и получателя.")
            return
        if sender not in self.users or recipient not in self.users:
            messagebox.showerror("Ошибка", "Некорректные пользователи.")
            return
        if amount <= 0:
            messagebox.showerror("Ошибка", "Сумма должна быть положительной.")
            return
        if self.users[sender].digital_balance < amount:
            messagebox.showerror("Ошибка", f"Недостаточно цифровых рублей на кошельке пользователя {sender}.")
            return

        transaction = Transaction(sender, recipient, amount)
        transaction.sign("private_key")
        bank = list(self.banks.values())[0]
        bank.add_transaction_to_queue(transaction)
        self.users[sender].digital_balance -= amount
        self.users[recipient].digital_balance += amount
        self.update_cb_table()
        self.update_users_table()
        messagebox.showinfo("Успех", f"Онлайн-транзакция {transaction.id} добавлена в очередь на обработку.")

    def create_offline_transaction(self):
        """Создаёт оффлайн-транзакцию"""
        sender = self.offline_sender_combobox.get()
        recipient = self.offline_recipient_combobox.get()
        try:
            amount = float(self.offline_amount_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректная сумма.")
            return
        if not sender or not recipient:
            messagebox.showerror("Ошибка", "Выберите отправителя и получателя.")
            return
        if sender not in self.users or recipient not in self.users:
            messagebox.showerror("Ошибка", "Некорректные пользователи.")
            return
        if amount <= 0:
            messagebox.showerror("Ошибка", "Сумма должна быть положительной.")
            return
        if self.users[sender].wallet is None:
            messagebox.showerror("Ошибка", f"У пользователя {sender} нет оффлайн-кошелька.")
            return
        if self.users[sender].wallet.get_balance() < amount:
            messagebox.showerror("Ошибка", f"Недостаточно цифровых рублей на оффлайн-кошельке пользователя {sender}.")
            return

        transaction = Transaction(sender, recipient, amount)
        transaction.sign("private_key")
        transaction.mark_as_offline()

        if self.users[sender].wallet.withdraw_funds(amount):
            if self.users[sender].wallet.add_offline_transaction(transaction):
                self.update_offline_transactions_table()
                self.update_offline_process_table(sender, recipient, amount, "Создание оффлайн-транзакции", transaction.id, "Создана")
                messagebox.showinfo("Успех", f"Оффлайн-транзакция {transaction.id} создана и сохранена.")
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить транзакцию в очередь.")
        else:
            messagebox.showerror("Ошибка", "Недостаточно средств на оффлайн-кошельке.")
