from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_books():
    response = client.get("/books")
    assert response.status_code == 200
def test_create_book():
    response = client.post("/books", json={
        "title": "Test",
        "author": "Test Author",
        "price": 10,
        "available": True
    })
    assert response.status_code == 200