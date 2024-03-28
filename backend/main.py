import json

import uvicorn as uvicorn
from fastapi import Request
from fastapi import FastAPI
from fastapi import HTTPException, Header, Depends
from fastapi.middleware.cors import  CORSMiddleware
from starlette.status import HTTP_401_UNAUTHORIZED

from backend.database import Database

db = Database(json.load(open("../config/config.json", "rb")))
app = FastAPI()
origins = [
    "http://localhost:3000",  # React app address
    # add more origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/session/list/{user}")
async def list_all_session_of_user(user: int):
    pass


@app.get("/history/{session_id}")
async def get_all_messages_in_session(session_id, authorization: str = Header(None)):
    user = get_user(authorization)
    db.mycursor.execute("SELECT * FROM session WHERE id = %s AND user_id = %s", [session_id, user[0]])
    session = db.mycursor.fetchone()

    if not session:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="User not associated with this session")

    # Query all messages from the message table where session_id matches the provided session id
    db.mycursor.execute("SELECT * FROM message WHERE session_id = %s", [session_id])
    username = user.get("username")
    messages = db.mycursor.fetchall()
    formated_messages = []
    for m in messages:
        formated_messages.append({
            "role": "assitent" if int(m.get("user_id")) == 1 else "user",
            "content": m.get("content")
        })
    return {"messages": messages}


def submit():
    pass


@app.post("/message")
async def send_message(request: Request, authorization: str = Header(None)):
    old_messages = await get_all_messages_in_session(authorization)
    # Get the request body as JSON
    data = await request.json()

    # Check if the 'message' field is in the JSON data
    if 'message' not in data:
        raise HTTPException(status_code=400, detail="No message field in the request body")

    # Get the message from the JSON data
    message = data['message']
    old_messages["messages"].append({
        "role": "user",
        "content": message
    })

    submit()


def get_user(authorization: str):
    token = authorization.split(" ")[1] if authorization and " " in authorization else None
    if not token:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="No authorization header provided")
    # Query the user from the database using the previous token
    db.mycursor.execute("SELECT * FROM user WHERE auth_token = %s", [token])
    user = db.mycursor.fetchone()
    return user


@app.post("/login")
async def send_new_token(request: Request, authorization: str = Header(None)):
    data = await request.json()

    # Check if the 'message' field is in the JSON data
    if 'username' not in data:
        raise HTTPException(status_code=400, detail="No username field in the request body")
    elif 'password' not in data:
        raise HTTPException(status_code=400, detail="No username field in the request body")
    # Get the message from the JSON data
    username = data['username']
    password = data['password']
    return {"api": db.login(username, password)}


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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)