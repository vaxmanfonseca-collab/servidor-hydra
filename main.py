from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

app = FastAPI()

# --- CONFIGURAÇÃO DO SISTEMA DE ATUALIZAÇÃO ---
latest_apk_link = "https://esperando-primeiro-link.com"

class UpdateLink(BaseModel):
    link: str

@app.get("/")
async def get_root():
    return {"status": "Servidor Hydra Online e Operacional"}

# ROTA 1: O Celular consulta essa rota para saber onde baixar o novo APK
@app.get("/get-latest-apk")
async def get_apk():
    return {"url": latest_apk_link}

# ROTA 2: O Colab usa essa rota para enviar o link novo após o build
@app.post("/update-apk-link")
async def update_link(data: UpdateLink):
    global latest_apk_link
    latest_apk_link = data.link
    return {"status": "Link atualizado com sucesso no servidor"}

# --- CONFIGURAÇÃO DO QUADRADO AMARELO (WEBSOCKET) ---
clients = []
quadrado_amarelo = False

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global quadrado_amarelo
    await websocket.accept()
    clients.append(websocket)
    try:
        # Envia o estado atual assim que o celular ou PC conecta
        await websocket.send_text("ON" if quadrado_amarelo else "OFF")
        
        while True:
            data = await websocket.receive_text()
            if data == "CLICK":
                quadrado_amarelo = not quadrado_amarelo
                estado = "ON" if quadrado_amarelo else "OFF"
                # Avisa todos os dispositivos (Celular e Notebook)
                for client in clients:
                    try:
                        await client.send_text(estado)
                    except:
                        continue
    except WebSocketDisconnect:
        if websocket in clients:
            clients.remove(websocket)
