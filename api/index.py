from fastapi import *

app = FastAPI()

@app.get("/")
async def root(): 
    return {"message": "Hello World"}