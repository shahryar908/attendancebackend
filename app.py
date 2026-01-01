from fastapi import FastAPI
from model import signuprequest
app=FastAPI()


@app.post("/")
async def root():
    return {"message":"this is me"}

@app.post("/signup")
async def signup(req:signuprequest):
    return {"message":"signup successful"}
    



