from fastapi import FastAPI

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int

    def __init__(self, id, title, author, description, rating):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating


BOOKS = [
    {
        "id": 1,
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "description": "A novel set in the American South during the 1930s, focusing on the Finch family and the moral challenges they face.",
        "rating": 5,
    },
    {
        "id": 2,
        "title": "1984",
        "author": "George Orwell",
        "description": "A dystopian novel exploring themes of totalitarianism, surveillance, and individual freedom.",
        "rating": 5,
    },
    {
        "id": 3,
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "description": "A story about the mysterious millionaire Jay Gatsby and his obsession with Daisy Buchanan during the Roaring Twenties.",
        "rating": 4,
    },
    {
        "id": 4,
        "title": "Moby-Dick",
        "author": "Herman Melville",
        "description": "A tale of obsession and revenge as Captain Ahab pursues the elusive white whale, Moby-Dick.",
        "rating": 4,
    },
    {
        "id": 5,
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "description": "A romantic novel that deals with issues of class, marriage, and social expectations in 19th-century England.",
        "rating": 5,
    },
    {
        "id": 6,
        "title": "The Catcher in the Rye",
        "author": "J.D. Salinger",
        "description": "The story of Holden Caulfield, a teenager dealing with themes of alienation, rebellion, and identity.",
        "rating": 4,
    },
    {
        "id": 7,
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "description": "A fantasy novel that follows Bilbo Baggins on an adventure to help a group of dwarves reclaim their treasure from a dragon.",
        "rating": 5,
    },
    {
        "id": 8,
        "title": "Brave New World",
        "author": "Aldous Huxley",
        "description": "A dystopian novel set in a future world where technology controls every aspect of life, and individualism is discouraged.",
        "rating": 4,
    },
    {
        "id": 9,
        "title": "War and Peace",
        "author": "Leo Tolstoy",
        "description": "An epic novel that explores Russian society during the Napoleonic Wars, with a focus on love, fate, and family.",
        "rating": 5,
    },
    {
        "id": 10,
        "title": "The Brothers Karamazov",
        "author": "Fyodor Dostoevsky",
        "description": "A philosophical and psychological novel that delves into themes of faith, doubt, and morality.",
        "rating": 5,
    },
]


@app.get("/")
async def read_all_books():
    return BOOKS

@app.get("/books")
async def read_all_books():
    return BOOKS

@app.post("/create_book")
async def create_book(book_request=Book):
    BOOKS.append(book_request)
    