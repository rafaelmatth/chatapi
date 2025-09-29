from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from . import database, models, auth

router = APIRouter()

active_connections = []

async def connect(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)

def disconnect(websocket: WebSocket):
    active_connections.remove(websocket)

async def broadcast(message: str):
    for connection in active_connections:
        await connection.send_text(message)

@router.websocket("/ws/chat")
async def chat_endpoint(websocket: WebSocket, token: str, db: Session = Depends(database.SessionLocal)):
    user = auth.get_current_user(token, db)
    await connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            msg = models.Message(user_id=user.id, content=data)
            db.add(msg)
            db.commit()
            await broadcast(f"{user.username}: {data}")
    except WebSocketDisconnect:
        disconnect(websocket)
        await broadcast(f"{user.username} left the chat")
