from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

class BookCreate(BaseModel):
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    status: str = "want to read"
    rating: Optional[int] = Field(default=None, ge=1, le=5)


class BookUpdate(BaseModel):
    status: Optional[str] = None
    rating: Optional[int] = Field(default=None, ge=1, le=5)


books_db: list[dict] = []
next_id = 1

app = FastAPI(title="Book Tracker API", version="1.0.0")


def _find_book(book_id: int) -> dict | None:
    return next((b for b in books_db if b["id"] == book_id), None)


@app.get("/")
def read_root():
    return {"message": "Welcome to Book Tracker API"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/books")
def get_books(status: Optional[str] = None):
    if status:
        return [b for b in books_db if b["status"] == status]
    return books_db

@app.get("/books/stats")
def get_stats():
    total = len(books_db)
    count_by_status: dict[str, int] = {}
    for book in books_db:
        status = book["status"]
        count_by_status[status] = count_by_status.get(status, 0) + 1

    read_books = [b for b in books_db if b["status"] == "read"]
    ratings = [b["rating"] for b in read_books if b.get("rating") is not None]
    average_rating = sum(ratings) / len(ratings) if ratings else 0

    return {
        "total": total,
        "count_by_status": count_by_status,
        "average_rating": average_rating,
    }


@app.get("/books/{book_id}")
def get_book(book_id: int):
    book = _find_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.post("/books", status_code=201)
def create_book(book: BookCreate):
    global next_id
    new_book = {"id": next_id, **book.model_dump()}
    books_db.append(new_book)
    next_id += 1
    return new_book


@app.put("/books/{book_id}")
def update_book(book_id: int, updates: BookUpdate):
    book = _find_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    for field, value in updates.model_dump(exclude_unset=True).items():
        if value is not None:
            book[field] = value
    return book


@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    book = _find_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    books_db.remove(book)
    return {"message": "Book deleted", "id": book_id}
