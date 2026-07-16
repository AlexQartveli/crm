"""Отраслевые типы ресурсов для модуля расписания."""

INDUSTRY_RESOURCE_TYPES: dict[str, str] = {
    "hospitality": "room",
    "medical": "doctor",
    "education": "classroom",
    "logistics": "vehicle",
    "construction": "site",
    "factory": "line",
    "services": "specialist",
    "agriculture": "field",
    "retail": "store",
}

INDUSTRY_SCHEDULE_VIEW: dict[str, str] = {
    "hospitality": "grid",
    "medical": "calendar",
    "education": "calendar",
    "logistics": "timeline",
    "construction": "timeline",
    "factory": "calendar",
    "services": "calendar",
    "agriculture": "calendar",
    "retail": "calendar",
}


def resource_type_for(crm_type: str) -> str:
    return INDUSTRY_RESOURCE_TYPES.get(crm_type, "resource")


def schedule_view_for(crm_type: str) -> str:
    return INDUSTRY_SCHEDULE_VIEW.get(crm_type, "calendar")
