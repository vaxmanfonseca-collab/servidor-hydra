from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
import os

app = FastAPI()

# --- CONFIGURAÇÃO DE PERSISTÊNCIA ---
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

# --- BANNER PARA O TERMINAL (STARTUP) ---
@app.on_event("startup")
async def startup_event():
    banner = r"""
    ##############################################################
    #                                                            #
    #    ________                                                #
    #    \______ \    ____   _____   ____                        #
    #     |    |  \ /  _ \ /     \_/ __ \                        #
    #     |    `   (  <_> )  Y Y  \  ___/                        #
    #    /_______  /\____/|__|_|  /\___  >                       #
    #            \/             \/     \/   DOME OF HYDRA        #
    #                                                            #
    #       SISTEMA OPERACIONAL - SINCRONIZAÇÃO ATIVA            #
    #                                                            #
    ##############################################################
    """
    print(banner)
    print(f"--> LOG: Servidor iniciado com sucesso.")
    print(f"--> LOG: APK atual na memória: {latest_apk_link}")

# --- ROTA PRINCIPAL (VISUALIZAÇÃO NO NAVEGADOR) ---
@app.get("/", response_class=HTMLResponse)
async def get_root():
    # Este é o banner que aparecerá no seu Browser
    banner_html = r"""
    <html>
    <body style="background-color: #0d0d0d; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh;">
        <pre style="color: #00ff00; font-family: 'Courier New', Courier, monospace; font-size: 14px; font-weight: bold; line-height: 1.2; text-shadow: 0 0 5px #00ff00;">
##############################################################
#                                                            #
#    ________                                                #
#    \______ \    ____   _____   ____                        #
#     |    |  \ /  _ \ /     \_/ __ \                        #
#     |    `   (  <_> )  Y Y  \  ___/                        #
#    /_______  /\____/|__|_|  /\___  >                       #
#            \/             \/     \/   DOME OF HYDRA        #
#                                                            #
#       SISTEMA OPERACIONAL - SINCRONIZAÇÃO ATIVA            #
#                                                            #
##############################################################

STATUS: ONLINE
DISPOSITIVOS CONECTADOS: {dispositivos}
URL APK: {apk}
        </pre>
    </body>
    </html>
    """.format(dispositivos=len(clients), apk=latest_apk_link)
    return banner_html

# --- ROTAS DE DADOS ---

@app.get("/get-latest-apk")
async def get_apk():
    return {"url": load_link()}

@app.post("/update-apk-link")
async def update_link(data: UpdateLink):
    global latest_apk_link
    latest_apk_link = data.link
    save_link(data.link)
    print(f"--> LOG: Novo link recebido: {data.link}")
    return {"status": "Link atualizado e persistido"}

# --- SISTEMA WEBSOCKET (SINCRONIZAÇÃO) ---

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global quadrado_amarelo
    await websocket.accept()
    clients.append(websocket)
    
    try:
        # Envia o estado atual assim que o dispositivo conecta
        await websocket.send_text("ON" if quadrado_amarelo else "OFF")
        
        while True:
            data = await websocket.receive_text()
            if data == "CLICK":
                quadrado_amarelo = not quadrado_amarelo
                estado = "ON" if quadrado_amarelo else "OFF"
                
                # Broadcast para todos os clientes
                for client in clients[:]:
                    try:
                        await client.send_text(estado)
                    except:
                        clients.remove(client)
    except WebSocketDisconnect:
        if websocket in clients:
            clients.remove(websocket)
            