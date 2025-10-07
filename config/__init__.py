import os
import dotenv

dotenv.load_dotenv()

class Config:
    def __init__(self):
        self.DEBUG = bool(int(os.getenv("DEBUG")))

class DatabaseConfig:
    def __init__(self):
        self.DB_PATH = os.getenv("DB_PATH")
