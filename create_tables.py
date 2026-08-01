from database import Base, engine
from models import Customer, Service, Booking

Base.metadata.create_all(bind=engine)
print("Tables created successfully")