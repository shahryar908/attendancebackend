from fastapi import FastAPI

app=FastAPI()


@app.post("/")
async def root():
    return {"message":"this is me"}

@app.post("/signup")
async def signup():
    return {"mmmmm":"signup route"}