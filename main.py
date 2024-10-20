from api.conifg import conf_settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.database import create_db_and_tables
from api.routers import queue, window

create_db_and_tables()


def setup() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=conf_settings.ALLOWED_ORIGINS,
        allow_credentials=conf_settings.ALLOW_CREDENTIALS,
        allow_methods=conf_settings.ALLOW_METHODS,
        allow_headers=conf_settings.ALLOW_HEADERS,
    )
    app.include_router(queue.router)
    app.include_router(window.router)
    return app


app = setup()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=conf_settings.APP_PORT)
