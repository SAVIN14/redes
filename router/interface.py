import os
import json
import subprocess
from log import Log
from djkastra import dijkstra


VIZIN= json.loads(os.getenv("vizin")) 
ROTEADOR_IP = os.getenv("ip_do_roteador")
ROTEADOR_NOME = os.getenv('my_name')
PORTA_LSA = 5000

class Configuracoes:
   
    @staticmethod
    def obter_rotas(rotas):
       
        rotas_existentes = {}
        rotas_sistema = {}
        adicionar = {}
        substituir = {}
        
        try:
            novas_rotas = {}
            for destino, proximo_salto in rotas.items():
                parts = destino.split('.')
                prefixo = '.'.join(parts[:3])
                network = f"{prefixo}.0/24"
                novas_rotas[network] = proximo_salto
            
            resultado = subprocess.run(
                ["ip", "route", "show"],
                capture_output=True,
                text=True,
                check=True
            )
            
            for linha in resultado.stdout.splitlines():
                partes = linha.split()
                
                if partes[0] != "default" and partes[1] == "via":
                    rede = partes[0]  # ex: 172.20.5.0/24
                    proximo_salto = partes[2]  # ex: 172.20.4.3
                    rotas_existentes[rede] = proximo_salto
                    
                elif partes[1] == 'dev':
                    rede = partes[0]
                    proximo_salto = partes[-1]
                    rotas_sistema[rede] = proximo_salto
                
            # Replase rotas que mudaram
            for rede, proximo_salto in novas_rotas.items():
                if (rede in rotas_existentes) and (rotas_existentes[rede] != proximo_salto):
                    substituir[rede] = proximo_salto
                    
            # Adicionar rotas inexistentes
            for rede, proximo_salto in novas_rotas.items():
                if (rede not in rotas_existentes) and (rede not in rotas_sistema):
                    adicionar[rede] = proximo_salto

            return adicionar, substituir    
        except Exception as e:
            Log.log(f"Erro ao obter rotas existentes: {e}")
            return {}, {}
        
    @staticmethod
    def add_rotas(salto: str, destino: str) -> bool:
       
        try:
            p = destino.split('.')
            prefixo = '.'.join(p[:3])
            destino = f"{prefixo}.0/24"
            
            comando = f"ip route add {destino} via {salto}"
            processo = subprocess.run(
                comando.split(),
                capture_output=True
            )
            Log.log(f"[LOG] Rota adicionada com sucesso!")
        except subprocess.CalledProcessError as error:
            Log.log(f"[ERROR] Erro ao adicionar rota: {error}")
        except Exception as e:
            Log.log(f"[ERROR] Erro ao tentar adicionar rota: {error}")
    
    @staticmethod
    def subst_rotas(salto: str, destino: str) -> bool:
        
        try:
            p = destino.split('.')
            prefixo = '.'.join(p[:3])
            destino = f"{prefixo}.0/24"
            
            comando = f"ip route replace {destino} via {salto}"
            processo = subprocess.run(comando.split(), check=True)
            Log.log(f"[LOG] Rota substituída: {destino} via {salto}") if processo.returncode == 0 else Log.log(f"[LOG] Problema ao substituir rota: {processo.stderr.decode()}")
            return True
        except Exception as error:
            Log.log(f"[LOG] Error de substituicao de rotas: {error}")
        return False
    
    @staticmethod
    def configurar_inter(lsdb):
       
        rotas = dijkstra(ROTEADOR_IP, lsdb)
        
        caminhos = {}
        for destino, salto in rotas.items():
            for v, ip_custo in VIZIN.items():
                ip, _ = ip_custo
                if salto == ip:
                    caminhos[destino] = salto
                    break
                
        add, substituir = Configuracoes.obter_rotas(caminhos)
        for destino, salto in add.items():
            Configuracoes.add_rotas(salto, destino)
                
        for destino, salto in substituir.items():
            Configuracoes.subst_rotas(salto, destino)
