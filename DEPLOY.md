# Как открыть CRM с телефона

## Почему был 404

Вы открыли **https://alexqartveli.github.io/** — это другой сайт (репозиторий `alexqartveli.github.io`).

CRM лежит в репозитории **`-`** и будет доступен по адресу:

## https://alexqartveli.github.io/-/

Но сначала нужно **один раз включить GitHub Pages** (2 минуты):

---

## Шаг 1. Включите GitHub Pages

1. Откройте: **https://github.com/AlexQartveli/-/settings/pages**
2. **Source:** Deploy from a branch
3. **Branch:** `gh-pages` → `/ (root)`
4. Нажмите **Save**

Через 1–2 минуты откройте на телефоне:

### https://alexqartveli.github.io/-/

---

## Шаг 2. Запустите backend (для данных CRM)

1. Зайдите на **https://render.com** → войдите через GitHub
2. **New → Blueprint**
3. Выберите репозиторий `AlexQartveli/-`
4. Нажмите **Apply**

API: https://bitrix-crm-api.onrender.com

> Первый запрос после простоя может идти ~30 секунд (бесплатный тариф Render).

---

## Создать отдельный репозиторий `bitrix-crm`

Если хотите отдельный проект (не `-`), выполните на компьютере:

```bash
git clone https://github.com/AlexQartveli/-.git bitrix-crm
cd bitrix-crm
gh repo create bitrix-crm --public --source=. --push
```

Потом в **Settings → Pages** нового репозитория включите ветку `gh-pages`.

Адрес будет: **https://alexqartveli.github.io/bitrix-crm/**
