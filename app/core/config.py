from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TripMate Backend"
    app_env: str = "dev"
    mysql_dsn: str = "mysql+pymysql://root:root@127.0.0.1:3306/trip_mate"
    redis_url: str = "redis://127.0.0.1:6379/0"
    jwt_secret: str = "replace_me"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
