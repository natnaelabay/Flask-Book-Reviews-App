import csv
import os
from dotenv import  load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


with open("books.csv") as f:
    f = csv.reader(f)
    count = 0
    print("start")
    for row in f:
        if count == 0:
            print("start")
            count = 123
        else:
            print(count)
            db.execute(
                "INSERT INTO books( isbn, title, author, year) VALUES (:isbn, :title,:author , :year);",
                {
                    "isbn": row[0].strip(),
                    "title": row[1].strip(),
                    "author": row[2].strip(),
                    "year": int(row[3].strip()),
                }
                )
        count += 1
    db.commit()
    print(count)

print("completed!!!!!!!!")
