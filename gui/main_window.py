import tkinter as tk
from tkinter import ttk, messagebox, font
from core.central_bank import CentralBank
from core.financial_organization import FinancialOrganization
from core.user import User
from core.transaction import Transaction
from core.wallet import Wallet
import hashlib
import os
from datetime import datetime, timedelta

class DigitalRubleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Цифровой рубль — Симулятор")

        # Увеличиваем шрифт по умолчанию
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=12)

        # Создаем стили для виджетов
        self.style = ttk.Style()
        self.style.configure("TButton", font=('Arial', 12))
        self.style.configure("TLabel", font=('Arial', 12))
        self.style.configure("TCombobox", font=('Arial', 12))
        self.style.configure("TEntry", font=('Arial', 12))

        # Очистка файла с хешами транзакций при запуске программы
        with open("transaction_hashes.txt", "w", encoding="utf-8") as file:
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

    def create_control_widgets(self):
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
        # Создание таблицы пользователей
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

        # Добавление скроллбара
        scrollbar = ttk.Scrollbar(self.users_tree, orient="vertical", command=self.users_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.users_tree.configure(yscrollcommand=scrollbar.set)

    def create_cb_table(self):
        # Метка для таблицы банков
        self.banks_label = ttk.Label(self.cb_tab, text="Балансы банков:", font=('Arial', 12, 'bold'))
        self.banks_label.pack(anchor="w", padx=10, pady=(10, 0))

        # Создание таблицы банков
        self.banks_tree = ttk.Treeview(self.cb_tab, columns=("bank_name", "cash_balance", "digital_balance"), show="headings", height=10)
        self.banks_tree.heading("bank_name", text="Название банка")
        self.banks_tree.heading("cash_balance", text="Безналичный баланс (РУБ)")
        self.banks_tree.heading("digital_balance", text="Цифровой баланс (ЦР)")
        self.banks_tree.column("bank_name", width=150)
        self.banks_tree.column("cash_balance", width=150)
        self.banks_tree.column("digital_balance", width=150)
        self.banks_tree.pack(fill="both", expand=True, pady=(0, 10))

        # Метка для очереди транзакций
        self.queue_label = ttk.Label(self.cb_tab, text="Очередь транзакций на обработку:", font=('Arial', 12, 'bold'))
        self.queue_label.pack(anchor="w", padx=10, pady=(10, 0))

        # Создание таблицы транзакций
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

        # Метка для хешей транзакций
        self.hash_label = ttk.Label(self.cb_tab, text="Хеши обработанных транзакций:", font=('Arial', 12, 'bold'))
        self.hash_label.pack(anchor="w", padx=10, pady=(10, 0))

        # Создание таблицы хешей транзакций
        self.hash_tree = ttk.Treeview(self.cb_tab, columns=("hash",), show="headings", height=10)
        self.hash_tree.heading("hash", text="Хеш")
        self.hash_tree.heading("#0", text="ID транзакции")
        self.hash_tree.column("#0", width=150)
        self.hash_tree.column("hash", width=400)
        self.hash_tree.pack(fill="both", expand=True, pady=(0, 0))

        # Добавление метки для общего баланса ЦБ
        self.cb_balance_label = ttk.Label(self.cb_tab, text=f"Общий баланс цифровых рублей ЦБ: {self.cb.total_balance} ЦР", font=('Arial', 12))
        self.cb_balance_label.pack(pady=(10, 0))

    def create_offline_transactions_table(self):
        # Метка для таблицы оффлайн-транзакций
        self.offline_label = ttk.Label(self.offline_tab, text="Оффлайн-транзакции:", font=('Arial', 12, 'bold'))
        self.offline_label.pack(anchor="w", padx=10, pady=(10, 0))

        # Создание таблицы оффлайн-транзакций
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

        # Добавление скроллбара
        scrollbar = ttk.Scrollbar(self.offline_transactions_tree, orient="vertical", command=self.offline_transactions_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.offline_transactions_tree.configure(yscrollcommand=scrollbar.set)

    def create_offline_process_table(self):
        # Метка для таблицы процессов оффлайн-транзакций
        self.offline_process_label = ttk.Label(self.offline_process_tab, text="Процессы оффлайн-транзакций:", font=('Arial', 12, 'bold'))
        self.offline_process_label.pack(anchor="w", padx=10, pady=(10, 0))

        # Создание таблицы процессов оффлайн-транзакций
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

        # Добавление скроллбара
        scrollbar = ttk.Scrollbar(self.offline_process_tree, orient="vertical", command=self.offline_process_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.offline_process_tree.configure(yscrollcommand=scrollbar.set)

    def update_users_table(self):
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

    def update_offline_process_table(self, sender, recipient, amount, action, transaction_id, status):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.offline_process_tree.insert("", "end", values=(
            sender, recipient, amount, action, transaction_id, status, timestamp
        ))

    def get_selected_bank(self):
        return self.banks[self.bank_combobox.get()]

    def request_emission(self):
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

    def create_users(self):
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
            # Обновляем списки отправителей, получателей и пользователей для пополнения
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

    def sync_offline_transactions(self):
        for user_id, user in self.users.items():
            if user.wallet is not None and user.wallet.pending_transactions:
                for transaction in user.wallet.pending_transactions:
                    # Добавляем транзакцию в очередь ЦБ
                    bank = list(self.banks.values())[0]
                    bank.add_transaction_to_queue(transaction)

                    # Обновляем статус в таблице процессов
                    self.update_offline_process_table(
                        transaction.sender_id,
                        transaction.recipient_id,
                        transaction.amount,
                        "Синхронизация оффлайн-транзакции",
                        transaction.id,
                        "Синхронизирована"
                    )

                    # Обновляем статус в таблице транзакций
                    self.update_offline_transactions_table(transaction.id, "Обработана")

                # Очищаем список ожидающих транзакций после синхронизации
                user.wallet.pending_transactions = []

                messagebox.showinfo("Успех", f"Оффлайн-транзакции пользователя {user_id} синхронизированы.")

        self.update_cb_table()
        self.update_users_table()

    def process_queue(self):
        if not self.cb.transaction_queue:
            messagebox.showinfo("Информация", "Очередь транзакций пуста.")
            return
        transaction_hashes = []
        for transaction in self.cb.transaction_queue:
            transaction_hash = hashlib.sha256(f"{transaction.id}{transaction.sender_id}{transaction.recipient_id}{transaction.amount}{transaction.timestamp}".encode()).hexdigest()
            transaction_hashes.append({"id": transaction.id, "hash": transaction_hash})

            # Если это оффлайн-транзакция, обновляем балансы пользователей
            if hasattr(transaction, 'is_offline') and transaction.is_offline:
                if transaction.sender_id in self.users and transaction.recipient_id in self.users:
                    self.users[transaction.recipient_id].digital_balance += transaction.amount

        self.cb.transaction_queue.clear()
        self.update_cb_table(transaction_hashes)
        self.write_hashes_to_file(transaction_hashes)
        messagebox.showinfo("Успех", "Очередь транзакций обработана. Хеши транзакций сохранены.")

    def write_hashes_to_file(self, transaction_hashes):
        """Запись хешей транзакций в файл."""
        with open("transaction_hashes.txt", "a", encoding="utf-8") as file:
            for hash_info in transaction_hashes:
                file.write(f"Транзакция: {hash_info['id']}, Хеш: {hash_info['hash']}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = DigitalRubleApp(root)
    root.mainloop()
