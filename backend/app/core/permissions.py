"""Роли и права доступа (AmoCRM / Bitrix24 стиль)."""

from __future__ import annotations

import re
from typing import Iterable

# --- Роли ---
ROLE_ADMIN = "admin"
ROLE_DIRECTOR = "director"
ROLE_SALES = "sales"
ROLE_OPERATOR = "operator"
ROLE_WAREHOUSE = "warehouse"
ROLE_ACCOUNTANT = "accountant"

ALL_ROLES = (
    ROLE_ADMIN,
    ROLE_DIRECTOR,
    ROLE_SALES,
    ROLE_OPERATOR,
    ROLE_WAREHOUSE,
    ROLE_ACCOUNTANT,
)

ROLE_LABELS: dict[str, dict[str, str]] = {
    ROLE_ADMIN: {"ru": "Администратор", "en": "Administrator", "ka": "ადმინისტრატორი"},
    ROLE_DIRECTOR: {"ru": "Руководитель", "en": "Director", "ka": "ხელმძღვანელი"},
    ROLE_SALES: {"ru": "Менеджер по продажам", "en": "Sales manager", "ka": "გაყიდვების მენეჯერი"},
    ROLE_OPERATOR: {"ru": "Оператор поддержки", "en": "Support operator", "ka": "ოპერატორი"},
    ROLE_WAREHOUSE: {"ru": "Кладовщик", "en": "Warehouse manager", "ka": "საწყობის მენეჯერი"},
    ROLE_ACCOUNTANT: {"ru": "Бухгалтер", "en": "Accountant", "ka": "ბუღალტერი"},
}

# --- Права ---
PERM_DASHBOARD = "dashboard.view"

PERM_CRM_LEADS_VIEW = "crm.leads.view"
PERM_CRM_LEADS_MANAGE = "crm.leads.manage"
PERM_CRM_DEALS_VIEW = "crm.deals.view"
PERM_CRM_DEALS_MANAGE = "crm.deals.manage"
PERM_CRM_CONTACTS_VIEW = "crm.contacts.view"
PERM_CRM_CONTACTS_MANAGE = "crm.contacts.manage"
PERM_CRM_COMPANIES_VIEW = "crm.companies.view"
PERM_CRM_COMPANIES_MANAGE = "crm.companies.manage"

PERM_WAREHOUSE_PRODUCTS_VIEW = "warehouse.products.view"
PERM_WAREHOUSE_PRODUCTS_MANAGE = "warehouse.products.manage"
PERM_WAREHOUSE_STOCKS_VIEW = "warehouse.stocks.view"
PERM_WAREHOUSE_MOVEMENTS_VIEW = "warehouse.movements.view"
PERM_WAREHOUSE_MOVEMENTS_MANAGE = "warehouse.movements.manage"

PERM_ACCOUNTING_VIEW = "accounting.view"
PERM_ACCOUNTING_MANAGE = "accounting.manage"
PERM_ACCOUNTING_SETTINGS = "accounting.settings"

PERM_MESSAGING_INBOX = "messaging.inbox"
PERM_MESSAGING_INTEGRATIONS = "messaging.integrations"

PERM_AUTOMATIONS_VIEW = "automations.view"
PERM_AUTOMATIONS_MANAGE = "automations.manage"

PERM_USERS_MANAGE = "users.manage"

ALL_PERMISSIONS = frozenset({
    PERM_DASHBOARD,
    PERM_CRM_LEADS_VIEW, PERM_CRM_LEADS_MANAGE,
    PERM_CRM_DEALS_VIEW, PERM_CRM_DEALS_MANAGE,
    PERM_CRM_CONTACTS_VIEW, PERM_CRM_CONTACTS_MANAGE,
    PERM_CRM_COMPANIES_VIEW, PERM_CRM_COMPANIES_MANAGE,
    PERM_WAREHOUSE_PRODUCTS_VIEW, PERM_WAREHOUSE_PRODUCTS_MANAGE,
    PERM_WAREHOUSE_STOCKS_VIEW,
    PERM_WAREHOUSE_MOVEMENTS_VIEW, PERM_WAREHOUSE_MOVEMENTS_MANAGE,
    PERM_ACCOUNTING_VIEW, PERM_ACCOUNTING_MANAGE, PERM_ACCOUNTING_SETTINGS,
    PERM_MESSAGING_INBOX, PERM_MESSAGING_INTEGRATIONS,
    PERM_AUTOMATIONS_VIEW, PERM_AUTOMATIONS_MANAGE,
    PERM_USERS_MANAGE,
})

ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    ROLE_ADMIN: ALL_PERMISSIONS,
    ROLE_DIRECTOR: ALL_PERMISSIONS - {PERM_USERS_MANAGE, PERM_ACCOUNTING_SETTINGS},
    ROLE_SALES: frozenset({
        PERM_DASHBOARD,
        PERM_CRM_LEADS_VIEW, PERM_CRM_LEADS_MANAGE,
        PERM_CRM_DEALS_VIEW, PERM_CRM_DEALS_MANAGE,
        PERM_CRM_CONTACTS_VIEW, PERM_CRM_CONTACTS_MANAGE,
        PERM_CRM_COMPANIES_VIEW, PERM_CRM_COMPANIES_MANAGE,
        PERM_MESSAGING_INBOX,
        PERM_AUTOMATIONS_VIEW,
    }),
    ROLE_OPERATOR: frozenset({
        PERM_DASHBOARD,
        PERM_CRM_LEADS_VIEW, PERM_CRM_LEADS_MANAGE,
        PERM_CRM_CONTACTS_VIEW, PERM_CRM_CONTACTS_MANAGE,
        PERM_MESSAGING_INBOX,
    }),
    ROLE_WAREHOUSE: frozenset({
        PERM_DASHBOARD,
        PERM_WAREHOUSE_PRODUCTS_VIEW, PERM_WAREHOUSE_PRODUCTS_MANAGE,
        PERM_WAREHOUSE_STOCKS_VIEW,
        PERM_WAREHOUSE_MOVEMENTS_VIEW, PERM_WAREHOUSE_MOVEMENTS_MANAGE,
    }),
    ROLE_ACCOUNTANT: frozenset({
        PERM_DASHBOARD,
        PERM_ACCOUNTING_VIEW, PERM_ACCOUNTING_MANAGE, PERM_ACCOUNTING_SETTINGS,
        PERM_CRM_CONTACTS_VIEW,
        PERM_CRM_COMPANIES_VIEW,
    }),
}


def get_role_permissions(role: str) -> frozenset[str]:
    return ROLE_PERMISSIONS.get(role, frozenset())


def has_permission(role: str, permission: str) -> bool:
    return permission in get_role_permissions(role)


def has_any_permission(role: str, permissions: Iterable[str]) -> bool:
    perms = get_role_permissions(role)
    return any(p in perms for p in permissions)


# --- Маршрут → право ---
_PUBLIC_PREFIXES = (
    "/api/health",
    "/api/auth/login",
    "/api/auth/register",
    "/api/auth/crm-types",
    "/api/messaging/webhooks/",
)

_ROUTE_RULES: list[tuple[re.Pattern[str], dict[str, str]]] = [
    (re.compile(r"^/api/dashboard$"), {"GET": PERM_DASHBOARD}),

    (re.compile(r"^/api/crm/leads$"), {"GET": PERM_CRM_LEADS_VIEW, "POST": PERM_CRM_LEADS_MANAGE}),
    (re.compile(r"^/api/crm/leads/\d+$"), {
        "GET": PERM_CRM_LEADS_VIEW, "PATCH": PERM_CRM_LEADS_MANAGE, "DELETE": PERM_CRM_LEADS_MANAGE,
    }),

    (re.compile(r"^/api/crm/deals$"), {"GET": PERM_CRM_DEALS_VIEW, "POST": PERM_CRM_DEALS_MANAGE}),
    (re.compile(r"^/api/crm/deals/\d+$"), {
        "GET": PERM_CRM_DEALS_VIEW, "PATCH": PERM_CRM_DEALS_MANAGE, "DELETE": PERM_CRM_DEALS_MANAGE,
    }),

    (re.compile(r"^/api/crm/contacts$"), {"GET": PERM_CRM_CONTACTS_VIEW, "POST": PERM_CRM_CONTACTS_MANAGE}),
    (re.compile(r"^/api/crm/contacts/\d+$"), {
        "GET": PERM_CRM_CONTACTS_VIEW, "PATCH": PERM_CRM_CONTACTS_MANAGE, "DELETE": PERM_CRM_CONTACTS_MANAGE,
    }),

    (re.compile(r"^/api/crm/companies$"), {"GET": PERM_CRM_COMPANIES_VIEW, "POST": PERM_CRM_COMPANIES_MANAGE}),
    (re.compile(r"^/api/crm/companies/\d+$"), {
        "GET": PERM_CRM_COMPANIES_VIEW, "PATCH": PERM_CRM_COMPANIES_MANAGE, "DELETE": PERM_CRM_COMPANIES_MANAGE,
    }),

    (re.compile(r"^/api/warehouse/products$"), {
        "GET": PERM_WAREHOUSE_PRODUCTS_VIEW, "POST": PERM_WAREHOUSE_PRODUCTS_MANAGE,
    }),
    (re.compile(r"^/api/warehouse/products/\d+$"), {
        "GET": PERM_WAREHOUSE_PRODUCTS_VIEW,
        "PATCH": PERM_WAREHOUSE_PRODUCTS_MANAGE,
        "DELETE": PERM_WAREHOUSE_PRODUCTS_MANAGE,
    }),
    (re.compile(r"^/api/warehouse/warehouses$"), {
        "GET": PERM_WAREHOUSE_STOCKS_VIEW, "POST": PERM_WAREHOUSE_PRODUCTS_MANAGE,
    }),
    (re.compile(r"^/api/warehouse/warehouses/\d+$"), {"PATCH": PERM_WAREHOUSE_PRODUCTS_MANAGE}),
    (re.compile(r"^/api/warehouse/stocks$"), {"GET": PERM_WAREHOUSE_STOCKS_VIEW}),
    (re.compile(r"^/api/warehouse/movements$"), {
        "GET": PERM_WAREHOUSE_MOVEMENTS_VIEW, "POST": PERM_WAREHOUSE_MOVEMENTS_MANAGE,
    }),

    (re.compile(r"^/api/accounting/invoices$"), {
        "GET": PERM_ACCOUNTING_VIEW, "POST": PERM_ACCOUNTING_MANAGE,
    }),
    (re.compile(r"^/api/accounting/invoices/\d+/sync$"), {"POST": PERM_ACCOUNTING_MANAGE}),
    (re.compile(r"^/api/accounting/invoices/\d+/activate$"), {"POST": PERM_ACCOUNTING_MANAGE}),
    (re.compile(r"^/api/accounting/settings$"), {"GET": PERM_ACCOUNTING_VIEW, "POST": PERM_ACCOUNTING_SETTINGS}),
    (re.compile(r"^/api/accounting/rsge/auth$"), {"POST": PERM_ACCOUNTING_SETTINGS}),
    (re.compile(r"^/api/accounting/rsge/check-vat$"), {"POST": PERM_ACCOUNTING_VIEW}),

    (re.compile(r"^/api/messaging/conversations$"), {"GET": PERM_MESSAGING_INBOX}),
    (re.compile(r"^/api/messaging/conversations/\d+$"), {"GET": PERM_MESSAGING_INBOX}),
    (re.compile(r"^/api/messaging/conversations/\d+/messages$"), {
        "GET": PERM_MESSAGING_INBOX, "POST": PERM_MESSAGING_INBOX,
    }),
    (re.compile(r"^/api/messaging/conversations/\d+/read$"), {"PATCH": PERM_MESSAGING_INBOX}),
    (re.compile(r"^/api/messaging/conversations/\d+/link$"), {"PATCH": PERM_MESSAGING_INBOX}),
    (re.compile(r"^/api/messaging/conversations/\d+/convert-contact$"), {"POST": PERM_MESSAGING_INBOX}),
    (re.compile(r"^/api/messaging/sync-crm$"), {"POST": PERM_MESSAGING_INTEGRATIONS}),
    (re.compile(r"^/api/messaging/calls$"), {"GET": PERM_MESSAGING_INBOX}),
    (re.compile(r"^/api/messaging/settings$"), {"GET": PERM_MESSAGING_INTEGRATIONS, "POST": PERM_MESSAGING_INTEGRATIONS}),
    (re.compile(r"^/api/messaging/sync/(whatsapp|messenger|telegram)$"), {"POST": PERM_MESSAGING_INTEGRATIONS}),

    (re.compile(r"^/api/automations/bots$"), {"GET": PERM_AUTOMATIONS_VIEW, "POST": PERM_AUTOMATIONS_MANAGE}),
    (re.compile(r"^/api/automations/bots/\d+$"), {
        "GET": PERM_AUTOMATIONS_VIEW, "PATCH": PERM_AUTOMATIONS_MANAGE, "DELETE": PERM_AUTOMATIONS_MANAGE,
    }),
    (re.compile(r"^/api/automations/bots/\d+/toggle$"), {"PATCH": PERM_AUTOMATIONS_MANAGE}),
    (re.compile(r"^/api/automations/templates$"), {"GET": PERM_AUTOMATIONS_VIEW, "POST": PERM_AUTOMATIONS_MANAGE}),
    (re.compile(r"^/api/automations/templates/\d+$"), {
        "PATCH": PERM_AUTOMATIONS_MANAGE, "DELETE": PERM_AUTOMATIONS_MANAGE,
    }),
    (re.compile(r"^/api/automations/logs$"), {"GET": PERM_AUTOMATIONS_VIEW}),

    (re.compile(r"^/api/auth/users$"), {"GET": PERM_USERS_MANAGE, "POST": PERM_USERS_MANAGE}),
    (re.compile(r"^/api/auth/users/\d+$"), {
        "GET": PERM_USERS_MANAGE, "PATCH": PERM_USERS_MANAGE, "DELETE": PERM_USERS_MANAGE,
    }),
    (re.compile(r"^/api/auth/roles$"), {"GET": PERM_USERS_MANAGE}),
    (re.compile(r"^/api/auth/profile$"), {"GET": "__authenticated__", "PATCH": "__authenticated__"}),
    (re.compile(r"^/api/auth/change-password$"), {"POST": "__authenticated__"}),
    (re.compile(r"^/api/tenant/me$"), {"GET": "__authenticated__", "PATCH": "__authenticated__"}),
]

_AUTH_ONLY_PATHS = (
    "/api/auth/me",
    "/api/auth/logout",
    "/api/auth/crm-config",
)


def is_public_path(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in _PUBLIC_PREFIXES)


def is_auth_only_path(path: str) -> bool:
    return path in _AUTH_ONLY_PATHS


def resolve_permission(method: str, path: str) -> str | None:
    """None = публичный или только авторизация без конкретного права."""
    if is_public_path(path) or method == "OPTIONS":
        return None
    if is_auth_only_path(path):
        return "__authenticated__"

    for pattern, methods in _ROUTE_RULES:
        if pattern.match(path):
            return methods.get(method.upper())
    return "__deny__"


def permission_allowed(role: str, permission: str | None) -> bool:
    if permission is None:
        return True
    if permission == "__authenticated__":
        return True
    if permission == "__deny__":
        return False
    return has_permission(role, permission)
