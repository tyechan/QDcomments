from fastapi import FastAPI
import pymysql.cursors
import uvicorn

app = FastAPI()
mysql = pymysql.connect()


@app.get("/books")
async def books():
    with mysql.cursor() as cursor:
        sql = "select * from books where status = '1'"
        cursor.execute(sql)
        books = cursor.fetchall()
    return {"books": books}


@app.get("/book/{book_id}")
async def book(book_id: str):
    with mysql.cursor() as cursor:
        sql = "select * from books where status = '1' and bookid = %s"
        cursor.execute(sql, (book_id))
        book_info = cursor.fetchone()
        sql = "select * from chapters where status = '1' and bookid = %s"
        cursor.execute(sql, (book_id))
        chapters = cursor.fetchall()
    return {"book_info": book_info, "chapters": chapters}


@app.get("/book/{book_id}/chapter/{chapter_id}")
async def chapter(book_id: str, chapter_id: str):
    with mysql.cursor() as cursor:
        sql = "select * from chapters where status = '1' and bookid = %s and chapterid = %s"
        cursor.execute(sql, (book_id, chapter_id))
        chapter_info = cursor.fetchone()
        sql = "select * from segments where status = '1' and bookid = %s and chapterid = %s"
        cursor.execute(sql, (book_id, chapter_id))
        segments = cursor.fetchall()
    return {"chapter_info": chapter_info, "segments": segments}


@app.get("/book/{book_id}/chapter/{chapter_id}/segment/{segment_id}")
async def segment(book_id: str, chapter_id: str, segment_id: int):
    with mysql.cursor() as cursor:
        sql = "select * from comments where status = '1' and bookid = %s and chapterid = %s and segmentid = %s"
        cursor.execute(sql, (book_id, chapter_id, segment_id))
        comments = cursor.fetchall()
    return {"comments": comments}


if __name__ == "__main__":
    uvicorn.run("main:app", port=80, log_level="info")
