from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters

from transaction.models import Wallet, Transaction
from transaction.v1.filters import WalletFilter, TransactionFilter
from transaction.v1.serializers import WalletSerializer, CreateTransactionSerializer, TransactionSerializer


class WalletViewSets(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    http_method_names = ["get", "post"]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = WalletFilter
    search_fields = [
        "business_name",
        "user_id",
    ]


class TransactionViewSets(viewsets.ModelViewSet):
    queryset = Transaction.objects.select_related('wallet').all()
    serializer_class = TransactionSerializer
    http_method_names = ["get", "post"]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = TransactionFilter
    search_fields = [
        "reference",
        "session_id",
    ]

    def get_serializer_class(self):
        if self.action == "create":
            return CreateTransactionSerializer
        return super().get_serializer_class()
