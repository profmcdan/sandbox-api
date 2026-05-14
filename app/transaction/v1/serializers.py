from django.db import transaction
from rest_framework import serializers

from transaction.models import Transaction, Wallet


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'
        extra_kwargs = {
            'tid': {'read_only': True},
            'balance': {'read_only': True},
        }


class CreateTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id', 'wallet', 'amount', 'reference', 'status',
            'transaction_class', 'transaction_mode', 'narration', 'session_id',
            'sender_bank_name', 'sender_name', 'sender_account_number',
        ]
        extra_kwargs = {
            'reference': {'read_only': True},
            'status': {'read_only': True},
        }

    def validate(self, attrs):
        attrs = super().validate(attrs)
        wallet = attrs.get('wallet')
        if attrs.get('transaction_mode') == 'debit':
            if wallet.balance < attrs.get('amount'):
                raise serializers.ValidationError({'amount': 'Not enough balance'})
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(id=validated_data['wallet'].id)
            tx = Transaction.objects.create(**validated_data)
            tx.old_balance = wallet.balance
            if validated_data.get('transaction_mode') == 'credit':
                wallet.credit(validated_data['amount'])
                tx.new_balance = wallet.balance + validated_data['amount']
            else:
                wallet.debit(validated_data['amount'])
                tx.new_balance = wallet.balance - validated_data['amount']
            tx.status = 'successful'
            tx.save()
        return tx


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
