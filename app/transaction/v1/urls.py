from django.urls import include, path
from rest_framework.routers import DefaultRouter

from transaction.v1.views import TransactionViewSets, WalletViewSets

app_name = "transactions"

router = DefaultRouter()
router.register("wallets", WalletViewSets, basename="wallets")
router.register("transactions", TransactionViewSets, basename="transactions")

urlpatterns = [
    path("", include(router.urls)),
]
