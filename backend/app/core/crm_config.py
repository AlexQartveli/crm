"""Отраслевая конфигурация CRM: модули, подписи, поля, этапы."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.core.crm_types import CRM_TYPES, DEFAULT_CRM_TYPE, get_crm_type


@dataclass(frozen=True)
class Label3:
    ru: str
    en: str
    ka: str

    def pick(self, locale: str) -> str:
        if locale == "en":
            return self.en
        if locale == "ka":
            return self.ka
        return self.ru


@dataclass(frozen=True)
class FieldOption:
    id: str
    label: Label3


@dataclass(frozen=True)
class FieldDef:
    key: str
    type: str  # text, number, date, select, textarea, phone, email
    label: Label3
    required: bool = False
    show_in_list: bool = False
    options: tuple[FieldOption, ...] = ()
    placeholder: Label3 | None = None


@dataclass(frozen=True)
class StatusDef:
    key: str
    label: Label3
    color: str


@dataclass(frozen=True)
class ServiceDef:
    id: str
    label: Label3


@dataclass(frozen=True)
class CrmTypeConfig:
    crm_type: str
    modules: tuple[str, ...]
    labels: dict[str, Label3]
    fields: dict[str, tuple[FieldDef, ...]]
    deal_stages: tuple[StatusDef, ...]
    lead_statuses: tuple[StatusDef, ...]
    services: tuple[ServiceDef, ...] = ()
    hide_base_fields: dict[str, tuple[str, ...]] = field(default_factory=dict)


L = Label3

# --- Общие опции ---

GEO_CITIES = (
    FieldOption("tbilisi", L("Тбилиси", "Tbilisi", "თბილისი")),
    FieldOption("batumi", L("Батуми", "Batumi", "ბათუმი")),
    FieldOption("kutaisi", L("Кутаиси", "Kutaisi", "ქუთაისი")),
    FieldOption("rustavi", L("Рустави", "Rustavi", "რუსთავი")),
    FieldOption("kakheti", L("Кахети", "Kakheti", "კახეთი")),
    FieldOption("other", L("Другой", "Other", "სხვა")),
)

PAYMENT_PLANS = (
    FieldOption("full", L("Полная оплата", "Full payment", "სრული გადახდა")),
    FieldOption("semester", L("По семестрам", "Per semester", "სემესტრულად")),
    FieldOption("monthly", L("Ежемесячно", "Monthly", "ყოველთვიურად")),
)

EDUCATION_PROGRAMS = (
    FieldOption("school", L("Школа", "School", "სკოლა")),
    FieldOption("college", L("Колледж", "College", "კოლეჯი")),
    FieldOption("university", L("Университет", "University", "უნივერსიტეტი")),
    FieldOption("courses", L("Курсы", "Courses", "კურსები")),
    FieldOption("language", L("Языковые курсы", "Language courses", "ენის კურსები")),
)

MEDICAL_SPECIALTIES = (
    FieldOption("therapy", L("Терапия", "Therapy", "თერაპია")),
    FieldOption("dentistry", L("Стоматология", "Dentistry", "სტომატოლოგია")),
    FieldOption("diagnostics", L("Диагностика", "Diagnostics", "დიაგnostika")),
    FieldOption("surgery", L("Хирургия", "Surgery", "хирургия")),
    FieldOption("pediatrics", L("Педиатрия", "Pediatrics", "педиатрия")),
)

ROOM_TYPES = (
    FieldOption("standard", L("Стандарт", "Standard", "სტандартული")),
    FieldOption("deluxe", L("Deluxe", "Deluxe", "დელuxe")),
    FieldOption("suite", L("Люкс", "Suite", "люкс")),
    FieldOption("family", L("Семейный", "Family", "семейный")),
)

SERVICE_TYPES = (
    FieldOption("consulting", L("Консалтинг", "Consulting", "консалтинг")),
    FieldOption("marketing", L("Маркетинг", "Marketing", "маркетинг")),
    FieldOption("it", L("IT / разработка", "IT / development", "IT")),
    FieldOption("legal", L("Юридические услуги", "Legal", "юридические")),
    FieldOption("accounting", L("Бухгалтерия", "Accounting", "бухгалтерия")),
)

CARGO_TYPES = (
    FieldOption("general", L("Генеральный груз", "General cargo", "генеральный")),
    FieldOption("refrigerated", L("Рефрижератор", "Refrigerated", "рефрижератор")),
    FieldOption("bulk", L("Насыпной", "Bulk", "насыпной")),
    FieldOption("containers", L("Контейнеры", "Containers", "контейнеры")),
)

STAGE_COLORS = {
    "new": "blue",
    "in_progress": "yellow",
    "converted": "green",
    "junk": "gray",
    "inquiry": "blue",
    "contacted": "purple",
    "interview": "yellow",
    "exam_passed": "orange",
    "enrolled": "green",
    "rejected": "red",
    "application": "blue",
    "documents": "purple",
    "payment": "yellow",
    "cancelled": "red",
    "quote": "purple",
    "contract": "yellow",
    "production": "orange",
    "shipping": "blue",
    "completed": "green",
    "preparation": "purple",
    "proposal": "yellow",
    "negotiation": "orange",
    "won": "green",
    "lost": "red",
    "booking": "blue",
    "confirmed": "green",
    "check_in": "purple",
    "check_out": "gray",
    "estimate": "blue",
    "approval": "yellow",
    "construction": "orange",
    "handover": "green",
    "harvest": "yellow",
    "processing": "orange",
    "export": "blue",
    "scheduled": "blue",
    "in_transit": "yellow",
    "delivered": "green",
    "scope": "blue",
    "execution": "yellow",
    "review": "purple",
    "closed": "green",
}


def _st(key: str, ru: str, en: str, ka: str) -> StatusDef:
    return StatusDef(key, L(ru, en, ka), STAGE_COLORS.get(key, "blue"))


def _f(
    key: str,
    ftype: str,
    ru: str,
    en: str,
    ka: str,
    *,
    required: bool = False,
    show_in_list: bool = False,
    options: tuple[FieldOption, ...] = (),
) -> FieldDef:
    return FieldDef(key, ftype, L(ru, en, ka), required, show_in_list, options)




def get_crm_config(crm_type: str) -> CrmTypeConfig:
    from app.core.crm_industry_data import CRM_CONFIGS
    return CRM_CONFIGS.get(crm_type, CRM_CONFIGS["general"])



def _field_to_dict(f: FieldDef) -> dict[str, Any]:
    d: dict[str, Any] = {
        "key": f.key,
        "type": f.type,
        "label_ru": f.label.ru,
        "label_en": f.label.en,
        "label_ka": f.label.ka,
        "required": f.required,
        "show_in_list": f.show_in_list,
    }
    if f.options:
        d["options"] = [
            {"id": o.id, "label_ru": o.label.ru, "label_en": o.label.en, "label_ka": o.label.ka}
            for o in f.options
        ]
    if f.placeholder:
        d["placeholder_ru"] = f.placeholder.ru
        d["placeholder_en"] = f.placeholder.en
        d["placeholder_ka"] = f.placeholder.ka
    return d


def _status_to_dict(s: StatusDef) -> dict[str, Any]:
    return {
        "key": s.key,
        "label_ru": s.label.ru,
        "label_en": s.label.en,
        "label_ka": s.label.ka,
        "color": s.color,
    }


def config_to_api(crm_type: str) -> dict[str, Any]:
    cfg = get_crm_config(crm_type)
    info = get_crm_type(crm_type)
    return {
        "crm_type": cfg.crm_type,
        "label_ru": info.label_ru,
        "label_en": info.label_en,
        "label_ka": info.label_ka,
        "modules": list(cfg.modules),
        "labels": {
            k: {"ru": v.ru, "en": v.en, "ka": v.ka}
            for k, v in cfg.labels.items()
        },
        "fields": {entity: [_field_to_dict(f) for f in fields] for entity, fields in cfg.fields.items()},
        "deal_stages": [_status_to_dict(s) for s in cfg.deal_stages],
        "lead_statuses": [_status_to_dict(s) for s in cfg.lead_statuses],
        "hide_base_fields": {k: list(v) for k, v in cfg.hide_base_fields.items()},
        "services": [
            {"id": s.id, "label_ru": s.label.ru, "label_en": s.label.en, "label_ka": s.label.ka}
            for s in cfg.services
        ],
    }
