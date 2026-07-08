# Как открыть Kinetix с телефона

## Адрес

### https://alexqartveli.github.io/crm/

---

## Если не открывается

### 1. Включите GitHub Pages

1. Откройте: **https://github.com/AlexQartveli/crm/settings/pages**
2. **Source:** Deploy from a branch
3. **Branch:** `gh-pages` → `/ (root)`
4. **Save**

### 2. Подключите backend на Render

1. **https://render.com** → войти через GitHub
2. **New → Blueprint** → репозиторий `AlexQartveli/crm`
3. **Apply**

API: https://kinetix-api.onrender.com

> Первый запрос после простоя может идти ~30 секунд.

---

## Создать отдельный репозиторий `kinetix`

```bash
git clone https://github.com/AlexQartveli/crm.git kinetix
cd kinetix
gh repo create kinetix --public --source=. --push
```

Потом в **Settings → Pages** включите ветку `gh-pages`.

Адрес: **https://alexqartveli.github.io/kinetix/**
