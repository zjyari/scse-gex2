import copy
import importlib
import random
import subprocess
import sys


RANDOM_SEED = 73129
rng = random.Random(RANDOM_SEED)


def random_book_id():

    return f"B{rng.randint(1000, 9999)}"


def random_title():

    adjective = rng.choice([
        "Hidden",
        "Silent",
        "Ancient",
        "Digital",
        "Lost",
        "Modern",
        "Frozen",
        "Invisible"
    ])

    noun = rng.choice([
        "World",
        "Machine",
        "Forest",
        "City",
        "Ocean",
        "Journey",
        "Signal",
        "Library"
    ])

    return f"{adjective} {noun}"


def random_author():

    first = rng.choice([
        "Anna",
        "David",
        "Chen",
        "Sara",
        "Leo",
        "Maya",
        "Nina",
        "Omar"
    ])

    last = rng.choice([
        "Lee",
        "Martin",
        "Patel",
        "Smith",
        "Chen",
        "Malik",
        "Garcia",
        "Wilson"
    ])

    return f"{first} {last}"


def random_category():

    return rng.choice([
        "Science",
        "History",
        "Technology",
        "Fiction",
        "Art",
        "Travel"
    ])


def make_books(count=8):

    books = {}

    while len(books) < count:

        book_id = random_book_id()

        if book_id not in books:

            books[book_id] = {
                "title": random_title(),
                "author": random_author(),
                "category": random_category(),
                "available": rng.choice([
                    True,
                    False
                ])
            }

    return books



admin = importlib.import_module("admin")
user = importlib.import_module("user")


def test_find_existing_books():

    books = make_books(10)

    for book_id in books:

        messy_id = (
            "   "
            + book_id.lower()
            + "   "
        )

        result = admin.find_book(
            books,
            messy_id
        )

        assert result == book_id


def test_find_nonexistent_book():

    books = make_books(6)

    result = admin.find_book(
        books,
        "ZZ99999"
    )

    assert result is None


def test_category_search():

    books = make_books(15)

    target_category = rng.choice([
        book["category"]
        for book in books.values()
    ])

    expected = []

    for book_id, book in books.items():

        if (
            book["category"].lower()
            == target_category.lower()
        ):
            expected.append(book_id)

    result = user.books_in_category(
        books,
        "  " + target_category.upper() + "  "
    )

    assert set(result) == set(expected)


def test_category_not_found():

    books = make_books(8)

    result = user.books_in_category(
        books,
        "Underwater Basket Weaving"
    )

    assert result == []



def test_title_search():

    books = make_books(12)

    selected_id = rng.choice(
        list(books.keys())
    )

    title = books[selected_id]["title"]

    search_text = (
        title.split()[0]
    )

    expected = []

    for book_id, book in books.items():

        if (
            search_text.lower()
            in book["title"].lower()
        ):
            expected.append(book_id)

    result = user.search_by_title(
        books,
        search_text.upper()
    )

    assert set(result) == set(expected)


def test_title_search_is_case_insensitive():

    books = {
        "X918": {
            "title": "Mysteries of Europa",
            "author": "Test Author",
            "category": "Science",
            "available": True
        }
    }

    result = user.search_by_title(
        books,
        "eUrOpA"
    )

    assert result == ["X918"]


def test_borrow_available_book():

    books = make_books(8)

    book_id = rng.choice(
        list(books.keys())
    )

    books[book_id]["available"] = True

    loans = []

    borrower = random_author()

    result = user.borrow_book(
        books,
        loans,
        " " + book_id.lower() + " ",
        borrower
    )

    assert result == "OK"

    assert (
        books[book_id]["available"]
        is False
    )

    assert len(loans) == 1

    assert loans[0]["book_id"] == book_id

    assert (
        loans[0]["borrower"]
        == borrower
    )


# ============================================================
# USER: BORROW UNAVAILABLE BOOK
# ============================================================

def test_cannot_borrow_unavailable_book():

    books = make_books(5)

    book_id = rng.choice(
        list(books.keys())
    )

    books[book_id]["available"] = False

    loans = [
        {
            "book_id": book_id,
            "borrower": "Existing Borrower"
        }
    ]

    before_books = copy.deepcopy(books)
    before_loans = copy.deepcopy(loans)

    result = user.borrow_book(
        books,
        loans,
        book_id,
        "New Borrower"
    )

    assert result == "NOT_AVAILABLE"

    assert books == before_books
    assert loans == before_loans



def test_borrow_unknown_book():

    books = make_books(7)

    loans = []

    before_books = copy.deepcopy(books)

    result = user.borrow_book(
        books,
        loans,
        "NOT-A-REAL-ID",
        "Alice"
    )

    assert result == "BOOK_NOT_FOUND"

    assert books == before_books
    assert loans == []



def test_empty_borrower():

    books = make_books(6)

    book_id = rng.choice(
        list(books.keys())
    )

    books[book_id]["available"] = True

    loans = []

    before_books = copy.deepcopy(books)

    result = user.borrow_book(
        books,
        loans,
        book_id,
        "     "
    )

    assert result == "EMPTY_NAME"

    assert books == before_books
    assert loans == []



def test_return_book():

    books = make_books(6)

    book_id = rng.choice(
        list(books.keys())
    )

    books[book_id]["available"] = False

    borrower = random_author()

    loans = [
        {
            "book_id": book_id,
            "borrower": borrower
        }
    ]

    result = user.return_book(
        books,
        loans,
        book_id.lower(),
        borrower
    )

    assert result == "OK"

    assert (
        books[book_id]["available"]
        is True
    )

    assert loans == []



def test_return_book_not_on_loan():

    books = make_books(6)

    book_id = rng.choice(
        list(books.keys())
    )

    books[book_id]["available"] = True
    borrower = random_author()

    loans = []

    before = copy.deepcopy(books)

    result = user.return_book(
        books,
        loans,
        book_id, 
        borrower
    )

    assert result == "NOT_ON_LOAN"

    assert books == before
    assert loans == []



def test_library_statistics():

    books = make_books(20)

    expected_total = len(books)

    expected_available = 0

    for book in books.values():

        if book["available"]:
            expected_available += 1

    expected_borrowed = (
        expected_total
        - expected_available
    )

    result = admin.library_statistics(
        books
    )

    assert result == (
        expected_total,
        expected_available,
        expected_borrowed
    )



def test_save_and_load(tmp_path):

    books = make_books(5)

    original_data = {
        "library": {
            "name": "Random Library",
            "branch": "Test",
            "year": 2026
        },

        "categories": [
            "Science",
            "History",
            "Technology"
        ],

        "books": books,

        "loans": []
    }

    filename = (
        tmp_path
        / "temporary_library.json"
    )

    admin.save_library(
        original_data,
        filename
    )

    loaded_data = admin.load_library(
        filename
    )

    assert loaded_data == original_data

def test_importing_admin_does_not_run_main():

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import admin"
        ],
        capture_output=True,
        text=True,
        timeout=3
    )

    assert result.returncode == 0

    assert result.stdout.strip() == ""


def test_importing_user_does_not_run_main():

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import user"
        ],
        capture_output=True,
        text=True,
        timeout=3
    )

    assert result.returncode == 0

    assert result.stdout.strip() == ""

def test_admin_runs_directly():

    result = subprocess.run(
        [
            sys.executable,
            "admin.py"
        ],
        capture_output=True,
        text=True,
        timeout=5
    )

    assert result.returncode == 0

    output = result.stdout

    assert "LIBRARY ADMINISTRATION" in output
    assert "STATISTICS" in output

def test_user_runs_directly():

    result = subprocess.run(
        [
            sys.executable,
            "user.py"
        ],
        input="5\n",
        capture_output=True,
        text=True,
        timeout=5
    )

    assert result.returncode == 0

    assert (
        "LIBRARY USER SYSTEM"
        in result.stdout
    )