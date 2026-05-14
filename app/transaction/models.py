from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db.models import F
from django.core.validators import MinValueValidator
from django.db import models, transaction

from common.kgs import generate_uuid
from common.models import AuditableModel
from transaction.enums import TRANSACTION_CLASS_CHOICES, TRANSACTION_MODE_CHOICES, TRANSACTION_STATUS_CHOICES
from transaction.exceptions import InsufficientBalanceError


class Wallet(AuditableModel):
    user_id = models.CharField(max_length=100, db_index=True)
    business_name = models.CharField(max_length=100, db_index=True)
    tid = models.CharField(max_length=100, db_index=True, unique=True, default=generate_uuid)
    balance = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(0)], default=Decimal('0.00'))

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.user_id

    @transaction.atomic
    def credit(self, amount: Decimal):
        if amount <= 0:
            raise ValidationError("Credit amount must be greater than 0")

        updated = Wallet.objects.filter(
            pk=self.pk
        ).update(
            balance=F("balance") + amount
        )

        if not updated:
            raise ValidationError("Wallet not found")

        self.refresh_from_db(fields=["balance"])
        return self.balance

    @transaction.atomic
    def debit(self, amount: Decimal):
        if amount <= 0:
            raise ValidationError("Debit amount must be greater than 0")

        # Atomic balance check + update
        updated = Wallet.objects.filter(
            pk=self.pk,
            balance__gte=amount
        ).update(
            balance=F("balance") - amount
        )

        if not updated:
            raise InsufficientBalanceError(balance=self.balance, attempted_amount=amount)

        self.refresh_from_db(fields=["balance"])
        return self.balance



class Transaction(AuditableModel):
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name='transactions')
    amount = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(0)])
    transaction_class = models.CharField(max_length=20, choices=TRANSACTION_CLASS_CHOICES, db_index=True)
    transaction_mode = models.CharField(max_length=20, choices=TRANSACTION_MODE_CHOICES, db_index=True)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, db_index=True, default='pending')
    narration = models.TextField(blank=True, null=True)
    session_id = models.CharField(max_length=100, db_index=True, unique=True, null=True)
    reference = models.CharField(max_length=100, db_index=True, unique=True, default=generate_uuid)
    sender_bank_name = models.CharField(max_length=100, null=True)
    sender_name = models.CharField(max_length=100, null=True)
    receiver_name = models.CharField(max_length=100, null=True)
    sender_account_number = models.CharField(max_length=100, null=True)
    receiver_account_number = models.CharField(max_length=100, null=True)
    old_balance = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(0)], default=Decimal('0.00'))
    new_balance = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(0)], default=Decimal('0.00'))

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.reference

