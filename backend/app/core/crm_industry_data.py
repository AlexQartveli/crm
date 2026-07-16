"""Детальные конфигурации модулей, полей и сервисов по отраслям."""

from __future__ import annotations

from app.core.crm_config import (
    CARGO_TYPES,
    EDUCATION_PROGRAMS,
    GEO_CITIES,
    L,
    MEDICAL_SPECIALTIES,
    PAYMENT_PLANS,
    ROOM_TYPES,
    SERVICE_TYPES,
    STAGE_COLORS,
    CrmTypeConfig,
    FieldDef,
    FieldOption,
    Label3,
    ServiceDef,
    StatusDef,
    _f,
    _st,
)

# Полный набор модулей платформы для максимального покрытия
FULL_MODULES = (
    "dashboard", "leads", "deals", "contacts", "companies", "products",
    "warehouse", "movements", "inbox", "bots", "integrations",
    "accounting", "cabinet", "users",
)


def _mods(*extra: str) -> tuple[str, ...]:
    return FULL_MODULES + extra

YES_NO = (
    FieldOption("yes", L("Да", "Yes", "დიახ")),
    FieldOption("no", L("Нет", "No", "არა")),
)

PAYMENT_METHODS = (
    FieldOption("cash", L("Наличные", "Cash", "ნაღდი")),
    FieldOption("card", L("Карта", "Card", "ბარათი")),
    FieldOption("transfer", L("Перевод", "Bank transfer", "გადარიცხვა")),
    FieldOption("online", L("Онлайн", "Online", "ონლაინ")),
)

INSURANCE_TYPES = (
    FieldOption("state", L("Гос. страховка", "State insurance", "სახელმწიფო")),
    FieldOption("private", L("Частная", "Private", "კერძო")),
    FieldOption("corporate", L("Корпоративная", "Corporate", "კორპორატიული")),
    FieldOption("none", L("Без страховки", "No insurance", "არა")),
)

AGRI_PRODUCTS = (
    FieldOption("wine", L("Вино", "Wine", "ღვინო")),
    FieldOption("hazelnut", L("Фундук", "Hazelnut", "თხილი")),
    FieldOption("tea", L("Чай", "Tea", "ჩაი")),
    FieldOption("citrus", L("Цитрусовые", "Citrus", "цитрус")),
    FieldOption("livestock", L("Животноводство", "Livestock", "livestock")),
    FieldOption("other", L("Другое", "Other", "სხვა")),
)


def _svc(sid: str, ru: str, en: str, ka: str) -> ServiceDef:
    return ServiceDef(sid, Label3(ru, en, ka))


def _labels(**kwargs: Label3) -> dict[str, Label3]:
    return kwargs


# ─── GENERAL ───────────────────────────────────────────────────────────────

GENERAL_SERVICES = (
    _svc("leads", "Управление лидами", "Lead management", "ლიდების მართვა"),
    _svc("deals", "Воронка продаж", "Sales pipeline", "გაყიდვების ვორკა"),
    _svc("crm", "Контакты и компании", "Contacts & companies", "კონტაქტები"),
    _svc("warehouse", "Складской учёт", "Warehouse", "საწყობი"),
    _svc("products", "Каталог товаров", "Product catalog", "კატალოგი"),
    _svc("inbox", "WhatsApp / Messenger / Telegram", "Messaging inbox", "მესენჯერები"),
    _svc("bots", "Чат-боты и автоматизация", "Chat bots", "ბოტები"),
    _svc("integrations", "Интеграции Meta", "Meta integrations", "ინტegracia"),
    _svc("accounting", "Счета и RS.ge", "Invoicing & RS.ge", "RS.ge"),
    _svc("rbac", "Роли и права доступа", "Roles & permissions", "როლები"),
)

GENERAL_CONFIG = CrmTypeConfig(
    crm_type="general",
    modules=FULL_MODULES,
    services=GENERAL_SERVICES,
    labels=_labels(
        leads=L("Лиды", "Leads", "ლიდები"),
        deals=L("Сделки", "Deals", "გარიგებები"),
        contacts=L("Контакты", "Contacts", "კონტაქტები"),
        companies=L("Компании", "Companies", "კომპანიები"),
        products=L("Товары", "Products", "პროდუქტები"),
        warehouse=L("Склад", "Warehouse", "საწყობი"),
        movements=L("Движения", "Movements", "მოძრაობები"),
        inbox=L("Сообщения", "Messages", "შეტყობინებები"),
        bots=L("Боты", "Bots", "ბოტები"),
        accounting=L("Бухгалтерия", "Accounting", "ბუღალტერია"),
    ),
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
        _st("contacted", "Связались", "Contacted", "დაკავშირებული"),
        _st("converted", "Конвертирован", "Converted", "კონვერტირებული"),
        _st("junk", "Некачественный", "Junk", "უხარისხო"),
    ),
)

# ─── EDUCATION ─────────────────────────────────────────────────────────────

EDUCATION_SERVICES = (
    _svc("applicants", "Приём абитуриентов", "Applicant intake", "აბიტურიენტები"),
    _svc("enrollment", "Зачисление и договоры", "Enrollment pipeline", "ჩარიცხვა"),
    _svc("students", "База студентов и родителей", "Students & parents", "სტუდენტები"),
    _svc("partners", "Партнёрские школы и вузы", "Partner institutions", "პარტნიორები"),
    _svc("courses", "Каталог программ и курсов", "Programs catalog", "პროგრამები"),
    _svc("finance", "Оплата обучения и RS.ge", "Tuition & invoicing", "გადახდები"),
    _svc("inventory", "Учебные материалы на складе", "Materials inventory", "მასალები"),
    _svc("inbox", "WhatsApp / Telegram для родителей", "Parent messaging", "მშობლები"),
    _svc("bots", "Бот записи на экзамен", "Exam booking bot", "ბოტი"),
    _svc("integrations", "Интеграции Meta", "Meta integrations", "ინტegracia"),
    _svc("rbac", "Роли: директор, приёмная, бухгалтер", "Staff roles", "როლები"),
)

EDUCATION_CONFIG = CrmTypeConfig(
    crm_type="education",
    modules=_mods("schedule"),
    services=EDUCATION_SERVICES,
    labels=_labels(
        leads=L("Абитуриенты", "Applicants", "აბიტურიენტები"),
        deals=L("Зачисления", "Enrollments", "ჩარიცხვები"),
        contacts=L("Студенты и родители", "Students & parents", "სტუდენტები და მშობლები"),
        companies=L("Партнёры / филиалы", "Partners / branches", "პარტნიორები"),
        products=L("Программы и курсы", "Programs & courses", "პროგრამები"),
        warehouse=L("Учебные материалы", "Learning materials", "მასალები"),
        movements=L("Выдача материалов", "Material issues", "გაცემა"),
        inbox=L("Сообщения родителям", "Parent messages", "მშობლები"),
        bots=L("Бот приёмной комиссии", "Admissions bot", "ბოტი"),
        accounting=L("Оплата обучения", "Tuition billing", "გადახდები"),
        schedule=L("Расписание занятий", "Class schedule", "განრიგი"),
    ),
    fields={
        "leads": (
            _f("program", "select", "Программа", "Program", "პროგრამა", show_in_list=True, required=True, options=EDUCATION_PROGRAMS),
            _f("grade", "text", "Класс / курс", "Grade / year", "კლასი", show_in_list=True),
            _f("faculty", "text", "Факультет", "Faculty", "ფაკულტეტი", show_in_list=True),
            _f("parent_name", "text", "Родитель", "Parent", "მშობელი"),
            _f("parent_phone", "phone", "Тел. родителя", "Parent phone", "მშობლის ტელ.", show_in_list=True),
            _f("exam_date", "date", "Дата экзамена", "Exam date", "გამოცდა", show_in_list=True),
            _f("exam_score", "number", "Балл экзамена", "Exam score", "ქულა"),
            _f("language_level", "select", "Уровень языка", "Language level", "ენა", options=(
                FieldOption("a1", L("A1", "A1", "A1")),
                FieldOption("b1", L("B1", "B1", "B1")),
                FieldOption("b2", L("B2", "B2", "B2")),
                FieldOption("c1", L("C1", "C1", "C1")),
            )),
            _f("city", "select", "Город", "City", "ქალაქი", options=GEO_CITIES),
            _f("source_channel", "select", "Источник", "Source", "წყარო", show_in_list=True, options=(
                FieldOption("website", L("Сайт", "Website", "საიტი")),
                FieldOption("fair", L("Ярмарка", "Education fair", "ярмарка")),
                FieldOption("referral", L("Рекомендация", "Referral", "რекomendacia")),
                FieldOption("social", L("Соцсети", "Social media", "სოცial")),
            )),
        ),
        "deals": (
            _f("tuition_amount", "number", "Стоимость (₾)", "Tuition (GEL)", "ღირებულება", show_in_list=True),
            _f("payment_plan", "select", "План оплаты", "Payment plan", "გადახდა", options=PAYMENT_PLANS, show_in_list=True),
            _f("start_semester", "text", "Семестр", "Semester", "სემესტრი", show_in_list=True),
            _f("scholarship_percent", "number", "Стипендия %", "Scholarship %", "სტიპendia %"),
            _f("contract_number", "text", "№ договора", "Contract #", "ხელშ. №"),
            _f("dormitory", "select", "Общежитие", "Dormitory", "საერთ. ნომ.", options=YES_NO),
        ),
        "contacts": (
            _f("student_id", "text", "ID студента", "Student ID", "ID", show_in_list=True),
            _f("birth_date", "date", "Дата рождения", "Birth date", "დაბადება"),
            _f("enrollment_year", "number", "Год поступления", "Enrollment year", "წელი", show_in_list=True),
            _f("group", "text", "Группа", "Group", "ჯგუფი", show_in_list=True),
            _f("gpa", "number", "Средний балл", "GPA", "GPA"),
        ),
        "companies": (
            _f("partnership_type", "select", "Тип партнёрства", "Partnership", "პარტ.", show_in_list=True, options=(
                FieldOption("school", L("Школа", "School", "სკოლა")),
                FieldOption("university", L("Вуз", "University", "универ")),
                FieldOption("employer", L("Работодатель", "Employer", "employer")),
            )),
            _f("accreditation", "text", "Аккредитация", "Accreditation", "accred"),
        ),
        "products": (
            _f("duration_months", "number", "Длительность (мес.)", "Duration (mo)", "ხანგ.", show_in_list=True),
            _f("language", "text", "Язык обучения", "Language", "ენა"),
            _f("format", "select", "Формат", "Format", "ფორმატი", options=(
                FieldOption("fulltime", L("Очно", "Full-time", "очно")),
                FieldOption("online", L("Онлайн", "Online", "ონლაინ")),
                FieldOption("hybrid", L("Гибрид", "Hybrid", "гибрид")),
            )),
        ),
    },
    deal_stages=(
        _st("application", "Заявка", "Application", "განაცხადი"),
        _st("documents", "Документы", "Documents", "დოკუმენტები"),
        _st("exam_passed", "Экзамен", "Exam", "გამოცდა"),
        _st("payment", "Оплата", "Payment", "გადახდა"),
        _st("enrolled", "Зачислен", "Enrolled", "ჩარიცხული"),
        _st("cancelled", "Отменено", "Cancelled", "გაუქმება"),
    ),
    lead_statuses=(
        _st("new", "Новая заявка", "New", "ახალი"),
        _st("contacted", "Связались", "Contacted", "დაკავშ."),
        _st("interview", "Собеседование", "Interview", "გასაუბ."),
        _st("exam_passed", "Экзамен сдан", "Exam passed", "ჩაბ."),
        _st("enrolled", "Зачислен", "Enrolled", "ჩარიც."),
        _st("rejected", "Отказ", "Rejected", "უარი"),
    ),
    hide_base_fields={"leads": ("amount",)},
)

# ─── FACTORY ───────────────────────────────────────────────────────────────

FACTORY_SERVICES = (
    _svc("orders", "Заказы на производство", "Production orders", "წარმოების შეკვეთები"),
    _svc("b2b", "B2B контрагенты и договоры", "B2B contracts", "B2B კონტრაქტები"),
    _svc("materials", "Склад сырья и комплектующих", "Raw materials warehouse", "ნედლეულის საწყობი"),
    _svc("production", "Планирование производства", "Production planning", "წარმოების დაგეგმვა"),
    _svc("quality", "Контроль качества партий", "Batch quality control", "ხარისხის კონტროლი"),
    _svc("shipments", "Отгрузки и логистика", "Shipments & logistics", "გატანა"),
    _svc("finance", "Счета и RS.ge", "Invoicing & RS.ge", "RS.ge"),
    _svc("inbox", "WhatsApp / Telegram для клиентов", "Client messaging", "მესენჯერები"),
    _svc("bots", "Бот статуса заказа", "Order status bot", "ბოტი"),
    _svc("integrations", "Интеграции Meta", "Meta integrations", "ინტegracia"),
    _svc("rbac", "Роли: директор, цех, склад", "Staff roles", "როლები"),
)

FACTORY_CONFIG = CrmTypeConfig(
    crm_type="factory",
    modules=_mods("schedule"),
    services=FACTORY_SERVICES,
    labels=_labels(
        leads=L("Запросы на производство", "Production inquiries", "წარმოების მოთხოვნები"),
        deals=L("Заказы на производство", "Production orders", "წარმოების შეკვეთები"),
        contacts=L("Контактные лица", "Contact persons", "საკონტაქტო პირები"),
        companies=L("Контрагенты", "Counterparties", "კო�ntrაგენტები"),
        products=L("Продукция и сырьё", "Products & materials", "პროდუქция და ნედლეული"),
        warehouse=L("Склад сырья", "Raw warehouse", "ნედლეულის საწყობი"),
        movements=L("Партии и отгрузки", "Batches & shipments", "პარტიები"),
        inbox=L("Сообщения клиентам", "Client messages", "შეტყობინებები"),
        bots=L("Бот статуса заказа", "Order status bot", "ბოტი"),
        accounting=L("Счета и RS.ge", "Invoicing & RS.ge", "RS.ge"),
        schedule=L("План производства", "Production schedule", "წარმოების გrafiki"),
    ),
    fields={
        "leads": (
            _f("product_interest", "text", "Интересующая продукция", "Product interest", "პროდუქტი", show_in_list=True),
            _f("volume_estimate", "number", "Ориентир. объём", "Est. volume", "მოცულობა", show_in_list=True),
            _f("unit", "text", "Единица", "Unit", "ერთეული"),
            _f("delivery_city", "select", "Город поставки", "Delivery city", "ქალაქი", options=GEO_CITIES, show_in_list=True),
            _f("deadline", "date", "Желаемый срок", "Desired deadline", "ვადა"),
            _f("spec_file", "text", "Спецификация (ссылка)", "Spec link", "სპecifikacia"),
            _f("source_channel", "select", "Источник", "Source", "წყარო", options=(
                FieldOption("website", L("Сайт", "Website", "საიტი")),
                FieldOption("tender", L("Тендер", "Tender", "ტendeრი")),
                FieldOption("referral", L("Рекомендация", "Referral", "რекomendacia")),
                FieldOption("exhibition", L("Выставка", "Exhibition", "გამოფენა")),
            )),
        ),
        "deals": (
            _f("order_volume", "number", "Объём заказа", "Order volume", "შეკვეთის მოცულობა", show_in_list=True, required=True),
            _f("unit", "text", "Единица", "Unit", "ერთეული", show_in_list=True),
            _f("delivery_date", "date", "Срок поставки", "Delivery date", "მიწოდების ვადა", show_in_list=True),
            _f("material_spec", "textarea", "Спецификация", "Specification", "სპecifikacia"),
            _f("production_line", "text", "Линия производства", "Production line", "საწარმოო ხაზი", show_in_list=True),
            _f("quality_standard", "text", "Стандарт качества", "Quality standard", "სტандარტი"),
            _f("payment_terms", "text", "Условия оплаты", "Payment terms", "გადახდის პირობები"),
            _f("contract_number", "text", "№ договора", "Contract #", "ხელშ. №", show_in_list=True),
        ),
        "contacts": (
            _f("position", "text", "Должность", "Position", "თანამდებობა", show_in_list=True),
            _f("department", "text", "Отдел", "Department", "განყოფილება"),
            _f("decision_maker", "select", "ЛПР", "Decision maker", "გადამწყვეტი", options=YES_NO),
            _f("preferred_contact", "select", "Связь", "Contact via", "კავშირი", options=(
                FieldOption("phone", L("Телефон", "Phone", "ტელეფონი")),
                FieldOption("email", L("Email", "Email", "ელ-ფოსტა")),
                FieldOption("whatsapp", L("WhatsApp", "WhatsApp", "WhatsApp")),
            )),
            _f("language", "select", "Язык", "Language", "ენა", options=(
                FieldOption("ka", L("Грузинский", "Georgian", "ქართული")),
                FieldOption("ru", L("Русский", "Russian", "რუსული")),
                FieldOption("en", L("English", "English", "ინგლისური")),
            )),
        ),
        "companies": (
            _f("contract_number", "text", "№ договора", "Contract #", "ხელშ. №", show_in_list=True),
            _f("payment_terms", "text", "Условия оплаты", "Payment terms", "გადახდის პირობები"),
            _f("vat_payer", "select", "Плательщик НДС", "VAT payer", "დღგ გადამხდელი", options=YES_NO, show_in_list=True),
            _f("industry", "text", "Отрасль", "Industry", "ინდუსტრია"),
            _f("credit_limit", "number", "Кредитный лимит (₾)", "Credit limit (GEL)", "ლიმიტი"),
            _f("tin", "text", "ИНН / ს/ნ", "TIN", "ს/ნ", show_in_list=True),
        ),
        "products": (
            _f("material_grade", "text", "Марка / сорт", "Grade", "მარკა", show_in_list=True),
            _f("weight_kg", "number", "Вес (кг)", "Weight (kg)", "წონა (კგ)"),
            _f("min_batch", "number", "Мин. партия", "Min batch", "მინ. პარტია", show_in_list=True),
            _f("shelf_life_days", "number", "Срок годности (дн.)", "Shelf life (days)", "ვადა"),
            _f("storage_temp", "text", "Температура хранения", "Storage temp", "ტემპერატურა"),
            _f("origin", "select", "Происхождение", "Origin", "წარმოშობა", options=GEO_CITIES),
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
    lead_statuses=(
        _st("new", "Новый запрос", "New inquiry", "ახალი"),
        _st("contacted", "Связались", "Contacted", "დაკავშ."),
        _st("in_progress", "Расчёт КП", "Quote in progress", "კalkulacia"),
        _st("converted", "Заказ оформлен", "Order placed", "შეკვეთა"),
        _st("rejected", "Отказ", "Rejected", "უარი"),
        _st("junk", "Некачественный", "Junk", "უხარისხო"),
    ),
    hide_base_fields={"leads": ("amount",)},
)

# ─── RETAIL ────────────────────────────────────────────────────────────────

RETAIL_SERVICES = (
    _svc("customers", "База покупателей", "Customer database", "მყიდველები"),
    _svc("sales", "Продажи и чеки", "Sales & receipts", "გაყიდვები"),
    _svc("catalog", "Каталог товаров", "Product catalog", "კატალოგი"),
    _svc("inventory", "Склад и остатки", "Inventory & stock", "ნაშთები"),
    _svc("loyalty", "Карты лояльности", "Loyalty cards", "ლოialty"),
    _svc("delivery", "Доставка по Грузии", "Delivery across Georgia", "მიწოდება"),
    _svc("inbox", "WhatsApp / Instagram / Messenger", "Social messaging", "მესენჯერები"),
    _svc("bots", "Бот заказов и акций", "Order & promo bot", "ბოტი"),
    _svc("finance", "Счета и RS.ge", "Invoicing & RS.ge", "RS.ge"),
    _svc("integrations", "Интеграции Meta", "Meta integrations", "ინტegracia"),
    _svc("rbac", "Роли: продавец, кассир, админ", "Staff roles", "როლები"),
)

RETAIL_CONFIG = CrmTypeConfig(
    crm_type="retail",
    modules=_mods("schedule"),
    services=RETAIL_SERVICES,
    labels=_labels(
        leads=L("Покупатели", "Customers", "მყიდველები"),
        deals=L("Продажи", "Sales", "გაყიდვები"),
        contacts=L("Покупатели", "Customers", "მყიდველები"),
        companies=L("Поставщики", "Suppliers", "მომწოდებლები"),
        products=L("Товары", "Products", "საქონელი"),
        warehouse=L("Магазин / склад", "Store / stock", "მაღაზია"),
        movements=L("Приход / расход", "Stock movements", "მოძრაობები"),
        inbox=L("Сообщения покупателям", "Customer messages", "შეტყობინებები"),
        bots=L("Бот заказов", "Order bot", "ბოტი"),
        accounting=L("Касса и RS.ge", "POS & RS.ge", "RS.ge"),
        schedule=L("Календарь акций", "Promo calendar", "აქციების კალენდარი"),
    ),
    fields={
        "leads": (
            _f("preferred_category", "text", "Категория интереса", "Category interest", "კატეგორია", show_in_list=True),
            _f("loyalty_card", "text", "Карта лояльности", "Loyalty card", "ლოialty ბარათი", show_in_list=True),
            _f("city", "select", "Город", "City", "ქალაქი", options=GEO_CITIES, show_in_list=True),
            _f("birthday", "date", "День рождения", "Birthday", "დაბადება"),
            _f("preferred_store", "text", "Предпочитаемый магазин", "Preferred store", "მაღაზია"),
            _f("source_channel", "select", "Источник", "Source", "წყარო", show_in_list=True, options=(
                FieldOption("store", L("Магазин", "In-store", "მაღაზია")),
                FieldOption("instagram", L("Instagram", "Instagram", "Instagram")),
                FieldOption("website", L("Сайт", "Website", "საიტი")),
                FieldOption("referral", L("Рекомендация", "Referral", "რекomendacia")),
            )),
            _f("sms_consent", "select", "SMS-рассылка", "SMS consent", "SMS", options=YES_NO),
        ),
        "deals": (
            _f("payment_method", "select", "Способ оплаты", "Payment method", "გადახდა", show_in_list=True, options=PAYMENT_METHODS),
            _f("delivery_address", "text", "Адрес доставки", "Delivery address", "მისამართი"),
            _f("discount_percent", "number", "Скидка %", "Discount %", "ფასდაკლება %", show_in_list=True),
            _f("delivery_date", "date", "Дата доставки", "Delivery date", "მიწოდება"),
            _f("store_location", "select", "Точка продажи", "Store location", "ფილიალი", options=GEO_CITIES, show_in_list=True),
            _f("receipt_number", "text", "№ чека", "Receipt #", "ქვით. №"),
            _f("return_reason", "text", "Причина возврата", "Return reason", "დაბრუნება"),
        ),
        "contacts": (
            _f("loyalty_points", "number", "Баллы лояльности", "Loyalty points", "ქულები", show_in_list=True),
            _f("preferred_size", "text", "Размер / параметры", "Size / params", "ზომა"),
            _f("purchase_count", "number", "Кол-во покупок", "Purchase count", "ყიდვები"),
            _f("last_purchase", "date", "Последняя покупка", "Last purchase", "ბოლო"),
            _f("vip", "select", "VIP", "VIP", "VIP", options=YES_NO, show_in_list=True),
        ),
        "companies": (
            _f("supplier_category", "text", "Категория товаров", "Product category", "კატეგორია", show_in_list=True),
            _f("payment_terms", "text", "Условия оплаты", "Payment terms", "პირობები"),
            _f("delivery_schedule", "text", "График поставок", "Delivery schedule", "გრაფიკი"),
            _f("tin", "text", "ИНН / ს/ნ", "TIN", "ს/ნ", show_in_list=True),
            _f("contact_person", "text", "Менеджер", "Account manager", "მeneჯeri"),
        ),
        "products": (
            _f("brand", "text", "Бренд", "Brand", "ბრენდი", show_in_list=True),
            _f("category", "text", "Категория", "Category", "კატეგორია", show_in_list=True),
            _f("barcode", "text", "Штрихкод", "Barcode", "штрихкод", show_in_list=True),
            _f("size", "text", "Размер", "Size", "ზომა"),
            _f("color", "text", "Цвет", "Color", "ფერი"),
            _f("season", "text", "Сезон", "Season", "სეზონი"),
            _f("supplier_sku", "text", "Артикул поставщика", "Supplier SKU", "SKU"),
        ),
    },
    deal_stages=(
        _st("new", "Новая продажа", "New sale", "ახალი"),
        _st("preparation", "Комплектация", "Preparation", "მომზადება"),
        _st("proposal", "Счёт / КП", "Invoice / quote", "შეთავაზება"),
        _st("negotiation", "Согласование", "Negotiation", "მოლაპარაკება"),
        _st("won", "Оплачено", "Paid", "გადახდილი"),
        _st("lost", "Отменено", "Cancelled", "გაუქმებული"),
    ),
    lead_statuses=(
        _st("new", "Новый покупатель", "New customer", "ახალი მყიდველი"),
        _st("contacted", "Связались", "Contacted", "დაკავშ."),
        _st("in_progress", "В работе", "In progress", "მუშავდება"),
        _st("converted", "Покупка", "Purchase", "ყიდვა"),
        _st("junk", "Не заинтересован", "Not interested", "არainteres"),
    ),
)

# ─── HOSPITALITY ───────────────────────────────────────────────────────────

HOSPITALITY_SERVICES = (
    _svc("bookings", "Бронирование номеров", "Room bookings", "ბroni"),
    _svc("tours", "Туры и пакеты по Грузии", "Tours across Georgia", "ტურები"),
    _svc("guests", "База гостей", "Guest database", "სტუმრები"),
    _svc("partners", "Отели и партнёры", "Hotels & partners", "პარტნიორები"),
    _svc("packages", "Каталог туров", "Tour catalog", "პაკეტები"),
    _svc("finance", "Оплата и RS.ge", "Payments & RS.ge", "RS.ge"),
    _svc("inbox", "WhatsApp / Telegram для гостей", "Guest messaging", "მესენჯერები"),
    _svc("bots", "Бот бронирования", "Booking bot", "ბოტი"),
    _svc("integrations", "Интеграции Meta", "Meta integrations", "ინტegracia"),
    _svc("rbac", "Роли: админ, ресепшн, гид", "Staff roles", "როლები"),
)

HOSPITALITY_CONFIG = CrmTypeConfig(
    crm_type="hospitality",
    modules=_mods("schedule"),
    services=HOSPITALITY_SERVICES,
    labels=_labels(
        leads=L("Бронирования", "Bookings", "ბронირებები"),
        deals=L("Туры и пакеты", "Tours & packages", "ტურები"),
        contacts=L("Гости", "Guests", "სტუმრები"),
        companies=L("Отели / партнёры", "Hotels & partners", "სასტუმრoes"),
        products=L("Туры и услуги", "Tours & services", "სერვისები"),
        warehouse=L("Инвентарь", "Inventory", "ინვentari"),
        movements=L("Выдача / возврат", "Issue & return", "გაცემა"),
        inbox=L("Сообщения гостям", "Guest messages", "შეტყობინებები"),
        bots=L("Бот бронирования", "Booking bot", "ბოტი"),
        accounting=L("Оплата и RS.ge", "Billing & RS.ge", "RS.ge"),
        schedule=L("Шахматка номеров", "Room grid", "ოთახების ცხრილი"),
    ),
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
            _f("destination", "select", "Направление", "Destination", "მიმართულება", show_in_list=True, options=GEO_CITIES),
            _f("source_channel", "select", "Источник", "Source", "წყარო", options=(
                FieldOption("booking", L("Booking.com", "Booking.com", "Booking")),
                FieldOption("airbnb", L("Airbnb", "Airbnb", "Airbnb")),
                FieldOption("direct", L("Прямое", "Direct", "პირდაპირი")),
                FieldOption("agent", L("Агент", "Agent", "აგენტი")),
            )),
            _f("special_requests", "textarea", "Особые пожелания", "Special requests", "მოთხოვნები"),
        ),
        "deals": (
            _f("package_name", "text", "Название пакета", "Package name", "პაკეტი", show_in_list=True),
            _f("season", "text", "Сезон", "Season", "სეზონი", show_in_list=True),
            _f("transfer_needed", "select", "Трансфер", "Transfer", "тransfer", options=YES_NO),
            _f("guide_language", "select", "Язык гида", "Guide language", "ენა", options=(
                FieldOption("ka", L("Грузинский", "Georgian", "ქართული")),
                FieldOption("ru", L("Русский", "Russian", "რუსული")),
                FieldOption("en", L("English", "English", "ინგლისური")),
            )),
            _f("group_size", "number", "Размер группы", "Group size", "ჯგუფი", show_in_list=True),
            _f("deposit_amount", "number", "Депозит (₾)", "Deposit (GEL)", "დეპoziti"),
            _f("payment_method", "select", "Оплата", "Payment", "გადახდა", options=PAYMENT_METHODS),
        ),
        "contacts": (
            _f("nationality", "text", "Гражданство", "Nationality", "მოქალაქეობა", show_in_list=True),
            _f("passport", "text", "Паспорт", "Passport", "პასპორტი"),
            _f("vip", "select", "VIP", "VIP", "VIP", options=YES_NO, show_in_list=True),
            _f("visit_count", "number", "Визитов", "Visit count", "ვიზიტები"),
            _f("dietary", "text", "Диета / аллергии", "Diet / allergies", "დიeta"),
            _f("preferred_room", "text", "Предпочитаемый номер", "Preferred room", "ნომერი"),
        ),
        "companies": (
            _f("hotel_stars", "number", "Звёзды", "Stars", "ვარსკვლavi", show_in_list=True),
            _f("room_count", "number", "Номеров", "Room count", "ნომრები"),
            _f("commission_percent", "number", "Комиссия %", "Commission %", "კომისია %"),
            _f("contract_until", "date", "Договор до", "Contract until", "ხელშ. ვადა"),
            _f("city", "select", "Город", "City", "ქალაქი", options=GEO_CITIES, show_in_list=True),
        ),
        "products": (
            _f("duration_days", "number", "Длительность (дн.)", "Duration (days)", "დღეები", show_in_list=True),
            _f("route", "text", "Маршрут", "Route", "მaršruti", show_in_list=True),
            _f("includes", "textarea", "Включено", "Includes", "შედის"),
            _f("max_group", "number", "Макс. группа", "Max group", "მакс."),
            _f("season", "text", "Сезон", "Season", "სეზონი"),
        ),
    },
    deal_stages=(
        _st("booking", "Бронь", "Booking", "ბroni"),
        _st("confirmed", "Подтверждено", "Confirmed", "დადასტურებული"),
        _st("payment", "Оплата", "Payment", "გადახდა"),
        _st("check_in", "Заезд", "Check-in", "შესვლა"),
        _st("check_out", "Выезд", "Check-out", "გასვლა"),
        _st("cancelled", "Отмена", "Cancelled", "გაუქმება"),
    ),
    lead_statuses=(
        _st("new", "Новая бронь", "New booking", "ახალი ბroni"),
        _st("contacted", "Уточнение", "Follow-up", "уточнение"),
        _st("in_progress", "Ожидает оплаты", "Awaiting payment", "გადახდა"),
        _st("converted", "Подтверждена", "Confirmed", "დადასტურებული"),
        _st("rejected", "Отменена", "Cancelled", "გაუქმებული"),
        _st("junk", "Спам", "Spam", "სპამი"),
    ),
    hide_base_fields={"leads": ("amount", "source")},
)

# ─── CONSTRUCTION ──────────────────────────────────────────────────────────

CONSTRUCTION_SERVICES = (
    _svc("projects", "Объекты и проекты", "Projects & sites", "ობიekтebi"),
    _svc("estimates", "Сметы и калькуляции", "Estimates & quotes", "შეფასებები"),
    _svc("contractors", "Заказчики и подрядчики", "Clients & contractors", "კონტრაქტori"),
    _svc("materials", "Материалы на объекте", "Site materials", "მასალები"),
    _svc("warehouse", "Склад стройматериалов", "Building materials warehouse", "საწყობი"),
    _svc("finance", "Счета и RS.ge", "Invoicing & RS.ge", "RS.ge"),
    _svc("inbox", "WhatsApp / Telegram на объекте", "Site messaging", "მესენჯერები"),
    _svc("bots", "Бот статуса объекта", "Project status bot", "ბოტი"),
    _svc("integrations", "Интеграции Meta", "Meta integrations", "ინტegracia"),
    _svc("rbac", "Роли: прораб, сметчик, директор", "Staff roles", "როლები"),
)

CONSTRUCTION_CONFIG = CrmTypeConfig(
    crm_type="construction",
    modules=_mods("schedule"),
    services=CONSTRUCTION_SERVICES,
    labels=_labels(
        leads=L("Заявки на строительство", "Construction inquiries", "მოთხოვნები"),
        deals=L("Объекты и проекты", "Projects & sites", "ობიekтebi"),
        contacts=L("Контактные лица", "Contact persons", "საკონტაქტო პირები"),
        companies=L("Заказчики и подрядчики", "Clients & contractors", "დამკვეთები"),
        products=L("Работы и услуги", "Works & services", "სამუშაოები"),
        warehouse=L("Материалы на объекте", "Site materials", "მასალები"),
        movements=L("Списание материалов", "Material usage", "მოხმარება"),
        inbox=L("Сообщения на объекте", "Site messages", "შეტყობინებები"),
        bots=L("Бот статуса объекта", "Project status bot", "ბოტი"),
        accounting=L("Сметы и RS.ge", "Estimates & RS.ge", "RS.ge"),
        schedule=L("График работ", "Work timeline", "სამუშაო გრafiki"),
    ),
    fields={
        "leads": (
            _f("object_address", "text", "Адрес объекта", "Site address", "მისამართი", show_in_list=True),
            _f("object_type", "select", "Тип объекта", "Project type", "ტიპი", show_in_list=True, options=(
                FieldOption("residential", L("Жилой", "Residential", "საცხოვრებელი")),
                FieldOption("commercial", L("Коммерческий", "Commercial", "коммерческий")),
                FieldOption("road", L("Дороги / инфра", "Infrastructure", "инфра")),
                FieldOption("renovation", L("Ремонт", "Renovation", "ремонт")),
            )),
            _f("sq_meters", "number", "Площадь (м²)", "Area (m²)", "ფართობი", show_in_list=True),
            _f("budget_estimate", "number", "Бюджет (₾)", "Budget (GEL)", "ბюджet"),
            _f("city", "select", "Город", "City", "ქალაქი", options=GEO_CITIES, show_in_list=True),
            _f("start_date", "date", "Желаемое начало", "Desired start", "დაწყება"),
            _f("source_channel", "select", "Источник", "Source", "წყარო", options=(
                FieldOption("referral", L("Рекомендация", "Referral", "რекomendacia")),
                FieldOption("tender", L("Тендер", "Tender", "ტendeრი")),
                FieldOption("website", L("Сайт", "Website", "საიტი")),
                FieldOption("agent", L("Риелтор", "Agent", "აგენტი")),
            )),
        ),
        "deals": (
            _f("object_address", "text", "Адрес объекта", "Site address", "მისამართი", show_in_list=True, required=True),
            _f("object_type", "select", "Тип объекта", "Project type", "ტიპი", show_in_list=True, options=(
                FieldOption("residential", L("Жилой", "Residential", "საცხოვრებელი")),
                FieldOption("commercial", L("Коммерческий", "Commercial", "коммерческий")),
                FieldOption("road", L("Дороги / инфра", "Infrastructure", "инфра")),
                FieldOption("renovation", L("Ремонт", "Renovation", "ремонт")),
            )),
            _f("sq_meters", "number", "Площадь (м²)", "Area (m²)", "ფართობი", show_in_list=True),
            _f("estimate_amount", "number", "Смета (₾)", "Estimate (GEL)", "შეფასება", show_in_list=True),
            _f("deadline", "date", "Срок сдачи", "Deadline", "ვადა", show_in_list=True),
            _f("foreman", "text", "Прораб", "Foreman", "პრораბი", show_in_list=True),
            _f("permit_number", "text", "№ разрешения", "Permit #", "ნებართვა"),
            _f("advance_percent", "number", "Аванс %", "Advance %", "ავანსი %"),
        ),
        "contacts": (
            _f("role", "select", "Роль", "Role", "როლი", show_in_list=True, options=(
                FieldOption("owner", L("Заказчик", "Client", "დამკვეთი")),
                FieldOption("architect", L("Архитектор", "Architect", "არქიტექტori")),
                FieldOption("engineer", L("Инженер", "Engineer", "ინჟeneრi")),
                FieldOption("supplier", L("Поставщик", "Supplier", "მომწოდებელი")),
            )),
            _f("company_role", "text", "Должность", "Position", "თანამდებობა"),
            _f("site_access", "select", "Допуск на объект", "Site access", "დopusk", options=YES_NO),
        ),
        "companies": (
            _f("license_number", "text", "Лицензия", "License", "ლიცenzia", show_in_list=True),
            _f("specialization", "text", "Специализация", "Specialization", "სპecializacia", show_in_list=True),
            _f("tin", "text", "ИНН / ს/ნ", "TIN", "ს/ნ", show_in_list=True),
            _f("insurance_policy", "text", "Страховка", "Insurance", "დაზღვევა"),
            _f("rating", "number", "Рейтинг", "Rating", "რეიტingi"),
        ),
        "products": (
            _f("work_unit", "text", "Ед. измерения", "Unit", "ერთეული", show_in_list=True),
            _f("labor_hours", "number", "Трудозатраты (ч)", "Labor hours", "საათები"),
            _f("material_cost", "number", "Стоимость материалов (₾)", "Material cost", "მასალა"),
            _f("warranty_months", "number", "Гарантия (мес.)", "Warranty (mo)", "გარantia"),
        ),
    },
    deal_stages=(
        _st("inquiry", "Заявка", "Inquiry", "მოთხოვნა"),
        _st("estimate", "Смета", "Estimate", "შეფასება"),
        _st("approval", "Согласование", "Approval", "დამტკიცება"),
        _st("contract", "Договор", "Contract", "ხელშეკრულება"),
        _st("construction", "Строительство", "Construction", "მშენებლობა"),
        _st("handover", "Сдача", "Handover", "ჩაბარება"),
        _st("cancelled", "Отменено", "Cancelled", "გაუქმებული"),
    ),
    lead_statuses=(
        _st("new", "Новая заявка", "New inquiry", "ახალი"),
        _st("contacted", "Выезд на объект", "Site visit", "ობიekti"),
        _st("in_progress", "Расчёт сметы", "Estimate in progress", "შეფასება"),
        _st("converted", "Договор подписан", "Contract signed", "ხელშ."),
        _st("rejected", "Отказ", "Rejected", "უარი"),
        _st("junk", "Некачественный", "Junk", "უხარისხო"),
    ),
    hide_base_fields={"leads": ("amount",)},
)

# ─── AGRICULTURE ─────────────────────────────────────────────────────────────

AGRICULTURE_SERVICES = (
    _svc("contracts", "Контракты на урожай", "Harvest contracts", "კონტრაქტები"),
    _svc("buyers", "Покупатели и экспортёры", "Buyers & exporters", "მყიდველები"),
    _svc("produce", "Каталог продукции", "Produce catalog", "პროდუქция"),
    _svc("storage", "Хранение и склад", "Storage & warehouse", "საწყობი"),
    _svc("export", "Экспорт (EU, СНГ)", "Export (EU, CIS)", "ექსპორტი"),
    _svc("certification", "Сертификация и органик", "Certification & organic", "სertifikacia"),
    _svc("finance", "Счета и RS.ge", "Invoicing & RS.ge", "RS.ge"),
    _svc("inbox", "WhatsApp / Telegram с фермерами", "Farmer messaging", "მესენჯერები"),
    _svc("bots", "Бот цен и закупок", "Price & purchase bot", "ბოტი"),
    _svc("integrations", "Интеграции Meta", "Meta integrations", "ინტegracia"),
)

AGRICULTURE_CONFIG = CrmTypeConfig(
    crm_type="agriculture",
    modules=_mods("schedule"),
    services=AGRICULTURE_SERVICES,
    labels=_labels(
        leads=L("Запросы на закупку", "Purchase inquiries", "მოთხოვნები"),
        deals=L("Контракты на урожай", "Harvest contracts", "კონტრაქტები"),
        contacts=L("Фермеры / агрономы", "Farmers & agronomists", "fermerebi"),
        companies=L("Покупатели / экспортёры", "Buyers & exporters", "მყიდველები"),
        products=L("Продукция", "Produce", "პროდუქция"),
        warehouse=L("Хранение", "Storage", "საწყობი"),
        movements=L("Приём / отгрузка", "Intake & shipment", "მოძრაობები"),
        inbox=L("Сообщения партнёрам", "Partner messages", "შეტყობინებები"),
        bots=L("Бот закупок", "Purchase bot", "ბოტი"),
        accounting=L("Расчёты и RS.ge", "Billing & RS.ge", "RS.ge"),
        schedule=L("Сезонный календарь", "Season calendar", "სეზონის კალენდარი"),
    ),
    fields={
        "leads": (
            _f("product_type", "select", "Продукция", "Product", "პროდუქტი", show_in_list=True, options=AGRI_PRODUCTS),
            _f("volume_tons", "number", "Объём (тонн)", "Volume (tons)", "მოცულობა", show_in_list=True),
            _f("harvest_season", "text", "Сезон урожая", "Harvest season", "სეზონი", show_in_list=True),
            _f("region", "select", "Регион", "Region", "რეგიონი", options=GEO_CITIES, show_in_list=True),
            _f("export_interest", "select", "Экспорт", "Export", "ექსპორტი", options=YES_NO),
            _f("organic_required", "select", "Органик", "Organic", "ორგანული", options=YES_NO),
            _f("price_offer", "number", "Предлож. цена (₾/т)", "Offer price", "ფასი"),
        ),
        "deals": (
            _f("harvest_season", "text", "Сезон урожая", "Harvest season", "სეზონი", show_in_list=True),
            _f("volume_tons", "number", "Объём (тонн)", "Volume (tons)", "მოცულობა", show_in_list=True, required=True),
            _f("export_country", "text", "Страна экспорта", "Export country", "ექსპორტი", show_in_list=True),
            _f("certification", "text", "Сертификация", "Certification", "სertifikacia"),
            _f("price_per_ton", "number", "Цена (₾/т)", "Price (GEL/ton)", "ფასი", show_in_list=True),
            _f("delivery_terms", "text", "Условия поставки", "Delivery terms", "მიწოდება"),
            _f("payment_method", "select", "Оплата", "Payment", "გადახდა", options=PAYMENT_METHODS),
            _f("warehouse_location", "select", "Склад", "Warehouse", "საწყობი", options=GEO_CITIES),
        ),
        "contacts": (
            _f("farm_name", "text", "Хозяйство", "Farm name", "ferma", show_in_list=True),
            _f("land_hectares", "number", "Площадь (га)", "Land (ha)", "hektari"),
            _f("region", "select", "Регион", "Region", "რეგიონი", options=GEO_CITIES, show_in_list=True),
            _f("organic_cert", "select", "Органик сертификат", "Organic cert", "ორგანული", options=YES_NO),
        ),
        "companies": (
            _f("buyer_type", "select", "Тип", "Type", "ტიპი", show_in_list=True, options=(
                FieldOption("local", L("Местный", "Local", "ადგili")),
                FieldOption("export", L("Экспорт", "Export", "ექსპორტი")),
                FieldOption("processor", L("Переработчик", "Processor", "დamუკავება")),
            )),
            _f("export_markets", "text", "Рынки экспорта", "Export markets", "რынки"),
            _f("tin", "text", "ИНН / ს/ნ", "TIN", "ს/ნ", show_in_list=True),
            _f("payment_terms", "text", "Условия оплаты", "Payment terms", "პირობები"),
        ),
        "products": (
            _f("product_type", "select", "Тип", "Type", "ტიპი", show_in_list=True, options=AGRI_PRODUCTS),
            _f("origin_region", "text", "Регион", "Region", "რეგიონი", show_in_list=True),
            _f("harvest_year", "number", "Год урожая", "Harvest year", "წელი", show_in_list=True),
            _f("organic", "select", "Органик", "Organic", "ორგანული", options=YES_NO, show_in_list=True),
            _f("grade", "text", "Сорт / класс", "Grade", "კლასი"),
            _f("moisture_percent", "number", "Влажность %", "Moisture %", "სიტენianoba"),
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
    lead_statuses=(
        _st("new", "Новый запрос", "New inquiry", "ახალი"),
        _st("contacted", "Связались", "Contacted", "დაკავშ."),
        _st("in_progress", "Переговоры", "Negotiation", "მოლაპარაკება"),
        _st("converted", "Контракт", "Contract", "კონტრაქტი"),
        _st("rejected", "Отказ", "Rejected", "უარი"),
        _st("junk", "Некачественный", "Junk", "უხარისხო"),
    ),
    hide_base_fields={"leads": ("amount", "source")},
)

# ─── MEDICAL ─────────────────────────────────────────────────────────────────

MEDICAL_SERVICES = (
    _svc("appointments", "Запись на приём", "Appointment booking", "ჩაწერები"),
    _svc("patients", "База пациентов", "Patient database", "პაციენტები"),
    _svc("doctors", "Расписание врачей", "Doctor schedules", "ექimები"),
    _svc("insurance", "Страховые компании", "Insurance companies", "დაზღვევა"),
    _svc("services", "Каталог услуг", "Services catalog", "სერვისები"),
    _svc("finance", "Счета и RS.ge", "Invoicing & RS.ge", "RS.ge"),
    _svc("inbox", "WhatsApp / Telegram для пациентов", "Patient messaging", "მესენჯერები"),
    _svc("bots", "Бот записи на приём", "Appointment bot", "ბოტი"),
    _svc("integrations", "Интеграции Meta", "Meta integrations", "ინტegracia"),
    _svc("rbac", "Роли: врач, админ, регистратура", "Staff roles", "როლები"),
)

MEDICAL_CONFIG = CrmTypeConfig(
    crm_type="medical",
    modules=_mods("schedule"),
    services=MEDICAL_SERVICES,
    labels=_labels(
        leads=L("Записи на приём", "Appointments", "ჩაწერები"),
        deals=L("Лечение / услуги", "Treatment / services", "მკureba"),
        contacts=L("Пациенты", "Patients", "პაციენტები"),
        companies=L("Страховые / партнёры", "Insurance & partners", "დაზღვევა"),
        products=L("Услуги и процедуры", "Services & procedures", "პროცedurebi"),
        warehouse=L("Мед. расходники", "Medical supplies", "მასალები"),
        movements=L("Выдача расходников", "Supply issues", "გაცემა"),
        inbox=L("Сообщения пациентам", "Patient messages", "შეტყობინებები"),
        bots=L("Бот записи", "Booking bot", "ბოტი"),
        accounting=L("Оплата и RS.ge", "Billing & RS.ge", "RS.ge"),
        schedule=L("Расписание приёмов", "Appointment schedule", "ჩაწერების გრafiki"),
    ),
    fields={
        "leads": (
            _f("specialty", "select", "Специальность", "Specialty", "სპecialoba", show_in_list=True, required=True, options=MEDICAL_SPECIALTIES),
            _f("appointment_date", "date", "Дата приёма", "Appointment date", "თარიღი", show_in_list=True, required=True),
            _f("doctor", "text", "Врач", "Doctor", "ექimი", show_in_list=True),
            _f("insurance_type", "select", "Страховка", "Insurance", "დაზღვევა", options=INSURANCE_TYPES, show_in_list=True),
            _f("insurance_company", "text", "Страховая компания", "Insurance company", "კომპანია"),
            _f("symptoms", "textarea", "Жалобы", "Symptoms", "symptom"),
            _f("urgency", "select", "Срочность", "Urgency", "სიმძიმe", options=(
                FieldOption("routine", L("Плановый", "Routine", "გეგმიური")),
                FieldOption("urgent", L("Срочный", "Urgent", "სასწრაფო")),
                FieldOption("emergency", L("Экстренный", "Emergency", "extrrenuli")),
            )),
            _f("referral", "select", "Направление", "Referral", "მიმართuvlა", options=YES_NO),
        ),
        "deals": (
            _f("diagnosis", "text", "Диагноз", "Diagnosis", "diagnozi", show_in_list=True),
            _f("treatment_plan", "textarea", "План лечения", "Treatment plan", "გეგმა"),
            _f("procedure_count", "number", "Процедур", "Procedures", "პროცedurebi"),
            _f("insurance_coverage", "number", "Покрытие страховки %", "Insurance coverage %", "დაფinansi"),
            _f("payment_method", "select", "Оплата", "Payment", "გადახდა", options=PAYMENT_METHODS),
            _f("follow_up_date", "date", "Кontrolный визит", "Follow-up", "kontroli"),
        ),
        "contacts": (
            _f("birth_date", "date", "Дата рождения", "Birth date", "დაბადება", show_in_list=True),
            _f("policy_number", "text", "Полис", "Policy #", "polisi", show_in_list=True),
            _f("blood_type", "text", "Группа крови", "Blood type", "სისხli"),
            _f("allergies", "textarea", "Аллергии", "Allergies", "ალergia"),
            _f("personal_id", "text", "Пersonal №", "Personal ID", "პ/n"),
            _f("emergency_contact", "phone", "Экстренный контакт", "Emergency contact", "extrrenuli"),
            _f("last_visit", "date", "Последний визит", "Last visit", "ბოლო", show_in_list=True),
        ),
        "companies": (
            _f("insurance_type", "select", "Тип", "Type", "ტიპი", options=INSURANCE_TYPES, show_in_list=True),
            _f("contract_number", "text", "№ договора", "Contract #", "ხელშ. №"),
            _f("coverage_percent", "number", "Покрытие %", "Coverage %", "დაფinansi"),
            _f("tin", "text", "ИНН / ს/ნ", "TIN", "ს/ნ", show_in_list=True),
        ),
        "products": (
            _f("specialty", "select", "Специальность", "Specialty", "სპecialoba", options=MEDICAL_SPECIALTIES, show_in_list=True),
            _f("duration_min", "number", "Длительность (мин.)", "Duration (min)", "ხანგ.", show_in_list=True),
            _f("preparation", "text", "Подготовка", "Preparation", "მომზადება"),
            _f("price_gel", "number", "Цена (₾)", "Price (GEL)", "ფასი", show_in_list=True),
            _f("requires_referral", "select", "Направление", "Referral required", "მიმართuvlა", options=YES_NO),
        ),
    },
    deal_stages=(
        _st("inquiry", "Запись", "Booking", "ჩაწერა"),
        _st("preparation", "Подготовка", "Preparation", "მომზადება"),
        _st("proposal", "Кonsultation", "Consultation", "konsultacia"),
        _st("negotiation", "Лечение", "Treatment", "მკureba"),
        _st("won", "Завершено", "Completed", "დასrულებული"),
        _st("lost", "Отменено", "Cancelled", "გაუქმებული"),
    ),
    lead_statuses=(
        _st("new", "Новая запись", "New appointment", "ახალი"),
        _st("contacted", "Подтверждена", "Confirmed", "დადასტურებული"),
        _st("in_progress", "Ожидание приёма", "Awaiting visit", "მოლოდinა"),
        _st("converted", "Приём состоялся", "Completed", "შესრულებული"),
        _st("rejected", "Перенесена", "Rescheduled", "გადატanili"),
        _st("junk", "Не явился", "No-show", "არ გამოცხad"),
    ),
    hide_base_fields={"leads": ("amount", "source")},
)

# ─── LOGISTICS ───────────────────────────────────────────────────────────────

LOGISTICS_SERVICES = (
    _svc("shipments", "Управление перевозками", "Shipment management", "გადაზიდვები"),
    _svc("clients", "Клиенты и контракты", "Clients & contracts", "კლიენტები"),
    _svc("fleet", "Автопарк и водители", "Fleet & drivers", "ავtoпarki"),
    _svc("routes", "Маршруты по Грузии и за рубеж", "Routes in Georgia & abroad", "maršrutebi"),
    _svc("warehouse", "Складские операции", "Warehouse operations", "საწყობი"),
    _svc("tracking", "Отслеживание грузов", "Cargo tracking", "tracking"),
    _svc("finance", "Счета и RS.ge", "Invoicing & RS.ge", "RS.ge"),
    _svc("inbox", "WhatsApp / Telegram для клиентов", "Client messaging", "მესენჯერები"),
    _svc("bots", "Бот статуса доставки", "Delivery status bot", "ბოტი"),
    _svc("integrations", "Интеграции Meta", "Meta integrations", "ინტegracia"),
)

LOGISTICS_CONFIG = CrmTypeConfig(
    crm_type="logistics",
    modules=_mods("schedule"),
    services=LOGISTICS_SERVICES,
    labels=_labels(
        leads=L("Заявки на перевозку", "Shipping requests", "მოთხოვნები"),
        deals=L("Перевозки", "Shipments", "გადაზიდვები"),
        contacts=L("Диспетчеры / водители", "Dispatchers & drivers", "დისпetчerები"),
        companies=L("Клиенты", "Clients", "კლიენტები"),
        products=L("Тарифы и услуги", "Rates & services", "tarifebi"),
        warehouse=L("Транзитный склад", "Transit warehouse", "საწყობი"),
        movements=L("Складские операции", "Warehouse ops", "ოპeraции"),
        inbox=L("Сообщения клиентам", "Client messages", "შეტყობინებები"),
        bots=L("Бот отслеживания", "Tracking bot", "ბოტი"),
        accounting=L("Расчёты и RS.ge", "Billing & RS.ge", "RS.ge"),
        schedule=L("График рейсов", "Shipment schedule", "რeisebis grafiki"),
    ),
    fields={
        "leads": (
            _f("cargo_type", "select", "Тип груза", "Cargo type", "ტვირთი", show_in_list=True, options=CARGO_TYPES),
            _f("weight_tons", "number", "Вес (тонн)", "Weight (tons)", "წონა", show_in_list=True),
            _f("route_from", "text", "Откуда", "From", "საიდan", show_in_list=True),
            _f("route_to", "text", "Куда", "To", "სად", show_in_list=True),
            _f("loading_date", "date", "Дата погрузки", "Loading date", "ჩატვირთვა", show_in_list=True),
            _f("vehicle_type", "text", "Транспорт", "Vehicle", "транспорт"),
            _f("customs_needed", "select", "Таможня", "Customs", "sasqmelebi", options=YES_NO),
        ),
        "deals": (
            _f("cargo_type", "select", "Тип груза", "Cargo type", "ტვირთი", show_in_list=True, options=CARGO_TYPES),
            _f("weight_tons", "number", "Вес (тонн)", "Weight (tons)", "წონა", show_in_list=True, required=True),
            _f("route_from", "text", "Откуда", "From", "საიდan", show_in_list=True),
            _f("route_to", "text", "Куда", "To", "სად", show_in_list=True),
            _f("vehicle_type", "text", "Транспорт", "Vehicle", "транспорт", show_in_list=True),
            _f("loading_date", "date", "Дата погрузки", "Loading date", "ჩატვირთვა", show_in_list=True),
            _f("delivery_date", "date", "Дата доставки", "Delivery date", "მიწოდება", show_in_list=True),
            _f("tracking_number", "text", "№ отслеживания", "Tracking #", "tracking", show_in_list=True),
        ),
        "contacts": (
            _f("driver_license", "text", "Водит. удостоверение", "Driver license", "მართვის მოწმ.", show_in_list=True),
            _f("vehicle_plate", "text", "Гос. номер", "Plate #", "nomeri", show_in_list=True),
            _f("role", "select", "Роль", "Role", "როლი", options=(
                FieldOption("driver", L("Водитель", "Driver", "მძღოლი")),
                FieldOption("dispatcher", L("Диспетчер", "Dispatcher", "დиспetчer")),
                FieldOption("manager", L("Менеджер", "Manager", "მeneჯeri")),
            )),
            _f("phone_backup", "phone", "Резервный тел.", "Backup phone", "rezervi"),
        ),
        "companies": (
            _f("fleet_size", "number", "Автопарк", "Fleet size", "ავtoпarki", show_in_list=True),
            _f("regular_routes", "textarea", "Регулярные маршруты", "Regular routes", "maršrutebi"),
            _f("tin", "text", "ИНН / ს/ნ", "TIN", "ს/ნ", show_in_list=True),
            _f("contract_type", "select", "Тип договора", "Contract type", "ხელშ.", options=(
                FieldOption("spot", L("Разовая", "Spot", "ერთჯერადი")),
                FieldOption("regular", L("Регулярная", "Regular", "რegulirebuli")),
            )),
            _f("payment_terms", "text", "Условия оплаты", "Payment terms", "პირობები"),
        ),
        "products": (
            _f("rate_per_km", "number", "Тариф (₾/км)", "Rate (GEL/km)", "tarifi", show_in_list=True),
            _f("min_weight", "number", "Мин. вес (т)", "Min weight (t)", "min"),
            _f("cargo_type", "select", "Тип груза", "Cargo type", "ტვირთი", options=CARGO_TYPES),
            _f("transit_days", "number", "Срок (дн.)", "Transit days", "დღეები"),
        ),
    },
    deal_stages=(
        _st("inquiry", "Заявка", "Request", "მოთხოვნა"),
        _st("quote", "Расчёт", "Quote", "расчёт"),
        _st("contract", "Договор", "Contract", "ხელშეკრულება"),
        _st("scheduled", "Запланировано", "Scheduled", "დაგეგმილი"),
        _st("in_transit", "В пути", "In transit", "გზაში"),
        _st("delivered", "Доставлено", "Delivered", "მიწოდებული"),
        _st("cancelled", "Отменено", "Cancelled", "გაუქმებული"),
    ),
    lead_statuses=(
        _st("new", "Новая заявка", "New request", "ახალი"),
        _st("contacted", "Расчёт стоимости", "Quote sent", "kalkulacia"),
        _st("in_progress", "Согласование", "Negotiation", "მოლაპარაკება"),
        _st("converted", "Заказ принят", "Order accepted", "მიღებული"),
        _st("rejected", "Отказ", "Rejected", "უარი"),
        _st("junk", "Некачественный", "Junk", "უხარისხო"),
    ),
)

# ─── SERVICES ────────────────────────────────────────────────────────────────

SERVICES_SERVICES = (
    _svc("requests", "Заявки на услуги", "Service requests", "მოთხოვნები"),
    _svc("projects", "Управление проектами", "Project management", "проекты"),
    _svc("clients", "База клиентов", "Client database", "კლიენტები"),
    _svc("catalog", "Каталог услуг", "Services catalog", "კატალოგი"),
    _svc("contracts", "Договоры и КП", "Contracts & quotes", "ხელშეკრულებები"),
    _svc("finance", "Счета и RS.ge", "Invoicing & RS.ge", "RS.ge"),
    _svc("inbox", "WhatsApp / Telegram / Email", "Client messaging", "მესენჯერები"),
    _svc("bots", "Бот заявок и статуса", "Request status bot", "ბოტი"),
    _svc("integrations", "Интеграции Meta", "Meta integrations", "ინტegracia"),
    _svc("rbac", "Роли: менеджер, исполнитель", "Staff roles", "როლები"),
)

SERVICES_CONFIG = CrmTypeConfig(
    crm_type="services",
    modules=_mods("schedule"),
    services=SERVICES_SERVICES,
    labels=_labels(
        leads=L("Заявки на услуги", "Service requests", "მოთხოვნები"),
        deals=L("Проекты", "Projects", "проекты"),
        contacts=L("Клиенты", "Clients", "კლიენტები"),
        companies=L("Компании-клиенты", "Client companies", "კომპანიები"),
        products=L("Услуги", "Services", "სერვისები"),
        warehouse=L("Материалы / ресурсы", "Materials / resources", "რესursები"),
        movements=L("Выдача ресурсов", "Resource allocation", "გაცემა"),
        inbox=L("Сообщения клиентам", "Client messages", "შეტყობინებები"),
        bots=L("Бот заявок", "Request bot", "ბოტი"),
        accounting=L("Счета и RS.ge", "Invoicing & RS.ge", "RS.ge"),
        schedule=L("Календарь проектов", "Project calendar", "проекtiuri kalendar"),
    ),
    fields={
        "leads": (
            _f("service_type", "select", "Тип услуги", "Service type", "სერვისი", show_in_list=True, required=True, options=SERVICE_TYPES),
            _f("budget", "number", "Бюджет (₾)", "Budget (GEL)", "ბюджet", show_in_list=True),
            _f("deadline", "date", "Желаемый срок", "Desired deadline", "ვადა", show_in_list=True),
            _f("brief", "textarea", "Описание задачи", "Brief", "აღწერა"),
            _f("city", "select", "Город", "City", "ქალაქი", options=GEO_CITIES, show_in_list=True),
            _f("source_channel", "select", "Источник", "Source", "წყარო", options=(
                FieldOption("website", L("Сайт", "Website", "საიტი")),
                FieldOption("referral", L("Рекомендация", "Referral", "რекomendacia")),
                FieldOption("social", L("Соцсети", "Social media", "სოცial")),
                FieldOption("partner", L("Партнёр", "Partner", "პარტნიორი")),
            )),
            _f("urgency", "select", "Срочность", "Urgency", "სიმძიმe", options=(
                FieldOption("normal", L("Обычная", "Normal", "ჩვეულებრივი")),
                FieldOption("urgent", L("Срочная", "Urgent", "სასწრაფო")),
            )),
        ),
        "deals": (
            _f("scope", "textarea", "Объём работ", "Scope", "მ объём", show_in_list=True),
            _f("hourly_rate", "number", "Ставка (₾/ч)", "Hourly rate", "stavka", show_in_list=True),
            _f("contract_type", "select", "Тип договора", "Contract type", "ხელშ.", options=(
                FieldOption("fixed", L("Фиксированная цена", "Fixed price", "фикс")),
                FieldOption("hourly", L("Почасовая", "Hourly", "საათობრივი")),
                FieldOption("retainer", L("Абонемент", "Retainer", "abonement")),
            ), show_in_list=True),
            _f("start_date", "date", "Дата начала", "Start date", "დაწყება", show_in_list=True),
            _f("end_date", "date", "Дата окончания", "End date", "დასrულება"),
            _f("project_manager", "text", "Менеджер проекта", "Project manager", "მeneჯeri", show_in_list=True),
            _f("payment_method", "select", "Оплата", "Payment", "გადახდა", options=PAYMENT_METHODS),
            _f("milestones", "textarea", "Этапы / вехи", "Milestones", "etapebi"),
        ),
        "contacts": (
            _f("company_role", "text", "Роль в компании", "Company role", "роль", show_in_list=True),
            _f("preferred_contact", "select", "Связь", "Contact via", "კავშირი", options=(
                FieldOption("phone", L("Телефон", "Phone", "ტელეფონი")),
                FieldOption("email", L("Email", "Email", "ელ-ფოსტა")),
                FieldOption("whatsapp", L("WhatsApp", "WhatsApp", "WhatsApp")),
            )),
            _f("decision_maker", "select", "ЛПР", "Decision maker", "გადამწყვეტი", options=YES_NO),
            _f("industry", "text", "Отрасль", "Industry", "ინდუსტრია"),
            _f("client_since", "date", "Клиент с", "Client since", "კლიენტი"),
        ),
        "companies": (
            _f("industry", "text", "Отрасль", "Industry", "ინდუსტრია", show_in_list=True),
            _f("employee_count", "number", "Сотрудников", "Employees", "თანამშ."),
            _f("tin", "text", "ИНН / ს/ნ", "TIN", "ს/ნ", show_in_list=True),
            _f("contract_value", "number", "Сумма контракта (₾)", "Contract value", "ღირებულება"),
            _f("account_manager", "text", "Менеджер", "Account manager", "მeneჯeri", show_in_list=True),
        ),
        "products": (
            _f("service_type", "select", "Тип", "Type", "ტიპი", options=SERVICE_TYPES, show_in_list=True),
            _f("hourly_rate", "number", "Ставка (₾/ч)", "Hourly rate", "stavka", show_in_list=True),
            _f("delivery_days", "number", "Срок (дн.)", "Delivery days", "დღეები"),
            _f("includes", "textarea", "Включено", "Includes", "შედის"),
            _f("min_budget", "number", "Мин. бюджет (₾)", "Min budget", "min"),
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
    lead_statuses=(
        _st("new", "Новая заявка", "New request", "ახალი"),
        _st("contacted", "Связались", "Contacted", "დაკავშ."),
        _st("in_progress", "Подготовка КП", "Quote in progress", "შეთავაზება"),
        _st("converted", "Проект запущен", "Project started", "დაწყებული"),
        _st("rejected", "Отказ", "Rejected", "უარი"),
        _st("junk", "Спам", "Spam", "სპამი"),
    ),
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
