FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ARG APP_PORT=5000

EXPOSE ${APP_PORT}

CMD uvicorn main:app --root-path /queue --host 0.0.0.0 --port $APP_PORT