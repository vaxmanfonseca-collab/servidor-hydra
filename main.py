from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()
clients = []
quadrado_amarelo = False

@app.get("/")
async def get():
    return {"status": "Servidor Hydra Online"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global quadrado_amarelo  # Movido para o topo da função
    await websocket.accept()
    clients.append(websocket)
    try:
        # Envia o estado atual assim que conecta
        await websocket.send_text("ON" if quadrado_amarelo else "OFF")
        while True:
            data = await websocket.receive_text()
            if data == "CLICK":
                quadrado_amarelo = not quadrado_amarelo
                estado = "ON" if quadrado_amarelo else "OFF"
                # Avisa todos os clientes conectados
                for client in clients:
                    try:
                        await client.send_text(estado)
                    except:
                        continue
    except WebSocketDisconnect:
        if websocket in clients:
            clients.remove(websocket)
