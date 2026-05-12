# AskIt

Веб-приложение для вопросов и ответов на Django.

## Страницы

| URL | Описание |
|-----|----------|
| `/` | Новые вопросы (главная) |
| `/hot/` | Лучшие вопросы |
| `/tag/<tag>/` | Вопросы по тегу |
| `/question/<id>/` | Страница вопроса с ответами |
| `/ask/` | Задать вопрос |
| `/login/` | Вход |
| `/signup/` | Регистрация |
| `/profile/` | Профиль |
| `/admin/` | Панель администратора |

## Локальный запуск

Требуется PostgreSQL. Проще всего поднять через Docker:

```bash
docker run -d --name askit-db \
  -e POSTGRES_DB=askit \
  -e POSTGRES_USER=askit \
  -e POSTGRES_PASSWORD=askit \
  -p 5432:5432 postgres:16-alpine
```

Затем:

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# заполнить SECRET_KEY и параметры БД в .env

python manage.py migrate
python manage.py createsuperuser
python manage.py fill_db 100

python manage.py runserver
```

Открыть http://localhost:8000

## Запуск через Docker

```bash
cp .env.example .env.docker
# заполнить .env.docker

docker compose up --build -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py fill_db 100
```

Открыть http://localhost:8000

## fill_db

Заполняет базу тестовыми данными. Аргумент `ratio` задаёт объём:

| Сущность | Количество |
|----------|------------|
| Пользователи | ratio |
| Вопросы | ratio × 10 |
| Ответы | ratio × 100 |
| Теги | ratio |
| Лайки | ratio × 200 |

```bash
python manage.py fill_db 10000
```

## Структура проекта

```
├── application/        # Настройки Django и маршруты
├── core/               # Профили пользователей
├── questions/          # Вопросы, ответы, теги, лайки
│   └── management/commands/fill_db.py
├── templates/          # Базовые шаблоны
├── static/
├── media/
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```
