FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /app

WORKDIR /

EXPOSE 5000

CMD gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:5000 --timeout 300
