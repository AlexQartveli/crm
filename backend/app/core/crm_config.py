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
class CrmTypeConfig:
    crm_type: str
    modules: tuple[str, ...]
    labels: dict[str, Label3]
    fields: dict[str, tuple[FieldDef, ...]]
    deal_stages: tuple[StatusDef, ...]
    lead_statuses: tuple[StatusDef, ...]
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


GENERAL_CONFIG = CrmTypeConfig(
    crm_type="general",
    modules=(
        "dashboard", "leads", "deals", "contacts", "companies", "products",
        "warehouse", "movements", "inbox", "bots", "integrations",
        "accounting", "cabinet", "users",
    ),
    labels={
        "leads": L("Лиды", "Leads", "ლიდები"),
        "deals": L("Сделки", "Deals", "გარიგებები"),
        "contacts": L("Контакты", "Contacts", "კონტაქტები"),
        "companies": L("Компании", "Companies", "კომპანიები"),
        "products": L("Товары", "Products", "პროდუქტები"),
        "warehouse": L("Склад", "Warehouse", "საწყობი"),
        "movements": L("Движения", "Movements", "მოძრაობები"),
    },
    fields={},
    deal_stages=(
        _st("new", "Новая", "New", "ახალი"),
        _st("preparation", "Подготовка", "Preparation", "მომზადება"),
        _st("proposal", "Предложение", "Proposal", "შეთავაზება"),
        _st("negotiation", "Переговоры", "Negotiation", "მოლაპარაკებები"),
        _st("won", "Выиграна", "Won", "მოგებული"),
        _st("lost", "Проиграна", "Lost", "წაგებული"),
    ),
    lead_statuses=(
        _st("new", "Новый", "New", "ახალი"),
        _st("in_progress", "В работе", "In progress", "მუშავდება"),
        _st("converted", "Конвертирован", "Converted", "კონვერტირებული"),
        _st("junk", "Некачественный", "Junk", "უხარისხო"),
    ),
)

EDUCATION_CONFIG = CrmTypeConfig(
    crm_type="education",
    modules=("dashboard", "leads", "deals", "contacts", "inbox", "bots", "cabinet", "users"),
    labels={
        "leads": L("Абитуриенты", "Applicants", "აბიტურიენტები"),
        "deals": L("Зачисления", "Enrollments", "ჩარიცხვები"),
        "contacts": L("Студенты и родители", "Students & parents", "სტუდენტები და მშობლები"),
    },
    fields={
        "leads": (
            _f("program", "select", "Программа", "Program", "პროგრამა", show_in_list=True, options=EDUCATION_PROGRAMS),
            _f("grade", "text", "Класс / курс", "Grade / year", "კლასი / კურსი", show_in_list=True),
            _f("parent_name", "text", "Родитель", "Parent name", "მშობელი"),
            _f("parent_phone", "phone", "Телефон родителя", "Parent phone", "მშობლის ტელეფონი", show_in_list=True),
            _f("exam_date", "date", "Дата экзамена", "Exam date", "გამოცდის თარიღი"),
            _f("preferred_faculty", "text", "Желаемый факультет", "Preferred faculty", "სასურველი ფაკულტეტი"),
            _f("city", "select", "Город", "City", "ქალაქი", options=GEO_CITIES),
        ),
        "deals": (
            _f("tuition_amount", "number", "Стоимость обучения (₾)", "Tuition (GEL)", "სწავლის ღირებულება", show_in_list=True),
            _f("payment_plan", "select", "План оплаты", "Payment plan", "გადახდის გეგმა", options=PAYMENT_PLANS),
            _f("start_semester", "text", "Семестр начала", "Start semester", "დაწყების სემესტრი", show_in_list=True),
            _f("scholarship", "text", "Стипендия / скидка", "Scholarship", "სტიპendia"),
        ),
        "contacts": (
            _f("student_id", "text", "ID студента", "Student ID", "სტუდენტის ID", show_in_list=True),
            _f("birth_date", "date", "Дата рождения", "Birth date", "დაბადების თარიღი"),
            _f("enrollment_year", "number", "Год поступления", "Enrollment year", "ჩარიცხვის წელი"),
        ),
    },
    deal_stages=(
        _st("application", "Заявка", "Application", "განაცხადი"),
        _st("documents", "Документы", "Documents", "დოკუმენტები"),
        _st("payment", "Оплата", "Payment", "გადახდა"),
        _st("enrolled", "Зачислен", "Enrolled", "ჩარიცხული"),
        _st("cancelled", "Отменено", "Cancelled", "გაუქმებული"),
    ),
    lead_statuses=(
        _st("new", "Новая заявка", "New application", "ახალი განაცხადი"),
        _st("contacted", "Связались", "Contacted", "დაკავშირებული"),
        _st("interview", "Собеседование", "Interview", "გასაუბრება"),
        _st("exam_passed", "Экзамен сдан", "Exam passed", "გამოცდა ჩაბარებული"),
        _st("enrolled", "Зачислен", "Enrolled", "ჩარიცხული"),
        _st("rejected", "Отказ", "Rejected", "უარი"),
    ),
    hide_base_fields={"leads": ("amount",), "deals": ()},
)

FACTORY_CONFIG = CrmTypeConfig(
    crm_type="factory",
    modules=("dashboard", "deals", "companies", "products", "warehouse", "movements", "accounting", "cabinet", "users"),
    labels={
        "deals": L("Заказы на производство", "Production orders", "წარმოების შეკვეთები"),
        "companies": L("Контрагенты", "Counterparties", "კონტრაგენტები"),
        "products": L("Продукция и сырьё", "Products & materials", "პროდუქция და ნედლეული"),
        "warehouse": L("Склад сырья", "Raw warehouse", "ნედლეულის საწყობი"),
        "movements": L("Партии и отгрузки", "Batches & shipments", "პარტიები"),
    },
    fields={
        "deals": (
            _f("order_volume", "number", "Объём заказа", "Order volume", "შეკვეთის მოცულობა", show_in_list=True),
            _f("unit", "text", "Единица", "Unit", "ერთეული", show_in_list=True),
            _f("delivery_date", "date", "Срок поставки", "Delivery date", "მიწოდების ვადა", show_in_list=True),
            _f("material_spec", "textarea", "Спецификация", "Specification", "სპეცifiкაცია"),
            _f("production_line", "text", "Линия производства", "Production line", "საწარმოო ხაზი"),
        ),
        "companies": (
            _f("contract_number", "text", "№ договора", "Contract #", "ხელშეკრულების №", show_in_list=True),
            _f("payment_terms", "text", "Условия оплаты", "Payment terms", "გადახდის პირობები"),
            _f("vat_payer", "select", "Плательщик НДС", "VAT payer", "დღგ გადამხდელი", options=(
                FieldOption("yes", L("Да", "Yes", "დიახ")),
                FieldOption("no", L("Нет", "No", "არა")),
            )),
        ),
        "products": (
            _f("material_grade", "text", "Марка / сорт", "Grade", "მარკა", show_in_list=True),
            _f("weight_kg", "number", "Вес (кг)", "Weight (kg)", "წონა (კგ)"),
            _f("min_batch", "number", "Мин. партия", "Min batch", "მინ. პარტია"),
        ),
    },
    deal_stages=(
        _st("inquiry", "Запрос", "Inquiry", "მოთხოვნა"),
        _st("quote", "Коммерческое предложение", "Quote", "შეთავაზება"),
        _st("contract", "Договор", "Contract", "ხელშეკრულება"),
        _st("production", "Производство", "Production", "წარმოება"),
        _st("shipping", "Отгрузка", "Shipping", "გატანა"),
        _st("completed", "Выполнено", "Completed", "შესრულებული"),
        _st("cancelled", "Отменено", "Cancelled", "გაუქმებული"),
    ),
    lead_statuses=GENERAL_CONFIG.lead_statuses,
)

RETAIL_CONFIG = CrmTypeConfig(
    crm_type="retail",
    modules=("dashboard", "leads", "deals", "products", "warehouse", "inbox", "cabinet", "users"),
    labels={
        "leads": L("Покупатели", "Customers", "მყიდველები"),
        "deals": L("Продажи", "Sales", "გაყიდვები"),
        "products": L("Товары", "Products", "საქონელი"),
        "warehouse": L("Магазин / склад", "Store / stock", "მაღაზია"),
    },
    fields={
        "leads": (
            _f("preferred_category", "text", "Категория интереса", "Category interest", "კატეგორია", show_in_list=True),
            _f("loyalty_card", "text", "Карта лояльности", "Loyalty card", "ლოialty ბარათი"),
            _f("city", "select", "Город", "City", "ქალაქი", options=GEO_CITIES, show_in_list=True),
        ),
        "deals": (
            _f("payment_method", "select", "Способ оплаты", "Payment method", "გადახდის მეთოდი", show_in_list=True, options=(
                FieldOption("cash", L("Наличные", "Cash", "ნაღდი")),
                FieldOption("card", L("Карта", "Card", "ბარათი")),
                FieldOption("online", L("Онлайн", "Online", "ონლაინ")),
            )),
            _f("delivery_address", "text", "Адрес доставки", "Delivery address", "მიწოდების მისამართი"),
            _f("discount_percent", "number", "Скидка %", "Discount %", "ფასდაკლება %"),
        ),
        "products": (
            _f("brand", "text", "Бренд", "Brand", "ბრენდი", show_in_list=True),
            _f("category", "text", "Категория", "Category", "კატეგორია", show_in_list=True),
            _f("barcode", "text", "Штрихкод", "Barcode", "штрихкод"),
        ),
    },
    deal_stages=GENERAL_CONFIG.deal_stages,
    lead_statuses=(
        _st("new", "Новый покупатель", "New customer", "ახალი მყიდველი"),
        _st("in_progress", "В работе", "In progress", "მუშავდება"),
        _st("converted", "Покупка", "Purchase", "ყიდვა"),
        _st("junk", "Не заинтересован", "Not interested", "არainteres"),
    ),
)

HOSPITALITY_CONFIG = CrmTypeConfig(
    crm_type="hospitality",
    modules=("dashboard", "leads", "deals", "contacts", "inbox", "bots", "cabinet", "users"),
    labels={
        "leads": L("Бронирования", "Bookings", "ბронირებები"),
        "deals": L("Туры и пакеты", "Tours & packages", "ტურები"),
        "contacts": L("Гости", "Guests", "სტუმრები"),
    },
    fields={
        "leads": (
            _f("check_in", "date", "Заезд", "Check-in", "შესვლა", show_in_list=True, required=True),
            _f("check_out", "date", "Выезд", "Check-out", "გასვლა", show_in_list=True, required=True),
            _f("guests", "number", "Гостей", "Guests", "სტუმრები", show_in_list=True),
            _f("room_type", "select", "Тип номера", "Room type", "ნომრის ტიპი", show_in_list=True, options=ROOM_TYPES),
            _f("meal_plan", "select", "Питание", "Meal plan", "კვება", options=(
                FieldOption("bb", L("Завтрак", "Breakfast", "საუზმე")),
                FieldOption("hb", L("Полупансион", "Half board", "ნახევar პანსion")),
                FieldOption("fb", L("Полный пансион", "Full board", "სრული")),
                FieldOption("none", L("Без питания", "Room only", "არა")),
            )),
        ),
        "deals": (
            _f("package_name", "text", "Название пакета", "Package name", "პაკეტი", show_in_list=True),
            _f("season", "text", "Сезон", "Season", "სეზონი", show_in_list=True),
            _f("transfer_needed", "select", "Трансфер", "Transfer", "тransfer", options=(
                FieldOption("yes", L("Нужен", "Required", "საჭირო")),
                FieldOption("no", L("Не нужен", "Not required", "არა")),
            )),
        ),
        "contacts": (
            _f("nationality", "text", "Гражданство", "Nationality", "მოქალაქეობა", show_in_list=True),
            _f("passport", "text", "Паспорт", "Passport", "პასპორტი"),
            _f("vip", "select", "VIP", "VIP", "VIP", options=(
                FieldOption("yes", L("Да", "Yes", "დიახ")),
                FieldOption("no", L("Нет", "No", "არა")),
            )),
        ),
    },
    deal_stages=(
        _st("booking", "Бронь", "Booking", "ბронი"),
        _st("confirmed", "Подтверждено", "Confirmed", "დადასტურებული"),
        _st("check_in", "Заезд", "Check-in", "შესვლა"),
        _st("check_out", "Выезд", "Check-out", "გასვლა"),
        _st("cancelled", "Отмена", "Cancelled", "გაუქმება"),
    ),
    lead_statuses=(
        _st("new", "Новая бронь", "New booking", "ახალი ბroni"),
        _st("in_progress", "Уточнение", "In progress", "уточнение"),
        _st("converted", "Подтверждена", "Confirmed", "დადასტურებული"),
        _st("junk", "Отменена", "Cancelled", "გაუქმებული"),
    ),
)

CONSTRUCTION_CONFIG = CrmTypeConfig(
    crm_type="construction",
    modules=("dashboard", "deals", "companies", "warehouse", "accounting", "cabinet", "users"),
    labels={
        "deals": L("Объекты и проекты", "Projects & sites", "ობიekтebi"),
        "companies": L("Заказчики и подрядчики", "Clients & contractors", "დამკვეთები"),
        "warehouse": L("Материалы на объекте", "Site materials", "მასალები"),
    },
    fields={
        "deals": (
            _f("object_address", "text", "Адрес объекта", "Site address", "ობიekтის მისამართი", show_in_list=True),
            _f("object_type", "select", "Тип объекта", "Project type", "ტიპი", show_in_list=True, options=(
                FieldOption("residential", L("Жилой", "Residential", "საცხოვრებელი")),
                FieldOption("commercial", L("Коммерческий", "Commercial", "коммерческий")),
                FieldOption("road", L("Дороги / инфра", "Infrastructure", "инфра")),
                FieldOption("renovation", L("Ремонт", "Renovation", "ремонт")),
            )),
            _f("sq_meters", "number", "Площадь (м²)", "Area (m²)", "ფართობი", show_in_list=True),
            _f("estimate_amount", "number", "Смета (₾)", "Estimate (GEL)", "შეფასება"),
            _f("deadline", "date", "Срок сдачи", "Deadline", "ვადა", show_in_list=True),
        ),
        "companies": (
            _f("license_number", "text", "Лицензия", "License", "ლიცenzia", show_in_list=True),
            _f("specialization", "text", "Специализация", "Specialization", "სპecializacia"),
        ),
    },
    deal_stages=(
        _st("inquiry", "Заявка", "Inquiry", "მოთხოვნა"),
        _st("estimate", "Смета", "Estimate", "შეფასება"),
        _st("approval", "Согласование", "Approval", "დამტკიცება"),
        _st("construction", "Строительство", "Construction", "მშენებლობა"),
        _st("handover", "Сдача", "Handover", "ჩაბარება"),
        _st("cancelled", "Отменено", "Cancelled", "გაუქმება"),
    ),
    lead_statuses=GENERAL_CONFIG.lead_statuses,
)

AGRICULTURE_CONFIG = CrmTypeConfig(
    crm_type="agriculture",
    modules=("dashboard", "deals", "products", "warehouse", "companies", "cabinet", "users"),
    labels={
        "deals": L("Контракты на урожай", "Harvest contracts", "კონტრაქტები"),
        "products": L("Продукция", "Produce", "პროდუქция"),
        "companies": L("Покупатели / экспортёры", "Buyers & exporters", "მყიდველები"),
        "warehouse": L("Хранение", "Storage", "საწყობი"),
    },
    fields={
        "deals": (
            _f("harvest_season", "text", "Сезон урожая", "Harvest season", "მო� harvest", show_in_list=True),
            _f("volume_tons", "number", "Объём (тонн)", "Volume (tons)", "მოცულობა", show_in_list=True),
            _f("export_country", "text", "Страна экспорта", "Export country", "ექსპორტი", show_in_list=True),
            _f("certification", "text", "Сертификация", "Certification", "სertifikacia"),
        ),
        "products": (
            _f("origin_region", "text", "Регион", "Region", "რეგიონი", show_in_list=True),
            _f("harvest_year", "number", "Год урожая", "Harvest year", "წელი", show_in_list=True),
            _f("organic", "select", "Органик", "Organic", "ორგანული", options=(
                FieldOption("yes", L("Да", "Yes", "დიახ")),
                FieldOption("no", L("Нет", "No", "არა")),
            )),
        ),
        "companies": (
            _f("buyer_type", "select", "Тип", "Type", "ტიპი", show_in_list=True, options=(
                FieldOption("local", L("Местный", "Local", "ადგili")),
                FieldOption("export", L("Экспорт", "Export", "ექსპორტი")),
            )),
        ),
    },
    deal_stages=(
        _st("inquiry", "Запрос", "Inquiry", "მოთხოვნა"),
        _st("quote", "Предложение", "Quote", "შეთავაზება"),
        _st("contract", "Контракт", "Contract", "კონტრაქტი"),
        _st("harvest", "Уборка", "Harvest", "მორჩენა"),
        _st("processing", "Переработка", "Processing", "დamუკავება"),
        _st("export", "Экспорт", "Export", "ექსპორტი"),
        _st("completed", "Завершено", "Completed", "დასrულებული"),
    ),
    lead_statuses=GENERAL_CONFIG.lead_statuses,
)

MEDICAL_CONFIG = CrmTypeConfig(
    crm_type="medical",
    modules=("dashboard", "leads", "contacts", "inbox", "bots", "cabinet", "users"),
    labels={
        "leads": L("Записи на приём", "Appointments", "ჩაწერები"),
        "contacts": L("Пациенты", "Patients", "პაციენტები"),
    },
    fields={
        "leads": (
            _f("specialty", "select", "Специальность", "Specialty", "სპecialoba", show_in_list=True, options=MEDICAL_SPECIALTIES),
            _f("appointment_date", "date", "Дата приёма", "Appointment date", "თარიღი", show_in_list=True, required=True),
            _f("doctor", "text", "Врач", "Doctor", "ექimი", show_in_list=True),
            _f("insurance_company", "text", "Страховая", "Insurance", "დაზღვევა"),
            _f("symptoms", "textarea", "Жалобы", "Symptoms", "symptom"),
        ),
        "contacts": (
            _f("birth_date", "date", "Дата рождения", "Birth date", "დაბადება", show_in_list=True),
            _f("policy_number", "text", "Полис", "Policy #", "polisi", show_in_list=True),
            _f("blood_type", "text", "Группа крови", "Blood type", "სისხli"),
            _f("allergies", "textarea", "Аллергии", "Allergies", "ალergia"),
        ),
    },
    deal_stages=GENERAL_CONFIG.deal_stages,
    lead_statuses=(
        _st("new", "Новая запись", "New appointment", "ახალი"),
        _st("in_progress", "Подтверждена", "Confirmed", "დადასტურებული"),
        _st("converted", "Приём состоялся", "Completed", "შესრულებული"),
        _st("junk", "Не явился", "No-show", "არ გამოცხad"),
    ),
    hide_base_fields={"leads": ("amount", "source")},
)

LOGISTICS_CONFIG = CrmTypeConfig(
    crm_type="logistics",
    modules=("dashboard", "deals", "companies", "contacts", "movements", "cabinet", "users"),
    labels={
        "deals": L("Перевозки", "Shipments", "გადაზიდვები"),
        "companies": L("Клиенты", "Clients", "клиенты"),
        "contacts": L("Диспетчеры / водители", "Dispatchers & drivers", "диспетчеры"),
        "movements": L("Складские операции", "Warehouse ops", "ოპeraции"),
    },
    fields={
        "deals": (
            _f("cargo_type", "select", "Тип груза", "Cargo type", "ტვირთი", show_in_list=True, options=CARGO_TYPES),
            _f("weight_tons", "number", "Вес (тонн)", "Weight (tons)", "წონა", show_in_list=True),
            _f("route_from", "text", "Откуда", "From", "საიდan", show_in_list=True),
            _f("route_to", "text", "Куда", "To", "სად", show_in_list=True),
            _f("vehicle_type", "text", "Транспорт", "Vehicle", "транспорт", show_in_list=True),
            _f("loading_date", "date", "Дата погрузки", "Loading date", "ჩატვირთვა"),
        ),
        "companies": (
            _f("fleet_size", "number", "Автопарк", "Fleet size", "ავtoпarki"),
            _f("regular_routes", "textarea", "Регулярные маршруты", "Regular routes", "maršrutebi"),
        ),
        "contacts": (
            _f("driver_license", "text", "Водит. удостоверение", "Driver license", "მართვის მოწმ"),
            _f("vehicle_plate", "text", "Гос. номер", "Plate #", "nomeri"),
        ),
    },
    deal_stages=(
        _st("inquiry", "Заявка", "Request", "მოთხოვნა"),
        _st("quote", "Расчёт", "Quote", "расчёт"),
        _st("contract", "Договор", "Contract", "ხელშეკრულება"),
        _st("scheduled", "Запланировано", "Scheduled", "დაგეგმილი"),
        _st("in_transit", "В пути", "In transit", "გზაში"),
        _st("delivered", "Доставлено", "Delivered", "მიწოდებული"),
        _st("cancelled", "Отменено", "Cancelled", "გაუქმება"),
    ),
    lead_statuses=GENERAL_CONFIG.lead_statuses,
)

SERVICES_CONFIG = CrmTypeConfig(
    crm_type="services",
    modules=("dashboard", "leads", "deals", "contacts", "inbox", "cabinet", "users"),
    labels={
        "leads": L("Заявки на услуги", "Service requests", "მოთხოვნები"),
        "deals": L("Проекты", "Projects", "проекты"),
        "contacts": L("Клиенты", "Clients", "клиенты"),
    },
    fields={
        "leads": (
            _f("service_type", "select", "Тип услуги", "Service type", "სერვისი", show_in_list=True, options=SERVICE_TYPES),
            _f("budget", "number", "Бюджет (₾)", "Budget (GEL)", "ბюджet", show_in_list=True),
            _f("deadline", "date", "Желаемый срок", "Desired deadline", "ვადა"),
            _f("brief", "textarea", "Описание задачи", "Brief", "აღწერა"),
        ),
        "deals": (
            _f("scope", "textarea", "Объём работ", "Scope", "მ объём", show_in_list=True),
            _f("hourly_rate", "number", "Ставка (₾/ч)", "Hourly rate", "stavka"),
            _f("contract_type", "select", "Тип договора", "Contract type", "ხელშ.", options=(
                FieldOption("fixed", L("Фиксированная цена", "Fixed price", "фикс")),
                FieldOption("hourly", L("Почасовая", "Hourly", "საათობრივი")),
                FieldOption("retainer", L("Абонемент", "Retainer", "abonement")),
            )),
        ),
        "contacts": (
            _f("company_role", "text", "Роль в компании", "Company role", "роль"),
            _f("preferred_contact", "select", "Связь", "Contact via", "связь", options=(
                FieldOption("phone", L("Телефон", "Phone", "тел")),
                FieldOption("email", L("Email", "Email", "email")),
                FieldOption("whatsapp", L("WhatsApp", "WhatsApp", "WA")),
            )),
        ),
    },
    deal_stages=(
        _st("inquiry", "Заявка", "Inquiry", "მოთხოვნა"),
        _st("proposal", "Предложение", "Proposal", "შეთავაზება"),
        _st("contract", "Договор", "Contract", "ხელშ."),
        _st("scope", "В работе", "In progress", "მუშაობა"),
        _st("review", "Приёмка", "Review", "მიღება"),
        _st("closed", "Закрыт", "Closed", "დახურული"),
        _st("cancelled", "Отменён", "Cancelled", "გაუქმება"),
    ),
    lead_statuses=GENERAL_CONFIG.lead_statuses,
)

CRM_CONFIGS: dict[str, CrmTypeConfig] = {
    "general": GENERAL_CONFIG,
    "education": EDUCATION_CONFIG,
    "factory": FACTORY_CONFIG,
    "retail": RETAIL_CONFIG,
    "hospitality": HOSPITALITY_CONFIG,
    "construction": CONSTRUCTION_CONFIG,
    "agriculture": AGRICULTURE_CONFIG,
    "medical": MEDICAL_CONFIG,
    "logistics": LOGISTICS_CONFIG,
    "services": SERVICES_CONFIG,
}


def get_crm_config(crm_type: str) -> CrmTypeConfig:
    return CRM_CONFIGS.get(crm_type, GENERAL_CONFIG)


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
    }
