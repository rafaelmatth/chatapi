import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chat.db")
JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey")
JWT_ALGORITHM = "HS256"
