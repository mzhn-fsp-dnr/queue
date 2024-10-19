import api.conifg

from fastapi import FastAPI
from api.database import create_db_and_tables
from api.routers import queue, window

create_db_and_tables()

app = FastAPI()

app.include_router(queue.router)
app.include_router(window.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
