import os
from dotenv import load_dotenv
from fastapi import *
import pymysql.cursors
from starlette.responses import *

app = FastAPI()

load_dotenv(".env")

databaseConfig = pymysql.connect(
	host=os.getenv("mysqlServer"),
	user="root",
	password=os.getenv("mysqlPassword"),
	port=3306,
	database="tragedy",
	charset='utf8mb4',
	cursorclass=pymysql.cursors.DictCursor,
	read_timeout=5,
	write_timeout=5,
	connect_timeout=5,
	autocommit=True
	)

cursor = databaseConfig.cursor()


@app.get("/newsletter/add")
async def add(email: str = None): 
    if not email:
        return HTTPException(400)
    else:
        try:
            cursor.execute("INSERT INTO news (email) VALUES (%s)", (email))
            cursor.commit()
            return HTMLResponse(status_code=200)
        except:
            return HTTPException(500)

if __name__ == "__main__":
    try:
        pass
    except pymysql.err.OperationalError:
        os.system("clear")
        print("lol")