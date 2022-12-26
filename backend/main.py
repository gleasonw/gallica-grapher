from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional


app = FastAPI()
requestID = 0

@app.get("/")
def index():
    return {"message": "Hello World"}


class Ticket(BaseModel):
    terms: List[str] | str

@app.post("/api/init")
def init(ticket: Ticket):
    global requestID
    requestID += 1
    print(ticket)
    return {"taskid": requestID, "requestid": requestID}

