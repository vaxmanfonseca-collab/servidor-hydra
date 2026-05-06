import customtkinter as ctk
import websocket
import threading

class AppNotebook(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x400")
        self.title("Receptor de Sinal")
        self.configure(fg_color="black")

        # O Quadrado (inicia preto/transparente)
        self.quadrado = ctk.CTkFrame(self, width=200, height=200, fg_color="transparent", border_width=2, border_color="white")
        self.quadrado.place(relx=0.5, rely=0.5, anchor="center")

        # Inicia a escuta do servidor em segundo plano
        threading.Thread(target=self.conectar_ao_servidor, daemon=True).start()

    def conectar_ao_servidor(self):
        # Substitua pela URL do seu servidor quando ele estiver online
        url = "ws://seu-servidor.render.com/ws"
        self.ws = websocket.WebSocketApp(url, on_message=self.ao_receber)
        self.ws.run_forever()

    def ao_receber(self, ws, mensagem):
        # Se a mensagem for "1", acende o amarelo. Se for "0", apaga.
        if mensagem == "1":
            self.quadrado.configure(fg_color="yellow")
        else:
            self.quadrado.configure(fg_color="transparent")

if __name__ == "__main__":
    app = AppNotebook()
    app.mainloop()
    
