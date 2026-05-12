# AskIt

Q&A web application built with Django.

## Pages

| URL | Description |
|-----|-------------|
| `/` | New questions (home) |
| `/hot/` | Hot questions |
| `/tag/<tag>/` | Questions by tag |
| `/question/<id>/` | Single question with answers |
| `/ask/` | Ask a question |
| `/login/` | Login form |
| `/signup/` | Registration form |
| `/profile/` | Edit profile |

## Local Setup

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver
```

Open http://localhost:8000 in your browser.

## Docker Setup

```bash
docker compose up --build
```

Open http://localhost:8000

## Project Structure

```
2026-VK-EDU-Web-8-b26-11-Yakubova-K/
├── application/          
├── core/                 
│   ├── templates/core/
│   └── static/core/
├── questions/           
│   ├── templates/questions/
│   └── static/questions/
├── templates/            
│   ├── base.html
│   └── includes/
├── static/              
├── media/                
├── public/              
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── .gitignore
```
