FROM tiangolo/uvicorn-gunicorn-fastapi:latest

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/

WORKDIR /app/

RUN apt-get update && \
    apt-get install -y python3-venv && \
    pip install --no-cache-dir --upgrade pip && \
    pip cache remove rtu-schedule-parser && \
    pip install --no-cache-dir -r requirements.txt

COPY /app/ /app/app/

ENV PORT="${PORT:-5000}"
ENV APP_MODULE="app.main:app"