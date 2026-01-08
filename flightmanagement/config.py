import os

class Settings:
    db_url: str = os.getenv("DB_URL", "sqlite:///data/FlightManagement.db")

settings = Settings()