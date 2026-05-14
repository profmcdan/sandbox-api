from enum import Enum


class CustomEnum(Enum):
    @classmethod
    def values(cls):
        return [c.value for c in cls]

    @classmethod
    def choices(cls):
        return [(c.value, c.value) for c in cls]


class RoleOption(CustomEnum):
    ADMIN = "admin"
    MERCHANT = "merchant"
    RECONCILIATION = "reconciliation"
    FRAUD_DESK = "frauddesk"
    SALES_AND_MARKETING = "sales and marketing"
    CUSTOMER_SUPPORT = "customer support"
    OPERATIONS = "operations"
    RELATIONSHIP_MANAGER = "relationship manager"
    INTERNAL_AUDIT = "internal audit"
    COMPLIANCE = "compliance"
    DEVELOPER = "developer"
    HEAD_OPERATIONS = "head operations"
    HEAD_RECONCILIATION = "head reconciliation"
    MASS_COMM = "mass comm"
    MERCHANT_ADMIN = "merchantadmin"
    MERCHANT_CUSTOMER_SUPPORT = "merchant customer support"
    MERCHANT_OPERATIONS = "merchant operations"


MERCHANT_SCOPED_ROLES = {
    RoleOption.MERCHANT.value,
    RoleOption.DEVELOPER.value,
    RoleOption.MERCHANT_ADMIN.value,
    RoleOption.MERCHANT_CUSTOMER_SUPPORT.value,
    RoleOption.MERCHANT_OPERATIONS.value,
}

ADMIN_ACCESS_ROLES = {
    RoleOption.ADMIN.value,
    RoleOption.RECONCILIATION.value,
    RoleOption.FRAUD_DESK.value,
    RoleOption.SALES_AND_MARKETING.value,
    RoleOption.RELATIONSHIP_MANAGER.value,
    RoleOption.INTERNAL_AUDIT.value,
    RoleOption.COMPLIANCE.value,
    RoleOption.CUSTOMER_SUPPORT.value,
    RoleOption.OPERATIONS.value,
    RoleOption.HEAD_OPERATIONS.value,
    RoleOption.HEAD_RECONCILIATION.value,
    RoleOption.MASS_COMM.value,
}
