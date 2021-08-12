import config
from fastapi import FastAPI


app = FastAPI(title="Schedule API")


from app import views