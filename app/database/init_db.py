from app.database.database import Base, engine
from app.models.user import User
from app.models.file import File


Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")