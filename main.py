from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import json
import os

app = FastAPI()

# --- CONFIGURAÇÃO DE PERSISTÊNCIA (PARA O RENDER NÃO ESQUECER) ---
DB_FILE = "database.json"

def save_link(link: str):
    with open(DB_FILE, "w") as f:
        json.dump({"latest_apk_link": link}, f)

def load_link():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f).get("latest_apk_link", "https://esperando-primeiro-link.com")
        except:
            return "https://esperando-primeiro-link.com"
    return "https://esperando-primeiro-link.com"

# --- ESTADO INICIAL ---
latest_apk_link = load_link()
clients = []
quadrado_amarelo = False

class UpdateLink(BaseModel):
    link: str

# --- BANNER DE INICIALIZAÇÃO ---
@app.on_event("startup")
async def startup_event():
    banner = r"""
    ##############################################################
    #                                                            #
    #   ________                                                 #
    #   \______ \   ____   _____   ____                         #
    #    |    |  \ /  _ \ /     \_/ __ \                        #
    #    |    `   (  <_> )  Y Y  \  ___/                        #
    #   /_______  /\____/|__|_|  /\___  >                      #
    #           \/             \/     \/   DOME OF HYDRA        #
    #                                                            #
    #       SISTEMA OPERACIONAL - SINCRONIZAÇÃO ATIVA            #
    #                                                            #
    ##############################################################
    """
    print(banner)
    print(f"--> LOG: Servidor iniciado com sucesso.")
    print(f"--> LOG: APK atual na memória: {latest_apk_link}")

# --- ROTAS API ---

@app.get("/")
async def get_root():
    return {
        "status": "DOME OF HYDRA: Online",
        "dispositivos_conectados": len(clients),
        "versao_apk": latest_apk_link
    }

@app.get("/get-latest-apk")
async def get_apk():
    # Carrega sempre do arquivo para garantir que pegou o último enviado pelo Colab
    return {"url": load_link()}

@app.post("/update-apk-link")
async def update_link(data: UpdateLink):
    global latest_apk_link
    latest_apk_link = data.link
    save_link(data.link) # Salva no arquivo database.json
    print(f"--> LOG: Novo link de APK recebido do Colab: {data.link}")
    return {"status": "Link atualizado e persistido com sucesso"}

# --- SISTEMA WEBSOCKET (QUADRADO AMARELO) ---

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global quadrado_amarelo
    await websocket.accept()
    clients.append(websocket)
    print(f"--> LOG: Novo dispositivo conectado. Total: {len(clients)}")
    
    try:
        # Envia o estado atual (ON/OFF) para o dispositivo que acabou de conectar
        await websocket.send_text("ON" if quadrado_amarelo else "OFF")
        
        while True:
            data = await websocket.receive_text()
            if data == "CLICK":
                quadrado_amarelo = not quadrado_amarelo
                estado = "ON" if quadrado_amarelo else "OFF"
                
                # Avisa todos os dispositivos conectados e limpa conexões mortas
                for client in clients[:]: 
                    try:
                        await client.send_text(estado)
                    except:
                        clients.remove(client)
    except WebSocketDisconnect:
        if websocket in clients:
            clients.remove(websocket)
        print("--> LOG: Dispositivo desconectado.")