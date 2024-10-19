from sqlmodel import create_engine, SQLModel

sqlite_file_name = "queue.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

from api.conifg import conf_settings

engine = create_engine(
    f"postgresql://{conf_settings.PG_USER}:"
    f"{conf_settings.PG_PASS}@"
    f"{conf_settings.PG_HOST}:"
    f"{conf_settings.PG_PORT}/"
    f"{conf_settings.PG_NAME}",
    echo=True
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

