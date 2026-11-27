from datetime import date
from sqlalchemy.orm import Session
from main import Base, engine, Book, Member, Loan, BookNote

Base.metadata.create_all(engine)

with Session(engine) as session:
    with session.begin():
        # parents first
        session.add_all([
            Book(id = 1, title = "The Hobbit"), 
            Book(id = 2, title = "A Wizard of Earthsea"), 
            Book(id = 3, title = "The Little Prince"),

            Member(id = 11, name = "Mina"), 
            Member(id = 12, name = "Ali"),
            Member(id = 13, name = "Sara")
        ])
        session.flush() # now parents exist in transation

        # children
        session.add_all([
            Loan(id = 101, book_id = 1, member_id = 11, 
                 borrowed_on = date(2026, 1, 5), returned_on=date(2026, 1, 10)), 
            Loan(id = 102, book_id = 1, member_id = 12, 
                 borrowed_on = date(2026, 1, 12), returned_on = None),
            Loan(id = 103, book_id = 2, member_id = 13, 
                 borrowed_on = date(2026, 1, 6), returned_on = date(2026, 1, 9))
        ])

        # another children
        session.add_all([
            BookNote(book_id = 1, text = "Reread the opening chapter."),
            BookNote(book_id = 1, text = "List the main characters."),
            BookNote(book_id = 1, text = "Track the journey."),
            BookNote(book_id = 1, text = "Write a short summary."),
            BookNote(book_id = 2, text = "Describe the setting."),
            BookNote(book_id = 2, text = "Review the dialogue."),
            BookNote(book_id = 2, text = "Compare the characters."),
            BookNote(book_id = 3, text = "Record a favorite scene."),
            BookNote(book_id = 3, text = "Review the ending."),
            BookNote(book_id = 3, text = "Prepare discussion questions."),
        ])