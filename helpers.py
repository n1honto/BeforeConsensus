def print_transaction(transaction):
    print(f"Transaction ID: {transaction.id}")
    print(f"Sender: {transaction.sender_id}")
    print(f"Recipient: {transaction.recipient_id}")
    print(f"Amount: {transaction.amount}")
    print(f"Status: {transaction.status}")
