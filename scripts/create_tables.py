from database import engine
from models import Base, Task


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")


if __name__ == "__main__":
    create_tables()