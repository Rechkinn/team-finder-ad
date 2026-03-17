# TeamFinder

Платформа для поиска команды на pet-проекты. Вариант 2 (навыки пользователей и фильтрация).

## Запуск проекта

### 1. Клонировать репозиторий и перейти в папку
```bash
git clone <ссылка на репозиторий>
cd team-finder-ad
```

### 2. Создать и активировать виртуальное окружение
```bash
python3 -m venv venv
source venv/bin/activate  # Mac
```

### 3. Установить зависимости
```bash
pip install -r requirements.txt
```

### 4. Создать .env файл
```bash
cp .env_example .env
```

Заполнить `.env`:
```
DJANGO_SECRET_KEY=django-insecure-your-secret-key
DJANGO_DEBUG=True
POSTGRES_DB=team_finder
POSTGRES_USER=team_finder
POSTGRES_PASSWORD=team_finder
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
TASK_VERSION=2
```

### 5. Запустить базу данных через Docker
```bash
docker compose up -d
```

### 6. Применить миграции
```bash
python manage.py migrate
```

### 7. Запустить сервер
```bash
python manage.py runserver
```

Проект доступен по адресу: **http://localhost:8000**

---

## Тестовые аккаунты

| Email | Пароль | Роль |
|-------|-------|------|
| admin@mail.ru | admin | Администратор |
| ivan@mail.ru | password123 | Пользователь |
| maria@mail.ru | password123 | Пользователь |
| dmitry@mail.ru | password123 | Пользователь |

