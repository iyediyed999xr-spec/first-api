from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from database import SessionLocal, get_db
from models import Book as BookModel, User
from sqlalchemy.orm import Session
import bcrypt
from jose import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
import stripe
from dotenv import load_dotenv
import os

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

SECRET_KEY = "my-super-secret-key-change-this-later"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(username: str):
    expire = datetime.utcnow() + timedelta(hours=1)
    data = {"sub": username, "exp": expire}
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

app = FastAPI()
class Book(BaseModel):
    title : str
    author : str
    price : float
    available : bool

class UserRegister(BaseModel):
    username: str
    password: str

@app.get("/books")
def get_books(available_only: bool = False, db: Session = Depends(get_db)):
    books = db.query(BookModel).all()
    if  available_only:
        books = db.query(BookModel).filter(BookModel.available == True).all()
    else:
        books = db.query(BookModel).all()
    return books
@app.post("/books") 
def receive(book: Book, db: Session = Depends(get_db)):
    new_book = BookModel(title=book.title, author=book.author, price=book.price, available=book.available)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book
@app.get("/books/{book_id}")
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if book is None: 
        raise HTTPException(status_code=404, detail="Book not found")
    return book 
@app.put("/books/{book_id}")
def update_book(book_id: int, updated_book: Book, db: Session = Depends(get_db)):
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    book.title = updated_book.title
    book.author = updated_book.author
    book.price = updated_book.price
    book.available = updated_book.available
    
    db.commit()
    db.refresh(book)
    return book
@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db.delete(book)
    db.commit()
    return {"message": f"Book {book_id} deleted"}
@app.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):    
    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())
    new_user = User(username=user.username, hashed_password=hashed.decode())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": f"User {new_user.username} registered successfully"}
@app.post("/login")
def login(user: UserRegister, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    
    if db_user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    if not bcrypt.checkpw(user.password.encode(), db_user.hashed_password.encode()):        
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token(db_user.username)
    return {"access_token": token, "token_type": "bearer"}
@app.post("/checkout/{book_id}")
def create_checkout(book_id: int, db: Session = Depends(get_db)):
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": book.title},
                "unit_amount": int(book.price * 100),
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url="http://localhost:8000/success",
        cancel_url="http://localhost:8000/cancel",
    )
    return {"checkout_url": session.url}