from fastapi import Body, FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from starlette import status

app = FastAPI()

class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date

class BookRequest(BaseModel):
    id: Optional[int] = Field(description='field is fulfill automatically', default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=3)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: Optional[int] = Field(description="release year", default=None)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "a new book title",
                "author": "a new book author",
                "description": "a new book description",
                "rating": 5
            }
        }
    }
    
BOOKS=[
    Book(1, "To Kill a Mockingbird", "Harper Lee", "A novel set in the American South during the 1930s, focusing on the Finch family and the moral challenges they face.",5, None),
    Book(2, "1984", "George Orwell", "A dystopian novel exploring themes of totalitarianism, surveillance, and individual freedom.", 5, None),
    Book(3, "The Great Gatsby", "F. Scott Fitzgerald", "A story about the mysterious millionaire Jay Gatsby and his obsession with Daisy Buchanan during the Roaring Twenties.", 4, None),
    Book(4, "Moby-Dick", "Herman Melville", "A tale of obsession and revenge as Captain Ahab pursues the elusive white whale, Moby-Dick.", 4,None),
    Book(5, "Pride and Prejudice", "Jane Austen", "A romantic novel that deals with issues of class, marriage, and social expectations in 19th-century England.", 3, None),
    Book(6, "The Catcher in the Rye", "J.D. Salinger", "The story of Holden Caulfield, a teenager dealing with themes of alienation, rebellion, and identity.", 4, None),
    Book(7, "The Hobbit", "J.R.R. Tolkien", "A fantasy novel that follows Bilbo Baggins on an adventure to help a group of dwarves reclaim their treasure from a dragon.", 5, None),
    Book(8, "Brave New World", "Aldous Huxley", "A dystopian novel set in a future world where technology controls every aspect of life, and individualism is discouraged.", 4, None),
    Book(9, "War and Peace", "Leo Tolstoy", "An epic novel that explores Russian society during the Napoleonic Wars, with a focus on love, fate, and family.", 5, None),
    Book(10, "The Brothers Karamazov", "Fyodor Dostoevsky", "A philosophical and psychological novel that delves into themes of faith, doubt, and morality.", 5, None)
]

@app.get("/")
async def read_all_books():
    return BOOKS

@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS

@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def find_book_id(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")
        
@app.get("/books/{published_date}", status_code=status.HTTP_200_OK)
async def find_book_by_published_date(published_date: int):
    books_to_return = []
    for i in range(len(BOOKS)):
        if BOOKS[i].published_date == published_date:
            books_to_return.append(BOOKS[i])
    return books_to_return
        
@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = book
            book_changed=True
            break
        if not book_changed:
            raise HTTPException(status_code=404, detail="Book not found")
        
@app.get("/books/", status_code=status.HTTP_200_OK)
async def find_book_by_rating(book_rating: int = Query(gt=0, lt=6)):
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return

@app.post("/create_book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_id_book(new_book))

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book_by_id(book_id: int = Path(gt=0)):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            break

    
async def find_id_book(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book
  
