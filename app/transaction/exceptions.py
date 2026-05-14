class InsufficientBalanceError(Exception):
    """
    Raised when a wallet does not have enough balance
    to complete a debit transaction.
    """

    default_message = "Insufficient balance"

    def __init__(self, message=None, balance=None, attempted_amount=None):
        self.message = message or self.default_message
        self.balance = balance
        self.attempted_amount = attempted_amount

        super().__init__(self.message)

    def __str__(self):
        details = self.message

        if self.balance is not None:
            details += f" | Current Balance: {self.balance}"

        if self.attempted_amount is not None:
            details += f" | Attempted Debit: {self.attempted_amount}"

        return details
