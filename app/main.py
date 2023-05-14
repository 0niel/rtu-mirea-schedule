import os

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .api.api_v1.router import router as api_router
from .core.config import API_V1_PREFIX
from .database.database_connection import (close_mongo_connection,
                                           connect_to_mongo)

app = FastAPI(
    title="Schedule API",
    debug=os.getenv("DEBUG", False),
    description="RTU MIREA Schedule API",
    openapi_url=f"{API_V1_PREFIX}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)

app.include_router(api_router, prefix=API_V1_PREFIX)
