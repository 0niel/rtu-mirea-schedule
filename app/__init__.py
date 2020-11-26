from flask import Flask

app = Flask(__name__)
app.config.update(
    SECRET_KEY=b"BUeDp@{@y'0C.Wc3z+Q~",
    DEBUG = False
)

from app import views

