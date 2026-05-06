from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()
clients = []
quadrado_amarelo = False

@app.get("/")
async def get():
    return {"status": "Servidor Hydra Online"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        # Envia o estado atual assim que conecta
        await websocket.send_text("ON" if quadrado_amarelo else "OFF")
        while True:
            data = await websocket.receive_text()
            if data == "CLICK":
                global quadrado_amarelo
                quadrado_amarelo = not quadrado_amarelo
                estado = "ON" if quadrado_amarelo else "OFF"
                # Avisa todos os clientes conectados
                for client in clients:
                    await client.send_text(estado)
    except WebSocketDisconnect:
        clients.remove(websocket)
