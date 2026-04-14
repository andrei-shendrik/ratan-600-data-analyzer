from pydantic import BaseModel, Field


class DatabaseSettings(BaseModel):
    host: str = Field(alias="DB_HOST")
    port: int = Field(alias="DB_PORT")
    user: str = Field(alias="DB_USER")
    password: str = Field(alias="DB_PASSWORD")
    name: str = Field(alias="DB_NAME")

    @property
    def db_url(self) -> str:
        """строка подключения для SQLAlchemy"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"