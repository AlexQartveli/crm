# BitrixCRM — CRM + Склад

Система управления клиентами и складом по принципу **Битрикс24**. Включает CRM-модули (лиды, сделки, контакты, компании) и складской учёт (товары, остатки, движения).

## Возможности

### CRM
- **Лиды** — входящие заявки с управлением статусами
- **Сделки** — воронка продаж (канбан-доска) с 6 стадиями
- **Контакты** — база контактных лиц с привязкой к компаниям
- **Компании** — карточки организаций с реквизитами
- **Дашборд** — сводная аналитика по CRM и складу

### Склад
- **Товары** — каталог с артикулами, ценами и единицами измерения
- **Склады** — несколько складов с остатками
- **Остатки** — количество, резерв, доступно
- **Движения** — приход, расход, перемещение, корректировка

## Стек технологий

| Компонент | Технология |
|-----------|-----------|
| Backend   | Python, FastAPI, SQLAlchemy, SQLite |
| Frontend  | React, TypeScript, Tailwind CSS, Vite |
| API       | REST, OpenAPI (Swagger) |

## Быстрый старт

### Docker Compose

```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

### Локальный запуск

**Backend:**

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

## API

Все эндпоинты доступны по префиксу `/api`:

| Модуль | Эндпоинты |
|--------|-----------|
| CRM | `/api/crm/leads`, `/api/crm/deals`, `/api/crm/contacts`, `/api/crm/companies` |
| Склад | `/api/warehouse/products`, `/api/warehouse/warehouses`, `/api/warehouse/stocks`, `/api/warehouse/movements` |
| Аналитика | `/api/dashboard` |

При первом запуске база автоматически заполняется демо-данными.

## Архитектура

```
backend/
  app/
    models/      — SQLAlchemy модели (CRM + склад)
    schemas/     — Pydantic схемы
    routers/     — API маршруты
    services/    — бизнес-логика (складские операции)
    seed.py      — демо-данные

frontend/
  src/
    pages/       — страницы (дашборд, CRM, склад)
    components/  — UI компоненты
    api/         — HTTP клиент
```

## Лицензия

MIT
