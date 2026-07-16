"""Стартовые данные CRM по отраслевым шаблонам."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.crm_types import DEFAULT_CRM_TYPE
from app.models.crm import Company, Contact, Deal, DealProduct, Lead
from app.models.warehouse import Product, Stock, Warehouse
from app.seed_bots import seed_bots


def _already_seeded(db: Session, tenant_id: int) -> bool:
    return db.query(Lead).filter(Lead.tenant_id == tenant_id).first() is not None


def _seed_bundle(
    db: Session,
    tenant_id: int,
    *,
    leads: list[dict],
    companies: list[dict],
    contacts: list[dict],
    warehouses: list[dict],
    products: list[dict],
    stocks: list[tuple[int, int, float]],
    deals: list[dict],
    deal_products: list[tuple[int, int, float, float]],
) -> None:
    company_objs: list[Company] = []
    for c in companies:
        obj = Company(tenant_id=tenant_id, **c)
        db.add(obj)
        company_objs.append(obj)
    db.flush()

    contact_objs: list[Contact] = []
    for i, c in enumerate(contacts):
        data = dict(c)
        if "company_idx" in data:
            data["company_id"] = company_objs[data.pop("company_idx")].id
        contact_objs.append(Contact(tenant_id=tenant_id, **data))
        db.add(contact_objs[-1])
    db.flush()

    for L in leads:
        db.add(Lead(tenant_id=tenant_id, **L))

    wh_objs: list[Warehouse] = []
    for w in warehouses:
        obj = Warehouse(tenant_id=tenant_id, **w)
        db.add(obj)
        wh_objs.append(obj)
    db.flush()

    prod_objs: list[Product] = []
    for p in products:
        obj = Product(tenant_id=tenant_id, **p)
        db.add(obj)
        prod_objs.append(obj)
    db.flush()

    for prod_idx, wh_idx, qty in stocks:
        db.add(Stock(
            tenant_id=tenant_id,
            product_id=prod_objs[prod_idx].id,
            warehouse_id=wh_objs[wh_idx].id,
            quantity=qty,
        ))

    deal_objs: list[Deal] = []
    for d in deals:
        data = dict(d)
        if "contact_idx" in data:
            data["contact_id"] = contact_objs[data.pop("contact_idx")].id
        if "company_idx" in data:
            data["company_id"] = company_objs[data.pop("company_idx")].id
        obj = Deal(tenant_id=tenant_id, **data)
        db.add(obj)
        deal_objs.append(obj)
    db.flush()

    for deal_idx, prod_idx, qty, price in deal_products:
        db.add(DealProduct(
            tenant_id=tenant_id,
            deal_id=deal_objs[deal_idx].id,
            product_id=prod_objs[prod_idx].id,
            quantity=qty,
            price=price,
        ))

    db.commit()


_TEMPLATES: dict[str, dict] = {
    "general": {
        "leads": [
            {"title": "Заявка с сайта", "name": "გიორგი ბერიძე", "phone": "+995 555 12 34 56", "source": "Сайт", "status": "new", "amount": 1500},
            {"title": "Звонок менеджеру", "name": "ნინო კვარაცხელია", "phone": "+995 599 98 76 54", "source": "Телефон", "status": "in_progress", "amount": 850},
        ],
        "companies": [
            {"name": "LLC «TechGeorgia»", "inn": "405123456", "phone": "+995 32 2 12 34 56", "email": "info@techgeorgia.ge", "address": "თბილისი, რუსთაველის გამზ. 12"},
            {"name": "ივ. მელაძის ИП", "inn": "010987654", "phone": "+995 555 44 33 22", "email": "meladze@mail.ge"},
        ],
        "contacts": [
            {"name": "ივane მელაძე", "phone": "+995 555 44 33 22", "email": "meladze@mail.ge", "position": "Director", "company_idx": 1},
            {"name": "ელენე ვოლკova", "phone": "+995 32 2 22 33 44", "email": "volkova@techgeorgia.ge", "position": "Purchasing", "company_idx": 0},
        ],
        "warehouses": [
            {"name": "მთავარი საწყობი", "address": "თბილისი, საწყობის ქ. 5", "is_default": True},
        ],
        "products": [
            {"name": "ნოუთბუქი Dell XPS", "sku": "NB-DELL", "unit": "шт", "price": 3200},
            {"name": "მონიტორი LG 27\"", "sku": "MON-LG27", "unit": "шт", "price": 890},
        ],
        "stocks": [(0, 0, 15), (1, 0, 30)],
        "deals": [
            {"title": "IT მოწყობილობის მიწოდება", "stage": "negotiation", "amount": 12500, "contact_idx": 1, "company_idx": 0},
            {"title": "ოფისის აქსესუარები", "stage": "proposal", "amount": 2100, "contact_idx": 0, "company_idx": 1},
        ],
        "deal_products": [(0, 0, 3, 3200), (0, 1, 5, 890)],
    },
    "education": {
        "leads": [
            {"title": "აბიტურიენტი — ბიზнес-админისტრaciა", "name": "სალომე გრძელიძე", "phone": "+995 555 11 22 33", "source": "Facebook", "status": "new", "amount": 4500},
            {"title": "მagistratura — IT", "name": "დavit ხარაძე", "phone": "+995 599 55 66 77", "source": "Open Day", "status": "in_progress", "amount": 6200},
            {"title": "კურსი — ინგლისური B2", "name": "მარიამ ჯანელidze", "phone": "+995 555 88 99 00", "source": "Сайт", "status": "new", "amount": 890},
        ],
        "companies": [
            {"name": "თბილისის საერთაშორისო უნივერსიტეტი", "inn": "205012345", "phone": "+995 32 2 00 11 22", "address": "თბილისი, კostaვის ქ. 77"},
            {"name": "LLC «GeoSchool»", "inn": "402334455", "phone": "+995 32 2 33 44 55", "email": "info@geoschool.ge"},
        ],
        "contacts": [
            {"name": "ნინo ბაკრadze", "phone": "+995 555 22 33 44", "email": "nino@geoschool.ge", "position": "Admissions", "company_idx": 1},
            {"name": "გიორგი მაისურadze", "phone": "+995 599 11 22 33", "position": "Dean", "company_idx": 0},
        ],
        "warehouses": [{"name": "სასწავლო მასალები", "address": "თბილისი", "is_default": True}],
        "products": [
            {"name": "ბакалavri — Business Admin (1 წელი)", "sku": "PROG-BBA", "unit": "курс", "price": 4500},
            {"name": "მagistratura — IT Management", "sku": "PROG-MIT", "unit": "курс", "price": 6200},
            {"name": "ინგლისური B2 — 6 თვე", "sku": "CRS-ENG-B2", "unit": "курс", "price": 890},
        ],
        "stocks": [],
        "deals": [
            {"title": "სალომე — BBA 2026", "stage": "negotiation", "amount": 4500, "contact_idx": 0, "company_idx": 1},
            {"title": "Corporate training — GeoBank", "stage": "proposal", "amount": 12000, "company_idx": 0},
        ],
        "deal_products": [(0, 0, 1, 4500), (1, 1, 2, 6200)],
    },
    "factory": {
        "leads": [
            {"title": "Запрос на оптовую поставку", "name": "Zurab Kiknadze", "phone": "+995 555 33 44 55", "source": "B2B портал", "status": "new", "amount": 45000},
            {"title": "Тender — металлоконструкции", "name": "LLC MetalPro", "phone": "+995 32 2 55 66 77", "source": "Tender", "status": "in_progress", "amount": 120000},
        ],
        "companies": [
            {"name": "ქარხანა «Rustavi Steel»", "inn": "204556677", "phone": "+995 341 25 25 25", "address": "რუსთავი, ინდustriული ზონა"},
            {"name": "LLC «Caucasus Packaging»", "inn": "401998877", "phone": "+995 32 2 77 88 99", "address": "თბილისი, გარდabani"},
        ],
        "contacts": [
            {"name": "Zurab Kiknadze", "phone": "+995 555 33 44 55", "position": "Procurement", "company_idx": 1},
            {"name": "Levan Gvasalia", "phone": "+995 341 25 25 26", "position": "Sales Director", "company_idx": 0},
        ],
        "warehouses": [
            {"name": "ქვეული საწყობი", "address": "რუსთავი", "is_default": True},
            {"name": "მზა პროდუქცია", "address": "რუსთავი", "is_default": False},
        ],
        "products": [
            {"name": "Сталь лист 3мм", "sku": "STL-3MM", "unit": "т", "price": 850},
            {"name": "Упаковка картонная", "sku": "PKG-CRD", "unit": "уп", "price": 2.5},
            {"name": "Профиль алюминиевый", "sku": "ALU-PRF", "unit": "м", "price": 12},
        ],
        "stocks": [(0, 0, 120), (1, 0, 5000), (2, 1, 800)],
        "deals": [
            {"title": "Поставка стали — MetalPro", "stage": "negotiation", "amount": 45000, "contact_idx": 0, "company_idx": 1},
            {"title": "Экспорт в Турцию", "stage": "won", "amount": 98000, "contact_idx": 1, "company_idx": 0},
        ],
        "deal_products": [(0, 0, 50, 850), (1, 1, 10000, 2.5)],
    },
    "retail": {
        "leads": [
            {"title": "Заказ онлайн — доставка", "name": "Ana Beridze", "phone": "+995 555 66 77 88", "source": "Instagram", "status": "new", "amount": 320},
            {"title": "Опт для магазина", "name": "Shop «Moda GE»", "phone": "+995 32 2 99 88 77", "source": "WhatsApp", "status": "in_progress", "amount": 4500},
        ],
        "companies": [
            {"name": "მაღაზია «Moda GE»", "inn": "403112233", "phone": "+995 32 2 99 88 77", "address": "თბილისი, ვაკe"},
            {"name": "E-shop geofashion.ge", "inn": "405667788", "email": "sales@geofashion.ge"},
        ],
        "contacts": [
            {"name": "Ana Beridze", "phone": "+995 555 66 77 88", "company_idx": 1},
            {"name": "Ketevan Lomidze", "phone": "+995 32 2 99 88 78", "position": "Buyer", "company_idx": 0},
        ],
        "warehouses": [{"name": "საცალო საწყობი", "address": "თბილისი, ვაზისუბani", "is_default": True}],
        "products": [
            {"name": "Kurtukhi kali", "sku": "W-JKT-01", "unit": "шт", "price": 189},
            {"name": "Jeans", "sku": "M-JNS-02", "unit": "шт", "price": 79},
            {"name": "Chanteli", "sku": "ACC-BAG", "unit": "шт", "price": 120},
        ],
        "stocks": [(0, 0, 45), (1, 0, 120), (2, 0, 60)],
        "deals": [
            {"title": "Опт осень 2026", "stage": "proposal", "amount": 4500, "contact_idx": 1, "company_idx": 0},
            {"title": "Online order #1042", "stage": "won", "amount": 320, "contact_idx": 0},
        ],
        "deal_products": [(0, 0, 20, 189), (0, 1, 15, 79)],
    },
    "hospitality": {
        "leads": [
            {"title": "Бронь — 3 ночи", "name": "Thomas Mueller", "phone": "+49 170 1234567", "source": "Booking.com", "status": "new", "amount": 420},
            {"title": "Корпоративный ужин", "name": "Bank of Georgia", "phone": "+995 32 2 44 44 44", "source": "Email", "status": "in_progress", "amount": 3500},
            {"title": "Тур — Кахетия", "name": "Maria Rossi", "phone": "+39 333 1234567", "source": "Сайт", "status": "new", "amount": 180},
        ],
        "companies": [
            {"name": "Hotel «Tbilisi View»", "inn": "402889900", "phone": "+995 32 2 11 22 33", "address": "თბილისი, აღმაშenebeli 45"},
            {"name": "Tour Operator «Caucasus Travel»", "inn": "401776655", "phone": "+995 32 2 55 44 33"},
        ],
        "contacts": [
            {"name": "Thomas Mueller", "phone": "+49 170 1234567", "company_idx": 0},
            {"name": "Nino Chkheidze", "phone": "+995 555 00 11 22", "position": "Events Manager", "company_idx": 0},
        ],
        "warehouses": [{"name": "Housekeeping", "address": "Hotel", "is_default": True}],
        "products": [
            {"name": "Standard Room / night", "sku": "RM-STD", "unit": "ночь", "price": 95},
            {"name": "Wine tour Kakheti", "sku": "TR-KAK", "unit": "чел", "price": 90},
            {"name": "Banquet per person", "sku": "EVT-BNQ", "unit": "чел", "price": 85},
        ],
        "stocks": [],
        "deals": [
            {"title": "Booking #8821 — Mueller", "stage": "won", "amount": 420, "contact_idx": 0},
            {"title": "Corporate dinner BoG", "stage": "negotiation", "amount": 3500, "company_idx": 0},
        ],
        "deal_products": [(0, 0, 3, 95), (1, 2, 40, 85)],
    },
    "construction": {
        "leads": [
            {"title": "ЖК «Lisi Green» — подряд", "name": "DevCo Georgia", "phone": "+995 32 2 33 55 77", "source": "Tender", "status": "in_progress", "amount": 850000},
            {"title": "Ремонт офиса 200м²", "name": "Tech Startup LLC", "phone": "+995 555 77 88 99", "source": "Сайт", "status": "new", "amount": 45000},
        ],
        "companies": [
            {"name": "LLC «DevCo Georgia»", "inn": "403445566", "phone": "+995 32 2 33 55 77", "address": "თბილისი, ლისi"},
            {"name": "LLC «BuildMaster GE»", "inn": "401223344", "phone": "+995 32 2 66 77 88"},
        ],
        "contacts": [
            {"name": "Giorgi Tsereteli", "phone": "+995 555 11 55 99", "position": "Project Manager", "company_idx": 0},
            {"name": "Lasha Kapanadze", "phone": "+995 32 2 66 77 89", "position": "Estimator", "company_idx": 1},
        ],
        "warehouses": [
            {"name": "Стройплощадка Lisi", "address": "თბილისი, ლისi", "is_default": True},
            {"name": "База материалов", "address": "მtskheta", "is_default": False},
        ],
        "products": [
            {"name": "Цемент M500", "sku": "CEM-M500", "unit": "т", "price": 95},
            {"name": "Арматура 12мм", "sku": "ARM-12", "unit": "т", "price": 780},
            {"name": "Блоки газобетон", "sku": "BLK-GAS", "unit": "м³", "price": 45},
        ],
        "stocks": [(0, 0, 200), (1, 1, 50), (2, 0, 1200)],
        "deals": [
            {"title": "Lisi Green — Phase 2", "stage": "negotiation", "amount": 850000, "contact_idx": 0, "company_idx": 0},
            {"title": "Office fit-out", "stage": "proposal", "amount": 45000},
        ],
        "deal_products": [(0, 0, 500, 95), (0, 1, 30, 780)],
    },
    "agriculture": {
        "leads": [
            {"title": "Экспорт фундука в EU", "name": "Italian Buyer SRL", "phone": "+39 02 1234567", "source": "Export fair", "status": "in_progress", "amount": 65000},
            {"title": "Закуп вина оптом", "name": "Wine Shop Chain", "phone": "+995 32 2 88 99 00", "source": "Email", "status": "new", "amount": 18000},
        ],
        "companies": [
            {"name": "ღვინის მარani «Kakheti Gold»", "inn": "402334411", "phone": "+995 350 27 12 34", "address": "კахетi, სიღnაბaდo"},
            {"name": "თხili Farm «Samegrelo»", "inn": "401556677", "phone": "+995 595 11 22 33", "address": "სamegrelo"},
        ],
        "contacts": [
            {"name": "Giorgi Khutsishvili", "phone": "+995 350 27 12 35", "position": "Export", "company_idx": 0},
            {"name": "Nika Beridze", "phone": "+995 595 11 22 34", "position": "Farm Manager", "company_idx": 1},
        ],
        "warehouses": [
            {"name": "Склад урожая", "address": "Kakheti", "is_default": True},
            {"name": "Холодильник", "address": "Kakheti", "is_default": False},
        ],
        "products": [
            {"name": "Saperavi Qvevri 750ml", "sku": "WINE-SAP", "unit": "бут", "price": 18},
            {"name": "Фундук очищенный", "sku": "HAZ-NUT", "unit": "кг", "price": 8.5},
            {"name": "Чай грузинский", "sku": "TEA-GE", "unit": "кг", "price": 12},
        ],
        "stocks": [(0, 1, 5000), (1, 0, 12000), (2, 0, 800)],
        "deals": [
            {"title": "Export hazelnuts — Italy", "stage": "negotiation", "amount": 65000, "contact_idx": 1, "company_idx": 1},
            {"title": "Wine wholesale Tbilisi", "stage": "proposal", "amount": 18000, "contact_idx": 0, "company_idx": 0},
        ],
        "deal_products": [(1, 1, 5000, 8.5), (0, 0, 800, 18)],
    },
    "medical": {
        "leads": [
            {"title": "Запись — стоматология", "name": "Ekaterine Maisuradze", "phone": "+995 555 22 44 66", "source": "Сайт", "status": "new", "amount": 150},
            {"title": "Check-up корпоративный", "name": "LLC SilkNet", "phone": "+995 32 2 00 55 66", "source": "B2B", "status": "in_progress", "amount": 8500},
        ],
        "companies": [
            {"name": "კlinika «MediGeorgia»", "inn": "403998877", "phone": "+995 32 2 45 67 89", "address": "თბილისი, ვაკe"},
            {"name": "Dental Studio «Smile GE»", "inn": "401112233", "phone": "+995 32 2 11 33 55"},
        ],
        "contacts": [
            {"name": "Ekaterine Maisuradze", "phone": "+995 555 22 44 66"},
            {"name": "Dr. Nino Gabelia", "phone": "+995 32 2 11 33 56", "position": "Chief Dentist", "company_idx": 1},
        ],
        "warehouses": [{"name": "Медрасходники", "address": "Clinic", "is_default": True}],
        "products": [
            {"name": "Консультация терапевта", "sku": "SRV-CON", "unit": "усл", "price": 80},
            {"name": "Имплант стандарт", "sku": "SRV-IMP", "unit": "усл", "price": 1200},
            {"name": "Check-up Full", "sku": "SRV-CHK", "unit": "усл", "price": 250},
        ],
        "stocks": [],
        "deals": [
            {"title": "Implant — Ekaterine", "stage": "proposal", "amount": 1200, "contact_idx": 0, "company_idx": 1},
            {"title": "Corporate check-up SilkNet", "stage": "negotiation", "amount": 8500, "company_idx": 0},
        ],
        "deal_products": [(0, 1, 1, 1200), (1, 2, 30, 250)],
    },
    "logistics": {
        "leads": [
            {"title": "Перевозка Tbilisi—Poti", "name": "LLC AgroExport", "phone": "+995 555 33 55 77", "source": "Phone", "status": "new", "amount": 2800},
            {"title": "Складское хранение 3 мес", "name": "Import Company TR", "phone": "+90 212 555 1234", "source": "Email", "status": "in_progress", "amount": 4500},
        ],
        "companies": [
            {"name": "LLC «TransCaucasus Logistics»", "inn": "403776655", "phone": "+995 32 2 77 66 55", "address": "თbilisi, Lilo"},
            {"name": "Port Service Poti", "inn": "401889900", "phone": "+995 493 27 12 34", "address": "ფოთi"},
        ],
        "contacts": [
            {"name": "Giorgi Abashidze", "phone": "+995 555 33 55 77", "position": "Logistics", "company_idx": 0},
            {"name": "Murat Yilmaz", "phone": "+90 212 555 1234", "position": "Import Manager"},
        ],
        "warehouses": [
            {"name": "Склад Lilo", "address": "თbilisi", "is_default": True},
            {"name": "Terminal Poti", "address": "Poti", "is_default": False},
        ],
        "products": [
            {"name": "FTL Tbilisi—Poti", "sku": "TRK-FTL", "unit": "рейс", "price": 1400},
            {"name": "Склад м²/мес", "sku": "WH-M2", "unit": "м²", "price": 8},
            {"name": "Таможенное оформление", "sku": "SRV-CUS", "unit": "усл", "price": 350},
        ],
        "stocks": [],
        "deals": [
            {"title": "2x FTL — AgroExport", "stage": "won", "amount": 2800, "contact_idx": 0},
            {"title": "Storage 500m² × 3mo", "stage": "negotiation", "amount": 4500, "contact_idx": 1},
        ],
        "deal_products": [(0, 0, 2, 1400), (1, 1, 500, 8)],
    },
    "services": {
        "leads": [
            {"title": "Разработка сайта", "name": "Startup «FinApp»", "phone": "+995 555 44 66 88", "source": "Referral", "status": "new", "amount": 8500},
            {"title": "Бухгалтерское сопровождение", "name": "LLC Restaurant Chain", "phone": "+995 32 2 22 44 66", "source": "Сайт", "status": "in_progress", "amount": 1200},
        ],
        "companies": [
            {"name": "Agency «Digital Georgia»", "inn": "402556677", "phone": "+995 32 2 99 11 22", "address": "თbilisi"},
            {"name": "Consulting «BizSupport GE»", "inn": "401334455", "phone": "+995 32 2 44 55 66"},
        ],
        "contacts": [
            {"name": "Luka Tsiklauri", "phone": "+995 555 44 66 88", "position": "Founder", "company_idx": 0},
            {"name": "Tamuna Kvaratskhelia", "phone": "+995 32 2 44 55 67", "position": "Accountant", "company_idx": 1},
        ],
        "warehouses": [],
        "products": [
            {"name": "Website development", "sku": "SRV-WEB", "unit": "проект", "price": 8500},
            {"name": "Accounting monthly", "sku": "SRV-ACC", "unit": "мес", "price": 400},
            {"name": "Legal consultation", "sku": "SRV-LAW", "unit": "час", "price": 120},
        ],
        "stocks": [],
        "deals": [
            {"title": "FinApp — MVP website", "stage": "negotiation", "amount": 8500, "contact_idx": 0},
            {"title": "Restaurant chain — accounting", "stage": "proposal", "amount": 4800, "contact_idx": 1, "company_idx": 1},
        ],
        "deal_products": [(0, 0, 1, 8500), (1, 1, 12, 400)],
    },
}


def seed_crm_template(db: Session, tenant_id: int, crm_type: str = DEFAULT_CRM_TYPE) -> None:
    if _already_seeded(db, tenant_id):
        return

    template = _TEMPLATES.get(crm_type) or _TEMPLATES[DEFAULT_CRM_TYPE]

    if not template.get("warehouses"):
        db.add(Warehouse(tenant_id=tenant_id, name="Main", is_default=True))
        db.flush()

    _seed_bundle(db, tenant_id, **template)
    seed_bots(db, tenant_id, crm_type=crm_type)
