import json
import operator

import uvicorn as uvicorn
from fastapi import Request
from fastapi import FastAPI
from fastapi import HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.status import HTTP_401_UNAUTHORIZED

from backend.database import Database
from backend.models import Model
from backend.plugin import PluginController

db = Database(json.load(open("../config/config.json", "rb")))
app = FastAPI()
plugin_controller = PluginController()
model = Model(plugin_controller)
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    # React app address
    # add more origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_user(authorization: str):
    token = authorization.split(" ")[1] if authorization and " " in authorization else None
    if not token or token == "null":
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="No authorization header provided")
    # Query the user from the database using the previous token
    user = db.parallelize_and_fetch(False, "SELECT * FROM user WHERE auth_token = %s", [token])
    return user


@app.get("/session")
async def list_all_session_of_user(authorization: str = Header(None)):
    user = get_user(authorization)
    user_id = user[0]
    result = db.parallelize_and_fetch(True, "SELECT * FROM session WHERE user_id = %s", [user_id])
    if result is None:
        return {"list": []}
    return {"list": result}


@app.get("/models")
async def list_all_available_models():
    with open("../config/config.json", "rb") as fb:
        config = json.load(fb)
        combined = config["required_models"] + config["addition_models"]
        return {"models": combined}


@app.get("/singleMessage")
async def get_single_message(request: Request, authorization: str = Header(None)):
    user = get_user(authorization)

    data = await request.json()
    if 'message_id' not in data:
        raise HTTPException(status_code=400, detail="No message_id field in the request body")
    msg_id = data["message_id"]
    msg = db.parallelize_and_fetch(False, "SELECT * FROM message WHERE id= %s", [msg_id])
    if msg is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid id")
    if not msg[1] == user[0]:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="User isn't allowed to watch this message")
    return {
        "role": user[0],
        "content": msg[4],
        "isDone": msg[5] == 1
    }


@app.get("/history/{session_id}")
async def get_all_messages_in_session(session_id, authorization: str = Header(None)):
    user = get_user(authorization)
    session = db.parallelize_and_fetch(False, "SELECT * FROM session WHERE id = %s AND user_id = %s",
                                       [session_id, user[0]])

    if not session:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="User not associated with this session")

    # Query all messages from the message table where session_id matches the provided session id
    username = user[1]
    messages = db.parallelize_and_fetch(True, "SELECT * FROM message WHERE session_id = %s", [session_id])
    formated_messages = []
    messages.sort(key=lambda test_list: test_list[3])
    for m in messages:
        formated_messages.append({
            "role": "assistant" if int(m[0]) == 1 else username,
            "content": m[4],
            "done": m[5]
        })
    return {"messages": messages}


async def submit(messages):
    # query the model

    db.parallelize_and_ignore()


@app.post("/message")
async def send_message(request: Request, authorization: str = Header(None)):
    # Get the request body as JSON
    data = await request.json()
    if 'message' not in data:
        raise HTTPException(status_code=400, detail="No message field in the request body")
    elif "session" not in data:
        raise HTTPException(status_code=400, detail="No session field in the request body")

    # Get the message from the JSON data
    message = data["message"]
    session = data["session"]
    old_messages = await get_all_messages_in_session(session_id=session, authorization=authorization)

    old_messages["messages"].append({
        "role": "user",
        "content": message
    })
    user = get_user(authorization)
    # add the last message with the status "Done" to the message table
    db.parallelize_and_ignore(
        "INSERT INTO message (user_id,session_id,order_id,content,status) VALUES ( %s,%s,%s,%s,%s)",
        [user[0], session, len(old_messages), message, 1])
    # add a premtive message last message with the status "Processing" to the message table
    db.parallelize_and_fetch("")
    # get the message_id of the assistant added message
    # TODO fire and forget
    submit(old_messages, session)
    # return the message_id


@app.post("/login")
async def send_new_token(request: Request):
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


@app.post("/register")
async def register(request: Request):
    data = await request.json()
    if 'username' not in data:
        raise HTTPException(status_code=400, detail="No username field in the request body")
    elif 'password' not in data:
        raise HTTPException(status_code=400, detail="No password field in the request body")
    username = data['username']
    password = data['password']
    user = db.create_user(username, password)
    if not user:
        raise HTTPException(status_code=400, detail="Username is already taken")
    return {"api": user}


@app.patch("/token/update")
async def send_new_token(authorization: str = Header(None)):
    # Extract the token from the header
    user = get_user(authorization)
    new_token = db.update_user(user)

    # Return the new token
    return {"auth_token": new_token}


@app.patch("/updateModel/{session}")
async def update_model_for_user(request: Request, session: int, authorization: str = Header(None)):
    user = get_user(authorization)
    # TODO add the update on the DB


@app.post("/newsession")
async def create_new_session(request: Request, authorization: str = Header(None)):
    user = get_user(authorization)
    data = await request.json()
    if 'model_name' not in data:
        raise HTTPException(status_code=400, detail="No model_name field in the request body")
    elif 'session_name' not in data:
        raise HTTPException(status_code=400, detail="No session_name field in the request body")
    model_name = data['model_name']
    session_name = data['session_name']
    if len(str(session_name)) > 256:
        raise HTTPException(status_code=400, detail="Session name is too big")
    session_id = db.parallelize_and_index("INSERT INTO session  (user_id, model_name, session_name) VALUES (%s,%s,%s)",
                                          [user[0], model_name, session_name])
    return {"session_id": session_id}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
