# SQLAlchemy ORM Guide

SQLAlchemy is the **Object-Relational Mapper (ORM)** used in this project to bridge the gap between Python code and the SQL database. Instead of writing raw `SELECT` or `INSERT` strings, we interact with Python classes and objects.

---

## 🏗️ 1. Database Setup (`engine.py`)

The database configuration lives in [engine.py](file:///e:/Fsociety/backend/database/engine.py). This is where the connection is established.

### Line-by-Line Explanation:
```python
# 1. create_engine: Manages the connection pool to the database.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 2. sessionmaker: A factory for creating Session objects.
# autocommit=False: We must explicitly call .commit() to save changes.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. declarative_base: The base class that all our Models will inherit from.
Base = declarative_base()

# 4. get_db(): A dependency used in FastAPI to provide a session per request.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() # Always close the connection!
```

---

## 📋 2. Defining Tables (`models.py`)

Every table is defined as a Python class in [models.py](file:///e:/Fsociety/backend/database/models.py).

### How it works:
- `__tablename__`: Defines the actual name of the table in SQL.
- `Column`: Defines a field (String, Integer, Boolean, etc.).
- `relationship`: Links tables together (e.g., a User has many ChatSessions).

---

## 🔍 3. How to Query (CRUD Operations)

We use the `db` session (usually found as `self.db` in repositories) to perform operations.

### A. SELECT (Fetching Data)
| SQL Equivalent | SQLAlchemy ORM |
| :--- | :--- |
| `SELECT * FROM users` | `db.query(User).all()` |
| `WHERE id = '...'` | `.filter(User.id == id).first()` |
| `ORDER BY date DESC` | `.order_by(desc(User.created_at))` |
| `LIMIT 10` | `.limit(10)` |

**Example (Complex Query):**
```python
# Get all active users with email ending in @gmail.com
users = db.query(User).filter(
    User.is_active == True,
    User.email.like("%@gmail.com")
).all()
```

### B. INSERT (Creating Data)
1. Create the instance.
2. Add it to the session.
3. Commit.

```python
new_user = User(username="neo", email="neo@matrix.com")
db.add(new_user)     # Stage it
db.commit()          # Save it permanently
db.refresh(new_user) # Reload object with ID from database
```

### C. UPDATE (Modifying Data)
1. Fetch the object.
2. Change its attributes.
3. Commit.

```python
user = db.query(User).filter(User.id == "123").first()
user.full_name = "Thomas Anderson"
db.commit() # Changes are detected and saved
```

### D. DELETE (Removing Data)
```python
user = db.query(User).filter(User.id == "123").first()
db.delete(user)
db.commit()
```

---

## 💾 4. Transactions: Commit vs. Rollback

Transactions ensure that either **all** changes are saved, or **none** are (Atomicity).

```python
try:
    db.add(item1)
    db.add(item2)
    db.commit() # Success!
except Exception:
    db.rollback() # Something failed, undo changes to keep DB clean
    raise
```

---

## 📂 5. Associated Files
The ORM is used across all "Repository" files. These are the files you should check for real-world query examples:

1.  [`user_repository.py`](file:///e:/Fsociety/backend/database/repositories/user_repository.py) - User management and Auth.
2.  [`chat_repository.py`](file:///e:/Fsociety/backend/database/repositories/chat_repository.py) - Chat history and context.
3.  [`scan_repository.py`](file:///e:/Fsociety/backend/database/repositories/scan_repository.py) - Malware and Network scan results.
4.  [`vpn_repository.py`](file:///e:/Fsociety/backend/database/repositories/vpn_repository.py) - VPN server configs.
5.  [`activity_repository.py`](file:///e:/Fsociety/backend/database/repositories/activity_repository.py) - System logs.
