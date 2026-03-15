from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# We use SQLite for local development
SQLALCHEMY_DATABASE_URL = "sqlite:///./water_management.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    # Test the connection
    try:
        engine.connect()
        print("Database connection successful!")
    except Exception as e:
        print(f"Connection failed: {e}")