from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .api.api_v1.router import router as api_router
from .core.config import API_V1_PREFIX
from .database.database_connection import (close_mongo_connection,
                                           connect_to_mongo)


def get_application() -> FastAPI:
    application = FastAPI(title="Schedule API")

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_event_handler("startup", connect_to_mongo)
    application.add_event_handler("shutdown", close_mongo_connection)

    application.include_router(api_router, prefix=API_V1_PREFIX)

    return application


app = get_application()
