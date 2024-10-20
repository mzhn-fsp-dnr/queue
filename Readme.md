# Сервис очереди

## Стек

`Python`, `sqlalchemy`, `Pydantic`, `alembic`, `fastapi`, `sqlmodel`

## Описание сервиса

Сервис отвечает за работу главной очереди, выдачи данных для аналитики.

## Структура проекта

```python

├── Dockerfile
├── api # Директория с приложением
│   ├── conifg.py # Конфигурация
│   ├── database.py # Настройка подключения к БД
│   ├── models # Модели БД
│   ├── routers # HTTP роутер
│   ├── schemas # Схемы sqlmodel
│   └── services # Слой сервисов
├── docker-compose.yml
├── main.py # Точка входа
└── requirements.txt
```
## Развертывание проекта

1. Склонируйте репозиторий

```bash
git clone https://github.com/mzhn-fsp-dnr/queue.git
```

2. Настройте приложение путем редактирования `.env` файла. Пример расположен в `.example.env`

3. Запустите приложение в Docker

```bash
docker compose up
```