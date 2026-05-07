from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import requests
import uvicorn

app = FastAPI()

# --- ARTE ASCII: DOME OF HYDRA ---
BANNER = """
 ██████   ██████  ███    ███ ███████      ██████  ███████ 
 ██   ██ ██    ██ ████  ████ ██          ██    ██ ██      
 ██   ██ ██    ██ ██ ████ ██ █████       ██    ██ █████   
 ██   ██ ██    ██ ██  ██  ██ ██          ██    ██ ██      
 ██████   ██████  ██      ██ ███████      ██████  ██      
                                                          
                                                          
 ██   ██ ██    ██ ██████  ██████   █████                  
 ██   ██  ██  ██  ██   ██ ██   ██ ██   ██                 
 ███████   ████   ██   ██ ██████  ███████                 
 ██   ██    ██    ██   ██ ██   ██ ██   ██                 
 ██   ██    ██    ██████  ██   ██ ██   ██                 
                                                          
  ---|||  SYSTEM OPERATIONAL: HYDRA'S DOME  |||---
"""

# --- CONFIGURAÇÃO DO BANCO DE DATOS (GITHUB) ---
# Substitua pelo seu link RAW do database.json
GITHUB_RAW_URL = "https://raw.githubusercontent.com/SEU_USUARIO/SEU_REPOSITORIO/main/database.json"

@app.get("/")
async def get_root():
    return {
        "msg": "DOME OF HYDRA IS ONLINE",
        "status": "SECURE",
        "power": "100%",
        "system_v": "3.0"
    }

# ROTA DE DOWNLOAD (O SEU PROCV)
@app.get("/get-latest-apk")
async def get_apk():
    try:
        response = requests.get(GITHUB_RAW_URL)
        response.raise_for_status()
        data = response.json()
        
        # Pega o último item da lista 'updates'
        ultima_versao = data["updates"][-1]
        
        return {"url": ultima_versao["url"], "v": ultima_versao["versao"]}
    except Exception as e:
        return {"error": f"Falha ao acessar o Domo: {str(e)}"}

# --- NÚCLEO WEBSOCKET (QUADRADO AMARELO) ---
clients = []
quadrado_amarelo = False

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global quadrado_amarelo
    await websocket.accept()
    clients.append(websocket)
    try:
        # Envia o estado atual na conexão
        await websocket.send_text("ON" if quadrado_amarelo else "OFF")
        
        while True:
            data = await websocket.receive_text()
            if data == "CLICK":
                quadrado_amarelo = not quadrado_amarelo
                estado = "ON" if quadrado_amarelo else "OFF"
                
                # Sincroniza todos os dispositivos conectados
                for client in clients:
                    try:
                        await client.send_text(estado)
                    except:
                        continue
    except WebSocketDisconnect:
        if websocket in clients:
            clients.remove(websocket)

# LOG NO TERMINAL DO RENDER
if __name__ == "__main__":
    print(BANNER)
    uvicorn.run(app, host="0.0.0.0", port=10000)

print(BANNER) # Garante que apareça nos logs do Render

            ### MAIN GITHUB !!! SERVIDOR GITHUB-RENDER