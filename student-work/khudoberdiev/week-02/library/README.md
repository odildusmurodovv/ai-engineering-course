# Homework 04: Library API with SQLAlchemy

## Setup and run

```sh
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
createdb library_homework
export DATABASE_URL='postgresql+psycopg://USER@localhost:5432/library_homework'
python setup_db.py          # once, on the empty database
uvicorn main:app --reload   # http://127.0.0.1:8000/docs
```

## Results

| Check | Result |
|---|---|
| `setup_db.py` | 4 tables; 3 books, 3 members, 3 loans, 10 notes |
| `GET /books/1`, `/2`, `/3` `/notes` | 200; 4, 3, 3 notes (IDs 1–4, 5–7, 8–10) |
| `GET /books/999/notes` | 404 |
| `GET /loans?open=true` | 200, loan 102 (The Hobbit, Ali) |
| `GET /loans?open=false` | 200, loans 101 and 103 |
| `GET /books/loans` | 200, 4 rows; book 3 has `loan_id: null` |
| Rollback check | 102 still `None` |
| `PATCH /loans/102/return` | 200, `returned_on: "2026-01-15"` |
| `GET /loans?open=true` after return | 200, `[]` |
| Restart, `GET /loans` | 102 keeps `2026-01-15` |
| `PATCH /loans/999/return` | 404 |

## Rollback check

```python
try:
    with Session(engine) as session:
        with session.begin():
            loan = session.get(Loan, 102)
            loan.returned_on = date(2026, 1, 15)
            session.flush()
            raise ValueError("deliberate failure before commit")
except ValueError as e:
    print("Rolled Back: ", e)

with Session(engine) as session:
    print(session.get(Loan, 102).returned_on)
```

Output: `Rolled Back:  deliberate failure before commit`, then `None`.

## How it works

- **How are tables created from the models?** `create_all()` reads every model that inherits `Base` and sends `CREATE TABLE`. `Mapped[int]` becomes `NOT NULL`, `| None` becomes nullable, and `ForeignKey` becomes `REFERENCES`.
- **How does `add_all()` insert rows?** It only queues objects. `flush()` sends the INSERTs inside the transaction, and the end of `session.begin()` commits them. Parents were flushed first so loans and notes had rows to point to.
- **Why does the left join keep book 3?** `/books/loans` starts from `Book` and uses `outerjoin`, so every book is kept. Book 3 has no loans, so its `loan_id` is `NULL`.
- **Why did the failed transaction leave the date empty?** `flush()` sent the UPDATE, but the exception left `session.begin()` before COMMIT, so it was rolled back.

## Bugs I hit

- `where(Loan.returned_on is None)` became `where(False)`. SQL needs `.is_(None)`.
- `where(BookNote.id == book_id)` filtered on the wrong column; it should be `BookNote.book_id`.
- `ForeignKey("member.id")` failed; it takes the table name, `members.id`.

## AI assistance

Claude was my tutor: it explained concepts, gave skeletons with blanks, and reviewed my code. It gave me the full `Loan` model, the `.is_()` / `.is_not()` lines, and the rollback script's blanks.
