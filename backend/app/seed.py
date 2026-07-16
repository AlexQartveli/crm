from app.models.crm import Company, Contact, Deal, DealProduct, Lead
from app.models.warehouse import Product, Stock, Warehouse


def seed_database(db, tenant_id: int):
    if db.query(Lead).filter(Lead.tenant_id == tenant_id).first():
        return

    leads = [
        Lead(
            tenant_id=tenant_id,
            title="Заявка с сайта",
            name="Иван Петров",
            phone="+7 999 123-45-67",
            email="ivan@example.com",
            source="Сайт",
            status="new",
            amount=150000,
        ),
        Lead(
            tenant_id=tenant_id,
            title="Звонок менеджеру",
            name="Мария Сидорова",
            phone="+7 999 234-56-78",
            source="Телефон",
            status="in_progress",
            amount=85000,
        ),
    ]
    for lead in leads:
        db.add(lead)

    companies = [
        Company(
            tenant_id=tenant_id,
            name="ООО «ТехноПром»",
            inn="7701234567",
            phone="+7 495 111-22-33",
            email="info@technoprom.ru",
            address="Москва, ул. Ленина, 1",
        ),
        Company(
            tenant_id=tenant_id,
            name="ИП Козлов А.В.",
            inn="7709876543",
            phone="+7 916 555-44-33",
            email="kozlov@mail.ru",
        ),
    ]
    for company in companies:
        db.add(company)
    db.flush()

    contacts = [
        Contact(
            tenant_id=tenant_id,
            name="Алексей Козлов",
            phone="+7 916 555-44-33",
            email="kozlov@mail.ru",
            position="Директор",
            company_id=companies[1].id,
        ),
        Contact(
            tenant_id=tenant_id,
            name="Елена Волкова",
            phone="+7 495 222-33-44",
            email="volkova@technoprom.ru",
            position="Менеджер по закупкам",
            company_id=companies[0].id,
        ),
    ]
    for contact in contacts:
        db.add(contact)
    db.flush()

    warehouses = [
        Warehouse(
            tenant_id=tenant_id,
            name="Основной склад",
            address="Москва, Складская 5",
            is_default=True,
        ),
        Warehouse(
            tenant_id=tenant_id,
            name="Склад №2",
            address="Москва, Промышленная 12",
        ),
    ]
    for wh in warehouses:
        db.add(wh)
    db.flush()

    products = [
        Product(
            tenant_id=tenant_id,
            name="Ноутбук Dell XPS 15",
            sku="NB-DELL-XPS15",
            unit="шт",
            price=125000,
        ),
        Product(
            tenant_id=tenant_id,
            name='Монитор LG 27"',
            sku="MON-LG-27",
            unit="шт",
            price=32000,
        ),
        Product(
            tenant_id=tenant_id,
            name="Клавиатура Logitech MX",
            sku="KB-LOG-MX",
            unit="шт",
            price=8500,
        ),
        Product(
            tenant_id=tenant_id,
            name="Мышь Logitech MX Master",
            sku="MS-LOG-MXM",
            unit="шт",
            price=7200,
        ),
        Product(
            tenant_id=tenant_id,
            name="Кабель HDMI 2м",
            sku="CB-HDMI-2M",
            unit="шт",
            price=450,
        ),
    ]
    for product in products:
        db.add(product)
    db.flush()

    stocks_data = [
        (products[0].id, warehouses[0].id, 15),
        (products[1].id, warehouses[0].id, 30),
        (products[2].id, warehouses[0].id, 50),
        (products[3].id, warehouses[0].id, 45),
        (products[4].id, warehouses[0].id, 200),
        (products[0].id, warehouses[1].id, 5),
        (products[1].id, warehouses[1].id, 10),
    ]
    for product_id, warehouse_id, qty in stocks_data:
        db.add(
            Stock(
                tenant_id=tenant_id,
                product_id=product_id,
                warehouse_id=warehouse_id,
                quantity=qty,
            )
        )

    deals = [
        Deal(
            tenant_id=tenant_id,
            title="Поставка IT-оборудования",
            stage="negotiation",
            amount=520000,
            contact_id=contacts[1].id,
            company_id=companies[0].id,
        ),
        Deal(
            tenant_id=tenant_id,
            title="Офисная периферия",
            stage="proposal",
            amount=89000,
            contact_id=contacts[0].id,
            company_id=companies[1].id,
        ),
        Deal(
            tenant_id=tenant_id,
            title="Мониторы для отдела",
            stage="new",
            amount=192000,
            contact_id=contacts[1].id,
            company_id=companies[0].id,
        ),
        Deal(
            tenant_id=tenant_id,
            title="Кабельная продукция",
            stage="won",
            amount=45000,
            contact_id=contacts[0].id,
            company_id=companies[1].id,
        ),
    ]
    for deal in deals:
        db.add(deal)
    db.flush()

    deal_products = [
        DealProduct(
            tenant_id=tenant_id,
            deal_id=deals[0].id,
            product_id=products[0].id,
            quantity=3,
            price=125000,
        ),
        DealProduct(
            tenant_id=tenant_id,
            deal_id=deals[0].id,
            product_id=products[1].id,
            quantity=5,
            price=32000,
        ),
        DealProduct(
            tenant_id=tenant_id,
            deal_id=deals[1].id,
            product_id=products[2].id,
            quantity=5,
            price=8500,
        ),
        DealProduct(
            tenant_id=tenant_id,
            deal_id=deals[1].id,
            product_id=products[3].id,
            quantity=5,
            price=7200,
        ),
    ]
    for dp in deal_products:
        db.add(dp)

    db.commit()
