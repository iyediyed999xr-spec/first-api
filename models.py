from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from database import Base
from sqlalchemy.orm import relationship

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    available = Column(Boolean, default=True)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer ,primary_key=True,index=True)
    name = Column(String,nullable=False)
    email = Column(String,unique=True,nullable=False)

class Service(Base):
    __tablename__ = "services"
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String,unique=True,nullable=False)
    price = Column(Float,nullable=False)
class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer,primary_key=True,index=True)
    customer_id = Column(Integer,ForeignKey("customers.id"))
    service_id = Column(Integer,ForeignKey("services.id"))
    booking_time = Column(String,nullable=False)
    customer = relationship("Customer")
    service = relationship("Service")