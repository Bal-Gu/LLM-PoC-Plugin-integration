import json

from fastapi import FastAPI
from fastapi import HTTPException, Header, Depends
from starlette.status import HTTP_401_UNAUTHORIZED

from backend.database import Database

db = Database(json.load(open("../config/config.json","rb")))
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/session/list/{user}")
async def list_all_session_of_user(user:int):
    pass

@app.post("/message/{str}")
async def send_message(authorization: str = Header(None)):
    db.get_all_message_from_user()


def get_user(authorization:str):
    token = authorization.split(" ")[1] if authorization and " " in authorization else None
    if not token:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="No authorization header provided")
    # Query the user from the database using the previous token
    db.mycursor.execute("SELECT * FROM user WHERE auth_token = %s", [token])
    user = db.mycursor.fetchone()
    return user

@app.post("/token/update")
async def send_new_token(authorization: str = Header(None)):
    # Extract the token from the header
    user = get_user(authorization)
    if not user:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token")
    new_token = db.update_user(user)

    # Return the new token
    return {"auth_token": new_token}

@app.post("/updateModel")
async def update_model_for_user():
    pass
