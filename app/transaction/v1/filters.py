from common.filter import DateFilter
from transaction.models import Wallet, Transaction


class WalletFilter(DateFilter):
    class Meta:
        model = Wallet
        fields = ["user_id", "tid"]


class TransactionFilter(DateFilter):
    class Meta:
        model = Transaction
        fields = ["wallet", "transaction_class", "transaction_mode", "status"]
