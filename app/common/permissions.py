import logging
from functools import wraps

from common.enums import ADMIN_ACCESS_ROLES, RoleOption
from django.conf import settings
from pykolofinance.phlox.permissions import role_has_permission
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

logger = logging.getLogger(__name__)


EXEMPTED_ROUTE = [
    "wallet.verify_bank_account",
]


def _get_client_ip(request):
    remote_addr = request.META.get("REMOTE_ADDR")
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")

    forwarded_chain = [ip.strip() for ip in x_forwarded_for.split(",") if ip.strip()]

    ip_addresses = []
    if remote_addr:
        ip_addresses.append(remote_addr)

    ip_addresses.extend(forwarded_chain)

    logger.info(
        {
            "remote_addr": remote_addr,
            "forwarded_chain": forwarded_chain,
            "all_ips": ip_addresses,
        }
    )
    return ip_addresses


class IsSuperAdmin(permissions.BasePermission):
    """Allows access only to admin users."""

    message = "Only Super Admins are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "Super Admin")


class IsAdmin(permissions.BasePermission):
    """Allows access only to admin users."""

    message = "Only Admins are authorized to perform this action."

    # def has_permission(self, request, view):
    #     return bool(request.user and request.user.role in ADMIN_ACCESS_ROLES)

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and user.role.lower() in ADMIN_ACCESS_ROLES
        )


class IsAdminViewOnly(permissions.BasePermission):
    """Allows access only to admin users."""

    message = "Only Admins are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "Admin View Only")


class IsAgentUser(permissions.BasePermission):
    """Allows access only to agents."""

    message = "Only Agent are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == "Agent")

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsDivisionalHead(permissions.BasePermission):
    """Allows access only to agents."""

    message = "Only Divisional Head are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated and request.user.role == "Divisional Head"
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsAgentNetworkManager(permissions.BasePermission):
    """Allows access only to Agent Network Manager."""

    message = "Only Divisional Head are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated
            and request.user.role == "Agent Network Manager"
        )


class IsRegionalHead(permissions.BasePermission):
    """Allows access only to Regional Head."""

    message = "Only Divisional Head are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated and request.user.role == "Regional Head"
        )


class IsRelationshipOfficer(permissions.BasePermission):
    """Allows access only to Relationship Officer."""

    message = "Only Divisional Head are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated
            and request.user.role == "Relationship Officer"
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsMerchant(permissions.BasePermission):
    """Allows access only to Merchant."""

    message = "Only Divisional Head are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == "Merchant")

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsSuperAgent(permissions.BasePermission):
    """Allows access only to Super Agent."""

    message = "Only Divisional Head are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated and request.user.role == "Super Agent"
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsHeadOfOperations(permissions.BasePermission):
    """Allows access only to Head of Operations."""

    message = "Only Head of Operations are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated and request.user.role == "Head of Operations"
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsAccounts(permissions.BasePermission):
    """Allows access only to Accounts."""

    message = "Only Accounts are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == "Accounts")

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsReconciliation(permissions.BasePermission):
    """Allows access only to CSO."""

    message = "Only Reconciliation are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated and request.user.role == "Reconciliation"
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsMaComm(permissions.BasePermission):
    """Allows access only to MaComm."""

    message = "Only MaComm are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == "MaComm")

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsCustomerSupportSupervisor(permissions.BasePermission):
    """Allows access only to Customer Support Supervisor."""

    message = "Only Customer Support Supervisor are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated
            and request.user.role == "Customer Support Supervisor"
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsCustomerSupportOfficer(permissions.BasePermission):
    """Allows access only to Customer Support Officer."""

    message = "Only Customer Support Officer are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated
            and request.user.role == "Customer Support Officer"
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsHeadInternalControl(permissions.BasePermission):
    """Allows access only to Head Internal Control."""

    message = "Only Head Internal Control are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated
            and request.user.role == "Head Internal Control"
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsInternalControlOfficer(permissions.BasePermission):
    """Allows access only to Internal Control Officer."""

    message = "Only Internal Control Officer are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated
            and request.user.role == "Internal Control Officer"
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


def permission_required(perm, raise_exception=True):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(cls, request, *args, **kwargs):
            if isinstance(perm, str):
                perms = (perm,)
            else:
                perms = perm

            user = request.user

            def check_perm(user_obj, perm_list):
                return all(
                    role_has_permission(user_obj.role, _perm) for _perm in perm_list
                )

            if user and check_perm(user, perms) is False and raise_exception:
                raise PermissionDenied
            return view_func(cls, request, *args, **kwargs)

        return wrapper

    return decorator


class IsSafeIPAddress(permissions.BasePermission):
    """
    Ensure the request's IP address is on the safe list configured in Django settings.
    """

    @staticmethod
    def get_client_ip(request):
        ip_addresses = [
            request.META.get("REMOTE_ADDR", ""),
            request.META.get("HTTP_X_FORWARDED_FOR", ""),
        ]
        return [addr for addr in ip_addresses if addr]

    def has_permission(self, request, view):
        remote_addresses = self.get_client_ip(request)
        logger.info({"remote_addresses": remote_addresses})
        if settings.DEBUG:
            return True
        return any(
            element in remote_addresses
            for element in settings.ERCAS_INWARD_SAFE_LIST_IPS
        )


class IsSafeInwardIPAddress(permissions.BasePermission):
    """
    Ensure the request's IP address is on the safe list configured in Django settings.
    """

    @staticmethod
    def get_client_ip(request):
        ip_addresses = [
            request.META.get("REMOTE_ADDR", ""),
            request.META.get("HTTP_X_FORWARDED_FOR", ""),
        ]
        return [addr for addr in ip_addresses if addr]

    def has_permission(self, request, view):
        remote_addresses = self.get_client_ip(request)
        logger.info({"remote_addresses": remote_addresses})
        return any(
            element in remote_addresses
            for element in settings.ERCAS_INWARD_SAFE_LIST_IPS
        )


class RoleBasedPermission(permissions.BasePermission):
    message = "You are not authorized to perform this action."

    def has_permission(self, request, view):
        # Ensure user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        role = getattr(request.user, "role", None)
        if not role:
            return False

        role = role.lower()
        merchant_status = getattr(request.user, "merchant_status", None)
        merchant_id = getattr(request.user, "merchant_id", None)

        # Validate role
        valid_roles = [r.value for r in RoleOption]
        if role not in valid_roles:
            return False

        # Build permission key
        permission_key = f"{view.basename}.{view.action}"

        if request.method in ["POST", "PATCH", "PUT", "DELETE"] and merchant_id:
            if (
                merchant_status.strip().lower() != "active"
                and permission_key not in EXEMPTED_ROUTE
            ):
                raise PermissionDenied("Only active merchants can perform this action.")

        from common.permissions_matrix import PERMISSION_MATRIX

        # Get allowed roles
        allowed_roles = PERMISSION_MATRIX.get(permission_key, [])

        # Final check
        return role in allowed_roles


class IsSageCloudIPAddress(permissions.BasePermission):
    def has_permission(self, request, view):
        remote_addresses = _get_client_ip(request)
        logger.info({"remote_addresses": remote_addresses})
        return settings.SAGECLOUD_IP in remote_addresses


class IsCoralPayIPAddress(permissions.BasePermission):
    def has_permission(self, request, view):
        remote_addresses = _get_client_ip(request)
        logger.info({"remote_addresses": remote_addresses})
        return settings.CORALPAY_IP in remote_addresses


class IsPhoenixCoreIPAddress(permissions.BasePermission):
    def has_permission(self, request, view):
        remote_addresses = _get_client_ip(request)
        logger.info({"remote_addresses": remote_addresses})
        return settings.PHOENIX_CORE_IP in remote_addresses


class IsSafePhoenixUserAddress(permissions.BasePermission):
    """
    Ensure the request's IP address is on the safe list for phoenix wallet
    configured in Django settings.
    """

    def has_permission(self, request, view):
        remote_addresses = _get_client_ip(request)
        logger.info({"remote_addresses": remote_addresses})
        return settings.PHOENIX_USER_IP in remote_addresses


class IsSafeCashoutIPAddress(permissions.BasePermission):

    def has_permission(self, request, view):
        remote_addresses = _get_client_ip(request)
        logger.info({"remote_addresses": remote_addresses})
        return settings.CASHOUT_IP in remote_addresses


class CustomBasePermission(permissions.BasePermission):
    message = "Unauthorized"
    allowed_roles = []

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        role = getattr(user, "role", "")
        if role.lower() not in self.allowed_roles:
            return False

        self._check_merchant_status(request, view, user)

        return True

    def _check_merchant_status(self, request, view, user):
        merchant_id = getattr(user, "merchant_id", None)
        merchant_status = getattr(user, "merchant_status", "")

        if not merchant_id or request.method not in ["POST", "PATCH", "PUT", "DELETE"]:
            return

        permission_key = f"{view.basename}.{view.action}"
        is_onboarding_route = permission_key in EXEMPTED_ROUTE
        is_inactive = merchant_status.strip().lower() != "active"

        if is_inactive and not is_onboarding_route:
            raise PermissionDenied("Only active accounts can perform this action.")

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsBackOfficeUser(CustomBasePermission):
    """Allows access only to back office users."""

    allowed_roles = [
        RoleOption.ADMIN.value,
        RoleOption.OPERATIONS.value,
        RoleOption.MERCHANT.value,
        RoleOption.INTERNAL_AUDIT.value,
        RoleOption.COMPLIANCE.value,
        RoleOption.RELATIONSHIP_MANAGER.value,
        RoleOption.SALES_AND_MARKETING.value,
        RoleOption.RECONCILIATION.value,
        RoleOption.CUSTOMER_SUPPORT.value,
        RoleOption.MASS_COMM.value,
        RoleOption.FRAUD_DESK.value,
    ]


class IsAdminUser(CustomBasePermission):
    """Allows access only to Admin users."""

    allowed_roles = [RoleOption.ADMIN.value]


class IsOperationsUser(CustomBasePermission):
    """Allows access only to Operations users."""

    allowed_roles = [RoleOption.OPERATIONS.value]


class IsInternalAuditUser(CustomBasePermission):
    """Allows access only to Internal Audit users."""

    allowed_roles = [RoleOption.INTERNAL_AUDIT.value]


class IsComplianceUser(CustomBasePermission):
    """Allows access only to Compliance users."""

    allowed_roles = [RoleOption.COMPLIANCE.value]


class IsRelationshipManagerUser(CustomBasePermission):
    """Allows access only to Relationship Manager users."""

    allowed_roles = [RoleOption.RELATIONSHIP_MANAGER.value]


class IsSalesAndMarketingUser(CustomBasePermission):
    """Allows access only to Sales and Marketing users."""

    allowed_roles = [RoleOption.SALES_AND_MARKETING.value]


class IsReconciliationUser(CustomBasePermission):
    """Allows access only to Reconciliation users."""

    allowed_roles = [RoleOption.RECONCILIATION.value]


class IsCustomerSupportUser(CustomBasePermission):
    """Allows access only to Customer Support users."""

    allowed_roles = [RoleOption.CUSTOMER_SUPPORT.value]


class IsDeveloperUser(CustomBasePermission):
    """Allows access only to Developer users."""

    allowed_roles = [RoleOption.DEVELOPER.value]


class IsMassCommUser(CustomBasePermission):
    """Allows access only to Mass Comm users."""

    allowed_roles = [RoleOption.MASS_COMM.value]


class IsMerchantUser(CustomBasePermission):
    """Allows access only to Merchant Admin users."""

    allowed_roles = [RoleOption.MERCHANT.value]


class IsMerchantAdminUser(CustomBasePermission):
    """Allows access only to Merchant Admin users."""

    allowed_roles = [RoleOption.MERCHANT_ADMIN.value]


class IsMerchantCustomerSupportUser(CustomBasePermission):
    """Allows access only to Merchant Customer Support users."""

    allowed_roles = [RoleOption.MERCHANT_CUSTOMER_SUPPORT.value]


class IsMerchantOperationsUser(CustomBasePermission):
    """Allows access only to Merchant Operations users."""

    allowed_roles = [RoleOption.MERCHANT_OPERATIONS.value]


class IsMerchantBackOfficeUser(CustomBasePermission):
    """Allows access only to Merchant back office users."""

    allowed_roles = [
        RoleOption.MERCHANT.value,
        RoleOption.DEVELOPER.value,
        RoleOption.MERCHANT_ADMIN.value,
        RoleOption.MERCHANT_CUSTOMER_SUPPORT.value,
        RoleOption.MERCHANT_OPERATIONS.value,
    ]


class IsFraudDeskUser(CustomBasePermission):
    """Allows access only to Admin users."""

    allowed_roles = [RoleOption.FRAUD_DESK.value]
