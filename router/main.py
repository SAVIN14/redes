import threading
import json
import os
import socket
from log import Log
import time
from interface import Configuracoes

VIZIN= json.loads(os.getenv("vizin")) 
ROTEADOR_IP = os.getenv("ip_do_roteador")
ROTEADOR_NOME = os.getenv('my_name')
PORTA_LSA = 5000

class Roteador:
   
    def __init__(self) -> None:
        self.lsdb = {}
        self.thread = threading.Lock()
        
        Log.log(f"Iniciando o roteador!")
        
    def enviar_pacotes(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sequencia = 0
        
        while True:
            sequencia += 1
            pacote = {
            "id": ROTEADOR_IP,
            "vizin": VIZIN,
            "seq": sequencia
        }
        
            msg = json.dumps(pacote).encode()
            for v, ip_custo in VIZIN.items():
                ip, custo = ip_custo
            
                sock.sendto(msg, (ip, PORTA_LSA))
                Log.log(f"[{ip}] A mensagem foi enviado com sucesso!")
                
            with self.thread:
                self.lsdb[ROTEADOR_IP] = pacote
                self.salvar_lsdb(self.lsdb)
                Configuracoes.configurar_inter(self.lsdb)
                
            time.sleep(10)
            
    def receber_pacotes(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            sock.bind(("0.0.0.0", PORTA_LSA))
        except socket.error as bind_error:
            return

        while True:
            try:
                dado, end = sock.recvfrom(4096)
                Log.log(f"Pacote recebido de {end}")
                lsa = json.loads(dado.decode())
                origem = lsa["id"]
                
                if origem not in self.lsdb or lsa["seq"] > self.lsdb[origem]["seq"]:
                    for v, ip_custo in VIZIN.items():
                        ip, _ = ip_custo
                        if ip != end[0]:
                            sock.sendto(dado, (ip, PORTA_LSA))
                
                    with self.thread:
                        self.lsdb[origem] = lsa
                        self.salvar_lsdb(self.lsdb)
                        Configuracoes.configurar_inter(self.lsdb)
                
                Log.log(f"Recebendo pacote dessa origem: {origem}")
            except socket.error as error:
                Log.log(f"Erro ao receber LSA: {error}")
            except json.JSONDecodeError:
                Log.log("Erro ao decodificar LSA recebido.")
            except Exception as error:
                Log.log(f"Erro inesperado ao receber LSA: {error}")
          
    def salvar_lsdb(self, lsdb) -> None:
        try:
            with open(f"lsdb/{ROTEADOR_NOME}_lsdb.json", "w") as file:
                json.dump(lsdb, file, indent=4)
        except Exception as error:
            Log.log(f"[{error}] Erro ao salvar o LSDB")
               

if __name__ == "__main__":
    os.makedirs(ROTEADOR_NOME, exist_ok = True)
    router = Roteador()
    threads = [
        threading.Thread(target=router.enviar_pacotes, daemon=True),
        threading.Thread(target=router.receber_pacotes, daemon=True)
    ]
    
    for thread in threads:
        thread.start()
    threading.Event().wait()