import sys
import os
import subprocess

def get_router_containers():
    
    output = subprocess.check_output(
        ['docker', 'ps', '--filter', 'name=router', '--format', '{{.Names}}'],
        text=True
    )
    return sorted(output.strip().splitlines())



def extract_router_number(container_name):
    pre = container_name.split('-')[1]
    result = pre.split('router')[1]
    return result

def get_routing_table(container):
    cmd = f"docker exec {container} ip route"
    print(f"{cmd}")
    result = os.popen(cmd).read()
    return result.strip()
def main():
   
    routers = get_router_containers()
    
    if not routers:
        print(f"Erro: Nenhum roteador está rodando. Execute 'make up' primeiro.")
        sys.exit(1)
    
    print(f"Encontrados {len(routers)} roteadores. Mostrando tabelas de roteamento...", end='\n\n')
    
    for router in sorted(routers, key=lambda x: extract_router_number(x)):
        router_num = extract_router_number(router)
        print(f"Tabela de Roteamento do Router {router_num}")
        
        routing_table = get_routing_table(router)
        
        if routing_table:
            lines = routing_table.split('\n')
            print(f"{lines[0]}")
            for line in lines[1:]:
                print(line)
        else:
            print(f"Nenhuma rota encontrada.")
        
        print(f"========================================", end='\n\n')

if __name__ == "__main__":
    main()