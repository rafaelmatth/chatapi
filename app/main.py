from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.routes import users, messages
from app.auth import get_current_user_ws  # função para validar token JWT no WS

app = FastAPI()

# Configuração CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # todos os front-ends permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas REST
app.include_router(users.router)
app.include_router(messages.router)

# Lista de conexões ativas de WebSocket
connections: list[WebSocket] = []

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    # Aceita a conexão
    await websocket.accept()
    try:
        # Valida o usuário pelo token
        user = await get_current_user_ws(token)
        connections.append(websocket)
        while True:
            data = await websocket.receive_text()
            # Envia para todos conectados
            for conn in connections:
                await conn.send_text(f"{user.username}: {data}")
    except WebSocketDisconnect:
        connections.remove(websocket)
