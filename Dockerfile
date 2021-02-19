FROM tiangolo/meinheld-gunicorn-flask:python3.7

WORKDIR /app
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /app

EXPOSE 5000

ENTRYPOINT ["python"]
CMD ["waitress_run.py"]
