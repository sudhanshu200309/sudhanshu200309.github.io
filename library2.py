import json, os, hashlib, sys
from datetime import datetime, timedelta

BASE = "data"
FILES = ["users", "books", "issues"]
FINE = 2
DAYS = 14

os.makedirs(BASE, exist_ok=True)

# ---------- BASIC FUNCTIONS ----------
def path(name): return f"{BASE}/{name}.json"

def load(name):
    try: return json.load(open(path(name)))
    except: return []

def save(name, data):
    json.dump(data, open(path(name), "w"), indent=2)

def sha(p): return hashlib.sha256(p.encode()).hexdigest()

def gen_id(items, prefix): return f"{prefix}{1001+len(items)}"

# ---------- INITIAL SETUP ----------
def init():
    for f in FILES:
        if not os.path.exists(path(f)): save(f, [])

    users = load("users")
    if not any(u["role"] == "librarian" for u in users):
        users.append({
            "username": "admin",
            "password": sha("admin123"),
            "role": "librarian",
            "name": "Admin"
        })
        save("users", users)

    if not load("books"):
        save("books", [
            {"id":"B1","title":"Python Programming","copies":5},
            {"id":"B2","title":"Clean Code","copies":3},
            {"id":"B3","title":"The Alchemist","copies":4},
])

def login(role):
    u = input("Username: ")
    p = input("Password: ")

    for user in load("users"):
        if user["username"] == u and user["role"] == role and user["password"] == sha(p):
            print("Login successful")
            return user

    print("Login failed")
    print("Login function loaded")
    return None

def view_books():
    b = load("books")
    print("\nBooks:")
    for x in b:
        print(f"{x['id']} | {x['title']} | Available: {x['copies']}")


def member(user):
    while True:
        print("\n--- Member Menu ---")
        print("1 View Books")
        print("2 Issue Book")
        print("3 Return Book")
        print("4 Logout")

        c = input("> ")

        if c == "1":
            view_books()
        elif c == "2":
            issue(user)
        elif c == "3":
            ret(user)
        else:
            break
        
# ---------- START PROGRAM ----------
if __name__ == "__main__":
    init()   # setup files + books

    while True:
        print("\n--- Library System ---")
        print("1 Librarian Login")
        print("2 Member Signup")
        print("3 Member Login")
        print("4 Exit")

        ch = input("> ")

        if ch == "1":
            user = login("librarian")
            if user: librarian(user)

        elif ch == "2":
            signup()

        elif ch == "3":
            user = login("member")
            if user: member(user)

        elif ch == "4":
            print("Goodbye!")
            sys.exit()

        else:
            print("Invalid choice")