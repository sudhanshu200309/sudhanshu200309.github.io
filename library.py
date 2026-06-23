import json
import os
import sys
import hashlib
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FILES = {
    "users": "users.json",
    "books": "books.json",
    "issues": "issues.json",
    "reservations": "reservations.json",
    "returns": "returns.json",
    "lost_books": "lost_books.json",
    "notifications": "notifications.json"
}

FINE_PER_DAY = 2
ISSUE_PERIOD_DAYS = 14


def ensure_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    for key, file_name in FILES.items():
        path = os.path.join(DATA_DIR, file_name)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump([], f)
    users = load_data("users")
    if not any(user["role"] == "librarian" for user in users):
        create_default_librarian(users)
    if not load_data("books"):
        create_default_books()


def create_default_librarian(users):
    admin = {
        "username": "admin",
        "password_hash": hash_password("admin123"),
        "role": "librarian",
        "name": "Admin Librarian",
        "address": "Library HQ",
        "contact": "0000000000",
        "locked": False,
        "failed_attempts": 0,
        "borrow_history": [],
        "notifications": []
    }
    users.append(admin)
    save_data("users", users)
    print("Created default librarian: username=admin password=admin123")


def create_default_books():
    sample_books = [
        {"book_id": "BK1001", "title": "The Alchemist", "author": "Paulo Coelho", "genre": "Fiction", "isbn": "9780061122415", "price": 249.0, "edition": "1", "copies_available": 3, "total_copies": 3, "borrowed_count": 0, "lost_count": 0},
        {"book_id": "BK1002", "title": "Python Crash Course", "author": "Eric Matthes", "genre": "Programming", "isbn": "9781593279288", "price": 599.0, "edition": "2", "copies_available": 5, "total_copies": 5, "borrowed_count": 0, "lost_count": 0},
        {"book_id": "BK1003", "title": "Clean Code", "author": "Robert C. Martin", "genre": "Programming", "isbn": "9780132350884", "price": 799.0, "edition": "1", "copies_available": 4, "total_copies": 4, "borrowed_count": 0, "lost_count": 0},
        {"book_id": "BK1004", "title": "To Kill a Mockingbird", "author": "Harper Lee", "genre": "Fiction", "isbn": "9780061120084", "price": 349.0, "edition": "2", "copies_available": 2, "total_copies": 2, "borrowed_count": 0, "lost_count": 0},
        {"book_id": "BK1005", "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "genre": "Fiction", "isbn": "9780743273565", "price": 299.0, "edition": "1", "copies_available": 3, "total_copies": 3, "borrowed_count": 0, "lost_count": 0}
    ]
    save_data("books", sample_books)
    print("Sample book catalog added.")


def load_data(key):
    file_path = os.path.join(DATA_DIR, FILES[key])
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_data(key, data):
    file_path = os.path.join(DATA_DIR, FILES[key])
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def validate_password(password):
    return len(password) >= 6


def find_user(username):
    return next((user for user in load_data("users") if user["username"] == username), None)


def save_user(updated_user):
    users = load_data("users")
    for index, user in enumerate(users):
        if user["username"] == updated_user["username"]:
            users[index] = updated_user
            save_data("users", users)
            return
    users.append(updated_user)
    save_data("users", users)


def generate_id(items, prefix):
    if not items:
        return f"{prefix}1001"
    max_number = 0
    for item in items:
        item_id = item.get("issue_id") or item.get("reservation_id") or item.get("book_id") or item.get("username")
        if isinstance(item_id, str) and item_id.startswith(prefix):
            try:
                number = int("".join(filter(str.isdigit, item_id)))
                max_number = max(max_number, number)
            except ValueError:
                continue
    return f"{prefix}{max_number + 1}"


def input_non_empty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Value cannot be empty.")


def print_header(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def librarian_login():
    print_header("Librarian Login")
    username = input("Username: ").strip()
    user = find_user(username)
    if not user or user["role"] != "librarian":
        print("No librarian account found.")
        return None
    if user.get("locked", False):
        print("Account is locked due to too many failed attempts.")
        return None
    password = input("Password: ").strip()
    if hash_password(password) == user["password_hash"]:
        user["failed_attempts"] = 0
        save_user(user)
        print("Login successful.")
        return user
    user["failed_attempts"] = user.get("failed_attempts", 0) + 1
    if user["failed_attempts"] >= 3:
        user["locked"] = True
        print("Account locked after 3 failed attempts.")
    else:
        print(f"Incorrect password. Attempts left: {3 - user['failed_attempts']}")
    save_user(user)
    return None


def member_signup():
    print_header("Member Registration")
    username = input_non_empty("Choose username: ")
    if find_user(username):
        print("Username already exists.")
        return None
    name = input_non_empty("Full name: ")
    address = input_non_empty("Address: ")
    contact = input_non_empty("Contact number: ")
    while True:
        password = input("Choose password: ").strip()
        if not validate_password(password):
            print("Password must be at least 6 characters.")
            continue
        confirm = input("Confirm password: ").strip()
        if password != confirm:
            print("Passwords did not match.")
            continue
        break
    member = {
        "username": username,
        "password_hash": hash_password(password),
        "role": "member",
        "name": name,
        "address": address,
        "contact": contact,
        "locked": False,
        "failed_attempts": 0,
        "borrow_history": [],
        "notifications": []
    }
    save_user(member)
    print("Member registered successfully. Please login to continue.")
    return member


def member_login():
    print_header("Member Login")
    username = input("Username: ").strip()
    user = find_user(username)
    if not user or user["role"] != "member":
        print("No member account found.")
        return None
    if user.get("locked", False):
        print("Account is locked due to too many failed attempts.")
        return None
    password = input("Password: ").strip()
    if hash_password(password) == user["password_hash"]:
        user["failed_attempts"] = 0
        save_user(user)
        show_notifications(user)
        return user
    user["failed_attempts"] = user.get("failed_attempts", 0) + 1
    if user["failed_attempts"] >= 3:
        user["locked"] = True
        print("Account locked after 3 failed attempts.")
    else:
        print(f"Incorrect password. Attempts left: {3 - user['failed_attempts']}")
    save_user(user)
    return None


def show_notifications(user):
    notifications = user.get("notifications", [])
    if notifications:
        print("\nYou have notifications:")
        for note in notifications:
            print(f"- {note}")
        user["notifications"] = []
        save_user(user)


def add_book():
    print_header("Add New Book")
    books = load_data("books")
    title = input_non_empty("Title: ")
    author = input_non_empty("Author: ")
    genre = input_non_empty("Genre: ")
    isbn = input_non_empty("ISBN: ")
    while True:
        price_text = input_non_empty("Price: ")
        try:
            price = float(price_text)
            break
        except ValueError:
            print("Enter a valid numeric price.")
    edition = input_non_empty("Edition: ")
    copies = input_non_empty("Copies available: ")
    book_id = generate_id(books, "BK")
    book = {
        "book_id": book_id,
        "title": title,
        "author": author,
        "genre": genre,
        "isbn": isbn,
        "price": price,
        "edition": edition,
        "copies_available": int(copies),
        "total_copies": int(copies),
        "borrowed_count": 0,
        "lost_count": 0
    }
    books.append(book)
    save_data("books", books)
    print(f"Book added successfully with ID {book_id}.")


def find_book(book_id):
    return next((book for book in load_data("books") if book["book_id"] == book_id), None)


def update_book():
    print_header("Edit Book Details")
    books = load_data("books")
    book = select_book(books)
    if not book:
        return
    print("Leave blank to keep existing value.")
    price = input(f"Price [{book['price']}]: ").strip()
    edition = input(f"Edition [{book['edition']}]: ").strip()
    copies = input(f"Copies available [{book['copies_available']}]: ").strip()
    if price:
        book["price"] = price
    if edition:
        book["edition"] = edition
    if copies:
        difference = int(copies) - book["copies_available"]
        book["copies_available"] = int(copies)
        book["total_copies"] += difference
        if difference > 0:
            confirm_pending_reservations(book)
    save_data("books", books)
    print("Book details updated.")


def delete_book():
    print_header("Delete Book")
    books = load_data("books")
    book = select_book(books)
    if not book:
        return
    books = [b for b in books if b["book_id"] != book["book_id"]]
    save_data("books", books)
    print("Book deleted successfully.")


def select_book(books):
    if not books:
        print("No books found.")
        return None
    print("Available books:")
    for book in books:
        print(f"{book['book_id']}: {book['title']} by {book['author']} (copies {book['copies_available']})")
    book_id = input_non_empty("Enter book ID: ")
    for book in books:
        if book["book_id"] == book_id:
            return book
    print("Book ID not found.")
    return None


def search_book():
    print_header("Search Book")
    books = load_data("books")
    query = input_non_empty("Search by title, author, genre or ISBN: ").lower()
    results = [book for book in books if query in book["title"].lower() or query in book["author"].lower() or query in book["genre"].lower() or query in book["isbn"].lower()]
    display_books(results)


def genre_listing():
    print_header("Genre-wise Listing")
    books = load_data("books")
    genres = sorted({book["genre"] for book in books})
    if not genres:
        print("No books available.")
        return
    for genre in genres:
        print(f"\nGenre: {genre}")
        display_books([book for book in books if book["genre"] == genre])


def display_books(books):
    if not books:
        print("No books matched the search.")
        return
    for book in books:
        print(f"{book['book_id']} | {book['title']} | {book['author']} | {book['genre']} | ISBN {book['isbn']} | Edition {book['edition']} | Price {book['price']} | Available {book['copies_available']}")


def view_all_books(filter_available=False):
    print_header("All Books")
    books = load_data("books")
    if filter_available:
        books = [book for book in books if book["copies_available"] > 0]
    display_books(books)


def sort_by_author():
    print_header("Books by Author A-Z")
    books = load_data("books")
    books = sorted(books, key=lambda item: item["author"].lower())
    display_books(books)


def sort_by_newest_edition():
    print_header("Books by Newest Edition")
    books = load_data("books")
    try:
        books = sorted(books, key=lambda item: int(item["edition"]), reverse=True)
    except ValueError:
        books = sorted(books, key=lambda item: item["edition"], reverse=True)
    display_books(books)


def issue_book(current_user):
    print_header("Issue Book")
    books = load_data("books")
    book = select_book(books)
    if not book:
        return
    if book["copies_available"] <= 0:
        print("Book is not currently available. You may reserve it.")
        return
    issues = load_data("issues")
    issue_id = generate_id(issues, "ISS")
    issue_date = datetime.now().strftime("%Y-%m-%d")
    due_date = (datetime.now() + timedelta(days=ISSUE_PERIOD_DAYS)).strftime("%Y-%m-%d")
    issue = {
        "issue_id": issue_id,
        "book_id": book["book_id"],
        "username": current_user["username"],
        "issue_date": issue_date,
        "due_date": due_date,
        "return_date": None,
        "fine": 0,
        "status": "issued"
    }
    issues.append(issue)
    book["copies_available"] -= 1
    book["borrowed_count"] += 1
    save_data("issues", issues)
    save_books(books)
    current_user["borrow_history"].append(issue_id)
    save_user(current_user)
    print_issue_slip(issue, book, current_user)
    confirm_pending_reservations(book)


def save_books(books):
    save_data("books", books)


def print_issue_slip(issue, book, user):
    print("\nIssue Slip")
    print("-------------------------")
    print(f"Issue ID: {issue['issue_id']}")
    print(f"Member: {user['name']} ({user['username']})")
    print(f"Book: {book['title']} by {book['author']}")
    print(f"Issue Date: {issue['issue_date']}")
    print(f"Due Date: {issue['due_date']}")
    print("Please return the book on or before the due date.")


def return_book(current_user):
    print_header("Return Book")
    issues = load_data("issues")
    open_issues = [issue for issue in issues if issue["username"] == current_user["username"] and issue["status"] == "issued"]
    if not open_issues:
        print("No issued books found for this member.")
        return
    for issue in open_issues:
        book = find_book(issue["book_id"])
        print(f"{issue['issue_id']}: {book['title']} due {issue['due_date']}")
    issue_id = input_non_empty("Enter issue ID to return: ")
    issue = next((item for item in open_issues if item["issue_id"] == issue_id), None)
    if not issue:
        print("Invalid issue ID.")
        return
    books = load_data("books")
    book = next((item for item in books if item["book_id"] == issue["book_id"]), None)
    if not book:
        print("Book record not found.")
        return
    return_date = datetime.now().strftime("%Y-%m-%d")
    overdue_days = calculate_overdue_days(issue["due_date"], return_date)
    fine = max(overdue_days * FINE_PER_DAY, 0)
    issue["return_date"] = return_date
    issue["fine"] = fine
    issue["status"] = "returned"
    book["copies_available"] += 1
    returns = load_data("returns")
    returns.append({
        "issue_id": issue_id,
        "book_id": book["book_id"],
        "username": current_user["username"],
        "return_date": return_date,
        "overdue_days": overdue_days,
        "fine": fine
    })
    save_data("issues", issues)
    save_data("books", books)
    save_data("returns", returns)
    print(f"Book returned successfully. Overdue days: {overdue_days}. Fine: Rs.{fine}")
    confirm_pending_reservations(book)


def calculate_overdue_days(due_date_str, return_date_str):
    due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
    return_date = datetime.strptime(return_date_str, "%Y-%m-%d")
    return max((return_date - due_date).days, 0)


def reserve_book(current_user):
    print_header("Reserve Book")
    books = load_data("books")
    available_books = [book for book in books if book["copies_available"] == 0]
    if not available_books:
        print("No books currently out of stock for reservation.")
        return
    display_books(available_books)
    book_id = input_non_empty("Enter book ID to reserve: ")
    book = find_book(book_id)
    if not book:
        print("Book ID not found.")
        return
    reservations = load_data("reservations")
    if any(res["book_id"] == book_id and res["username"] == current_user["username"] and res["status"] in ["requested", "confirmed"] for res in reservations):
        print("You already have a reservation for this book.")
        return
    reservation_id = generate_id(reservations, "RES")
    reservation = {
        "reservation_id": reservation_id,
        "book_id": book_id,
        "username": current_user["username"],
        "request_date": datetime.now().strftime("%Y-%m-%d"),
        "status": "requested"
    }
    reservations.append(reservation)
    save_data("reservations", reservations)
    print("Reservation requested successfully. We will confirm when the book becomes available.")


def cancel_reservation(current_user):
    print_header("Cancel Reservation")
    reservations = load_data("reservations")
    user_reservations = [res for res in reservations if res["username"] == current_user["username"] and res["status"] in ["requested", "confirmed"]]
    if not user_reservations:
        print("No active reservations to cancel.")
        return
    for res in user_reservations:
        book = find_book(res["book_id"])
        print(f"{res['reservation_id']}: {book['title']} ({res['status']})")
    reservation_id = input_non_empty("Enter reservation ID to cancel: ")
    reservation = next((res for res in user_reservations if res["reservation_id"] == reservation_id), None)
    if not reservation:
        print("Reservation not found.")
        return
    reservation["status"] = "cancelled"
    save_data("reservations", reservations)
    print("Reservation cancelled.")


def confirm_pending_reservations(book):
    reservations = load_data("reservations")
    pending = [res for res in reservations if res["book_id"] == book["book_id"] and res["status"] == "requested"]
    if book["copies_available"] <= 0 or not pending:
        return
    next_reservation = pending[0]
    next_reservation["status"] = "confirmed"
    save_data("reservations", reservations)
    user = find_user(next_reservation["username"])
    if user:
        user.setdefault("notifications", []).append(f"Your reservation {next_reservation['reservation_id']} for '{book['title']}' is confirmed.")
        save_user(user)


def handle_lost_book():
    print_header("Report Lost Book")
    issues = load_data("issues")
    issued = [issue for issue in issues if issue["status"] == "issued"]
    if not issued:
        print("No currently issued books to report.")
        return
    for issue in issued:
        user = find_user(issue["username"])
        book = find_book(issue["book_id"])
        label = f"{issue['issue_id']}: {book['title']} issued to {user['username']}"
        print(label)
    issue_id = input_non_empty("Enter issue ID of the lost book: ")
    issue = next((item for item in issued if item["issue_id"] == issue_id), None)
    if not issue:
        print("Invalid issue ID.")
        return
    books = load_data("books")
    book = next((item for item in books if item["book_id"] == issue["book_id"]), None)
    issue["status"] = "lost"
    issue["return_date"] = datetime.now().strftime("%Y-%m-%d")
    issue["fine"] = float(book["price"]) if book else 0
    if book:
        book["lost_count"] += 1
    lost_books = load_data("lost_books")
    lost_books.append({
        "issue_id": issue_id,
        "book_id": issue["book_id"],
        "username": issue["username"],
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        "fine": issue["fine"]
    })
    save_data("issues", issues)
    save_data("lost_books", lost_books)
    save_data("books", books)
    print("Lost book recorded and fine applied.")


def view_profile(current_user):
    print_header("Member Profile")
    print(f"Username: {current_user['username']}")
    print(f"Name: {current_user['name']}")
    print(f"Address: {current_user['address']}")
    print(f"Contact: {current_user['contact']}")
    print(f"Borrowed history count: {len(current_user['borrow_history'])}")


def update_member_profile(current_user):
    print_header("Update Profile")
    address = input(f"Address [{current_user['address']}]: ").strip()
    contact = input(f"Contact [{current_user['contact']}]: ").strip()
    if address:
        current_user["address"] = address
    if contact:
        current_user["contact"] = contact
    save_user(current_user)
    print("Profile updated.")


def view_borrowing_history(current_user):
    print_header("Borrowing History")
    issues = load_data("issues")
    history = [issue for issue in issues if issue["username"] == current_user["username"]]
    if not history:
        print("No borrowing history found.")
        return
    for issue in history:
        book = find_book(issue["book_id"])
        status = issue["status"]
        print(f"{issue['issue_id']} | {book['title']} | Issued {issue['issue_date']} | Due {issue['due_date']} | Status {status} | Fine Rs.{issue['fine']}")


def librarian_reports():
    print_header("Reports Dashboard")
    books = load_data("books")
    users = load_data("users")
    issues = load_data("issues")
    reservations = load_data("reservations")
    returns = load_data("returns")
    lost_books = load_data("lost_books")
    total_books_issued = len([issue for issue in issues if issue["status"] in ["issued", "returned", "lost"]])
    total_members = len([user for user in users if user["role"] == "member"] )
    most_borrowed = max(books, key=lambda book: book.get("borrowed_count", 0), default=None)
    overdue_books = [issue for issue in issues if issue["status"] == "issued" and calculate_overdue_days(issue["due_date"], datetime.now().strftime("%Y-%m-%d")) > 0]
    fine_collected = sum(r.get("fine", 0) for r in returns) + sum(l.get("fine", 0) for l in lost_books)
    top_member = None
    member_activity = {}
    for issue in issues:
        if issue["username"] not in member_activity:
            member_activity[issue["username"]] = 0
        member_activity[issue["username"]] += 1
    if member_activity:
        top_username = max(member_activity, key=member_activity.get)
        top_member = find_user(top_username)
    print(f"Total books issued: {total_books_issued}")
    print(f"Total members: {total_members}")
    print(f"Most borrowed book: {most_borrowed['title'] if most_borrowed else 'N/A'}")
    print(f"Overdue books count: {len(overdue_books)}")
    print(f"Fine collected: Rs.{fine_collected}")
    print(f"Lost books reported: {len(lost_books)}")
    if top_member:
        print(f"Top active member: {top_member['name']} ({top_member['username']})")
    else:
        print("Top active member: N/A")


def list_overdue_books():
    print_header("Overdue Books")
    issues = load_data("issues")
    overdue = [issue for issue in issues if issue["status"] == "issued" and calculate_overdue_days(issue["due_date"], datetime.now().strftime("%Y-%m-%d")) > 0]
    if not overdue:
        print("No overdue books at the moment.")
        return
    for issue in overdue:
        book = find_book(issue["book_id"])
        days = calculate_overdue_days(issue["due_date"], datetime.now().strftime("%Y-%m-%d"))
        print(f"{issue['issue_id']} | {book['title']} | Borrower {issue['username']} | Due {issue['due_date']} | Overdue {days} days")


def librarian_menu(user):
    while True:
        print_header("Librarian Dashboard")
        print("1. Add New Book")
        print("2. Update Book")
        print("3. Delete Book")
        print("4. Search Book")
        print("5. Genre-wise Listing")
        print("6. View All Books")
        print("7. Issue Book")
        print("8. Return Book")
        print("9. Reservation Management")
        print("10. Report Lost Book")
        print("11. Reports Dashboard")
        print("12. View Overdue Books")
        print("13. Logout")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            add_book()
        elif choice == "2":
            update_book()
        elif choice == "3":
            delete_book()
        elif choice == "4":
            search_book()
        elif choice == "5":
            genre_listing()
        elif choice == "6":
            view_all_books()
        elif choice == "7":
            issue_book(user)
        elif choice == "8":
            return_book(user)
        elif choice == "9":
            reservation_management()
        elif choice == "10":
            handle_lost_book()
        elif choice == "11":
            librarian_reports()
        elif choice == "12":
            list_overdue_books()
        elif choice == "13":
            print("Logging out...")
            break
        else:
            print("Invalid option. Try again.")


def reservation_management():
    print_header("Reservation Management")
    reservations = load_data("reservations")
    if not reservations:
        print("No reservations found.")
        return
    for res in reservations:
        book = find_book(res["book_id"])
        print(f"{res['reservation_id']} | {book['title']} | {res['username']} | {res['status']} | Requested {res['request_date']}")
    print("Use member account to reserve or cancel reservations. This dashboard is informational.")


def member_menu(current_user):
    while True:
        print_header(f"Member Dashboard - {current_user['name']}")
        print("1. View Profile")
        print("2. Update Profile")
        print("3. View Borrowing History")
        print("4. Search All Books")
        print("5. Search by Title/Author/Genre")
        print("6. View Available Books")
        print("7. Sort Books by Author")
        print("8. Sort Books by Newest Edition")
        print("9. Issue Book")
        print("10. Return Book")
        print("11. Reserve Book")
        print("12. Cancel Reservation")
        print("13. Logout")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            view_profile(current_user)
        elif choice == "2":
            update_member_profile(current_user)
        elif choice == "3":
            view_borrowing_history(current_user)
        elif choice == "4":
            view_all_books()
        elif choice == "5":
            search_book()
        elif choice == "6":
            view_all_books(filter_available=True)
        elif choice == "7":
            sort_by_author()
        elif choice == "8":
            sort_by_newest_edition()
        elif choice == "9":
            issue_book(current_user)
        elif choice == "10":
            return_book(current_user)
        elif choice == "11":
            reserve_book(current_user)
        elif choice == "12":
            cancel_reservation(current_user)
        elif choice == "13":
            print("Logging out...")
            break
        else:
            print("Invalid option. Try again.")


def main_menu():
    ensure_data_files()
    print_header("Library Management System")
    while True:
        print("1. Librarian Login")
        print("2. Member Registration")
        print("3. Member Login")
        print("4. Exit")
        choice = input("Select an option: ").strip()
        if choice == "1":
            user = librarian_login()
            if user:
                librarian_menu(user)
        elif choice == "2":
            member_signup()
        elif choice == "3":
            user = member_login()
            if user:
                member_menu(user)
        elif choice == "4":
            print("Exiting. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please choose a valid menu item.")


if __name__ == "__main__":
    main_menu()
