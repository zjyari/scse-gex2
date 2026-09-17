# admin.py
import json
import os


## This function should load the library data from a JSON file and return it as a suitable Python data structure.
def load_library(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


## This function should save the library data to a JSON file.
## This function does not need to return anything, but it should ensure that the data is saved correctly to the specified file.
def save_library(data, filename):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


## This function should find a book by its title, author, or ID.
## If the book is found, it should return the book ID.
## If the book is not found, it should return None.
def find_book(books, search_text):
    if search_text is None:
        return None

    search = str(search_text).strip().lower()
    if search == "":
        return None

    # Exact ID match
    for book_id, book in books.items():
        if book_id.lower() == search:
            return book_id

    # Exact title or author match
    for book_id, book in books.items():
        title = str(book.get("title", "")).strip().lower()
        author = str(book.get("author", "")).strip().lower()
        if title == search or author == search:
            return book_id

    # Partial title or author match
    for book_id, book in books.items():
        title = str(book.get("title", "")).lower()
        author = str(book.get("author", "")).lower()
        if search in title or search in author:
            return book_id

    return None


## This function should display the list of books in a user-friendly format.
## It should show the book ID, title, category, and availability status (available or on loan).
## If the book is available, it should display "AVAILABLE", and if it is on loan, it should display "ON LOAN".
## The function should not return anything, but it should print the information to the console.
## The heading for this display should be "BOOK CATALOGUE".
def display_books(books):
    print("BOOK CATALOGUE")
    print("-" * 60)

    for book_id, book in books.items():
        status = "AVAILABLE" if book.get("available", False) else "ON LOAN"
        print(
            f"{book_id} | {book.get('title', '')} | "
            f"{book.get('category', '')} | {status}"
        )


## This function should display the list of current loans in a user-friendly format.
## It should show the book ID, title, and the name of the borrower.
## The heading for this display should be "CURRENT LOANS".
## The function should not return anything, but it should print the information to the console.
def display_loans(loans, books):
    print("CURRENT LOANS")
    print("-" * 60)

    for loan in loans:
        book_id = loan.get("book_id", "")
        book = books.get(book_id, {})
        title = book.get("title", "Unknown")
        borrower = loan.get("borrower", "")
        print(f"{book_id} | {title} | Borrower: {borrower}")


## This function should calculate and return the library statistics
## The statsitics should include the total number of books, the number of available books, and the number of borrowed books.
## The function should return these three values in the order: total, available, borrowed. Use a suitable data structure to return these values, such as a tuple or a dictionary.
def library_statistics(books):
    total = len(books)
    available = sum(1 for book in books.values() if book.get("available", False))
    borrowed = total - available
    return (total, available, borrowed)


## This function should display the library statistics in a user-friendly format.
## It should first load the library data from a JSON file, 
## Then calculate the statistics, and finally print the information to the console.
## The heading for this display should be "LIBRARY STATISTICS".
## It should print the total number of books, the number of available books, and the number of borrowed books.
## The function should not return anything, but it should print the information to the console.
def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(base_dir, "library.json")

    data = load_library(filename)
    library = data.get("library", {})

    print("LIBRARY ADMINISTRATION")
    print("=" * 60)
    print(f"Library: {library.get('name', '')}")
    print(f"Branch: {library.get('branch', '')}")
    print(f"Year: {library.get('year', '')}")
    print(f"Categories: {', '.join(data.get('categories', []))}")
    print()

    display_books(data.get("books", {}))
    print()

    display_loans(data.get("loans", []), data.get("books", {}))
    print()

    stats = library_statistics(data.get("books", {}))
    print("LIBRARY STATISTICS")
    print("-" * 60)
    print(f"Total books: {stats[0]}")
    print(f"Available: {stats[1]}")
    print(f"Borrowed: {stats[2]}")


if __name__ == "__main__":
    main()