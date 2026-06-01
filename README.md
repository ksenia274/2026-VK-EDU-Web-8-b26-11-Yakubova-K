# AskIt

Веб-приложение для вопросов и ответов на Django.

## Страницы и API

| URL | Метод | Описание |
|-----|-------|----------|
| `/` | GET | Новые вопросы (главная) |
| `/hot/` | GET | Лучшие вопросы |
| `/tag/<tag>/` | GET | Вопросы по тегу |
| `/question/<id>/` | GET, POST | Страница вопроса с ответами |
| `/ask/` | GET, POST | Задать вопрос |
| `/login/` | GET, POST | Вход (поддерживает `?next=`) |
| `/signup/` | GET, POST | Регистрация |
| `/profile/` | GET, POST | Редактирование профиля и аватарки |
| `/logout/` | POST | Выход |
| `/admin/` | GET | Панель администратора |
| `/like/question/` | POST | AJAX: лайк/дизлайк вопроса → `{rating, user_vote}` |
| `/like/answer/` | POST | AJAX: лайк/дизлайк ответа → `{rating, user_vote}` |
| `/mark-correct/` | POST | AJAX: отметить правильный ответ → `{is_correct, answer_id}` |

## Локальный запуск (без Docker)

Требуется PostgreSQL с базой `askit` и пользователем `askit`.

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

Скопировать `.env.local` в `.env` и убедиться, что `DEBUG=True` (нужно для раздачи media-файлов через Django):

```bash
# Windows:
copy .env.local .env
# Linux/macOS:
cp .env.local .env
```

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py fill_db 100

python manage.py runserver
```

Открыть http://localhost:8000

## Запуск через Docker

`.env.docker` уже настроен (DB_HOST=db). Просто:

```bash
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
├── core/               # Авторизация, регистрация, профили
│   ├── models.py       # Profile (аватарка с UUID-именем)
│   └── forms.py        # Валидация аватарки (расширение, размер)
├── questions/          # Вопросы, ответы, теги, лайки
│   ├── views.py        # + AJAX: like_question, like_answer, mark_correct
│   └── management/commands/fill_db.py
├── templates/          # Базовые шаблоны
├── static/
│   ├── css/
│   │   ├── bootstrap-icons.min.css   # Bootstrap Icons (локально)
│   │   └── fonts/
│   └── js/
│       └── main.js     # jQuery AJAX: лайки и правильный ответ
├── media/              # Загруженные аватарки
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example        # Шаблон переменных окружения
├── .env.local          # Локальная разработка (DEBUG=True, DB_HOST=localhost)
└── .env.docker         # Docker (DEBUG=True, DB_HOST=db)
```
