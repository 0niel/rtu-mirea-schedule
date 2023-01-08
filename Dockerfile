FROM tiangolo/uvicorn-gunicorn-fastapi:latest

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/

WORKDIR /app/

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY /app/ /app/app/

ENV PORT="${PORT:-5000}"
ENV APP_MODULE="app.main:app"