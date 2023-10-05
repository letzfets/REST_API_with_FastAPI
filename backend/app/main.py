from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    """This is the root path of the API"""
    return {"message": "Hello World"}