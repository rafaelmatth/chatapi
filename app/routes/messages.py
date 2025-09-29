# app/routes/messages.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import List
from app import database, models, auth, schemas
import json

router = APIRouter()

# Conexões WebSocket ativas
active_connections: List[WebSocket] = []

# Função para enviar uma mensagem a todos
async def broadcast_message(message: dict):
    for connection in active_connections:
        await connection.send_text(json.dumps(message))

# Rota REST existente
@router.get("/messages", response_model=list[schemas.MessageResponse])
def get_messages(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.Message).order_by(models.Message.timestamp.desc()).limit(50).all()


# Novo endpoint WebSocket
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(database.get_db)):
    # Valida token
    try:
        user = auth.get_current_user(token, db)
    except:
        await websocket.close(code=1008)  # Policy violation
        return

    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            # Espera JSON com { "content": "mensagem" }
            try:
                msg_data = json.loads(data)
                content = msg_data.get("content", "").strip()
            except:
                continue

            if content:
                # Cria e salva a mensagem no banco
                new_message = models.Message(user_id=user.id, content=content)
                db.add(new_message)
                db.commit()
                db.refresh(new_message)

                # Converte para JSON
                msg_json = {
                    "id": new_message.id,
                    "user_id": new_message.user_id,
                    "content": new_message.content,
                    "timestamp": new_message.timestamp.isoformat()
                }

                # Envia para todos os clientes
                await broadcast_message(msg_json)

    except WebSocketDisconnect:
        active_connections.remove(websocket)
