"""Типы CRM для разных отраслей (Грузия и СНГ)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CrmTypeInfo:
    id: str
    label_ru: str
    label_en: str
    label_ka: str
    desc_ru: str
    desc_en: str
    desc_ka: str
    icon: str
    features: tuple[str, ...]


CRM_TYPES: dict[str, CrmTypeInfo] = {
    "general": CrmTypeInfo(
        id="general",
        label_ru="Универсальный CRM",
        label_en="Universal CRM",
        label_ka="უნივერსალური CRM",
        desc_ru="Подходит для любого бизнеса: лиды, сделки, склад, сообщения",
        desc_en="For any business: leads, deals, warehouse, messaging",
        desc_ka="ნებისმიერი ბიზნესისთვის: ლიდები, გარიგებები, საწყობი",
        icon="briefcase",
        features=("leads", "deals", "warehouse", "inbox", "bots"),
    ),
    "education": CrmTypeInfo(
        id="education",
        label_ru="Учебные заведения",
        label_en="Education",
        label_ka="საგანმანათლებლო დაწესებულებები",
        desc_ru="Школы, колледжи, университеты, курсы — абитуриенты и студенты",
        desc_en="Schools, colleges, universities — applicants and students",
        desc_ka="სკოლები, კოლეჯები, უნივერსიტეტები — აბიტურიენტები და სტუდენტები",
        icon="graduation-cap",
        features=("leads", "deals", "contacts", "inbox"),
    ),
    "factory": CrmTypeInfo(
        id="factory",
        label_ru="Производство и фабрики",
        label_en="Manufacturing",
        label_ka="წარმოება და ფაბრიკები",
        desc_ru="Заводы, цеха, B2B-поставки, сырьё и готовая продукция",
        desc_en="Factories, plants, B2B supply, raw materials and finished goods",
        desc_ka="ფაბრიკები, B2B მიწოდება, ნედლეული და მზა პროდუქცია",
        icon="factory",
        features=("deals", "warehouse", "movements", "companies"),
    ),
    "retail": CrmTypeInfo(
        id="retail",
        label_ru="Розница и магазины",
        label_en="Retail & shops",
        label_ka="საცალო ვაჭრობა",
        desc_ru="Магазины, торговые сети, e-commerce в Грузии",
        desc_en="Shops, retail chains, e-commerce in Georgia",
        desc_ka="მაღაზიები, საცალო ქსელები, ონლაინ ვაჭრობა",
        icon="shopping-bag",
        features=("leads", "deals", "products", "warehouse", "inbox"),
    ),
    "hospitality": CrmTypeInfo(
        id="hospitality",
        label_ru="Отели и туризм",
        label_en="Hotels & tourism",
        label_ka="სასტუმროები და ტურიზმი",
        desc_ru="Отели, рестораны, туроператоры, гостевой сервис",
        desc_en="Hotels, restaurants, tour operators, guest services",
        desc_ka="სასტუმროები, რესტორნები, ტუროპერატორები",
        icon="hotel",
        features=("leads", "deals", "contacts", "inbox", "bots"),
    ),
    "construction": CrmTypeInfo(
        id="construction",
        label_ru="Строительство",
        label_en="Construction",
        label_ka="მშენებლობა",
        desc_ru="Стройкомпании, девелоперы, подрядчики, сметы и объекты",
        desc_en="Construction firms, developers, contractors, projects",
        desc_ka="სამშენებლო კომპანიები, დეველოპერები, პროექტები",
        icon="hard-hat",
        features=("deals", "companies", "warehouse", "accounting"),
    ),
    "agriculture": CrmTypeInfo(
        id="agriculture",
        label_ru="Сельское хозяйство",
        label_en="Agriculture & wine",
        label_ka="სოფლის მეურნეობა და ღვინო",
        desc_ru="Фермы, виноделие, фундук, чай, экспорт продукции",
        desc_en="Farms, wine, hazelnuts, tea, export",
        desc_ka="ფერმები, ღვინო, თხილი, ჩაი, ექსპორტი",
        icon="wheat",
        features=("deals", "products", "warehouse", "companies"),
    ),
    "medical": CrmTypeInfo(
        id="medical",
        label_ru="Медицина и клиники",
        label_en="Medical clinics",
        label_ka="მედიცინა და კლინიკები",
        desc_ru="Клиники, стоматология, диагностика, записи пациентов",
        desc_en="Clinics, dentistry, diagnostics, patient appointments",
        desc_ka="კლინიკები, სტომატოლოგია, პაციენტების ჩანაწერები",
        icon="stethoscope",
        features=("leads", "contacts", "inbox", "bots"),
    ),
    "logistics": CrmTypeInfo(
        id="logistics",
        label_ru="Логистика и перевозки",
        label_en="Logistics & transport",
        label_ka="ლოგისტია",
        desc_ru="Грузоперевозки, склады, доставка по Грузии и за рубеж",
        desc_en="Freight, warehousing, delivery across Georgia",
        desc_ka="ტვირყის გადაზიდვა, საწყობები, მიწოდება",
        icon="truck",
        features=("deals", "companies", "movements", "contacts"),
    ),
    "services": CrmTypeInfo(
        id="services",
        label_ru="Услуги и агентства",
        label_en="Services & agencies",
        label_ka="სერვისები და აგენტურები",
        desc_ru="Консалтинг, маркeting, IT, юридические и бухгалтерские услуги",
        desc_en="Consulting, marketing, IT, legal and accounting services",
        desc_ka="კონსალტინგი, მარკეტინგი, IT, სასამარტო სერვისები",
        icon="users",
        features=("leads", "deals", "contacts", "inbox"),
    ),
}

DEFAULT_CRM_TYPE = "general"
ALL_CRM_TYPE_IDS = tuple(CRM_TYPES.keys())


def get_crm_type(crm_type: str) -> CrmTypeInfo:
    return CRM_TYPES.get(crm_type, CRM_TYPES[DEFAULT_CRM_TYPE])


def is_valid_crm_type(crm_type: str) -> bool:
    return crm_type in CRM_TYPES
