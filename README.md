# Simulação de Roteamento por Estado de Enlace com Docker e Python

Este projeto simula uma rede de computadores com múltiplos hosts e roteadores usando Python e Docker. Cada roteador utiliza o algoritmo de roteamento por estado de enlace (Link State), permitindo comunicação eficiente entre hosts em diferentes subredes.

## Objetivo

- Simular uma rede com várias subredes, cada uma com 2 hosts e 1 roteador.
- Implementar roteamento dinâmico entre roteadores usando o algoritmo de estado de enlace.
- Permitir comunicação entre hosts de diferentes subredes.

## Tecnologias

- **Python 3**: Lógica dos roteadores e hosts.
- **Docker e Docker Compose**: Simulação dos elementos da rede.
- **Threading**: Execução paralela de tarefas.
- **UDP**: Comunicação entre roteadores.

## Estrutura do Projeto

```
prova_1_rayner/
├── router/           # Código dos roteadores
│   ├── router.py
│   ├── dycastra.py
│   ├── formater.py
│   └── Dockerfile
├── host/             # Código dos hosts
│   ├── host.py
│   └── Dockerfile
├── scripts_test/     # Scripts de teste
│   ├── router_show_tables.py
│   ├── router_connect_router.py
│   ├── user_connect_router.py
│   └── user_connect_user.py
├── docker-compose.yml
└── makefile
```

## Como Executar

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/KauaHenSilva/{Nome_Repositorio}.git
   cd {Nome_Repositorio}
   ```

2. **Inicie os containers**:
   ```bash
   docker compose up --build
   ```
   Para rodar em segundo plano:
   ```bash
   docker compose up --build -d
   ```

3. **Aguarde a inicialização da rede** (cerca de 30 segundos).

4. **Verifique as tabelas de roteamento**:
   ```bash
   python3 testes/exibir_tabela.py
   ```

5. **Teste a conectividade**:
   - Entre host:
     ```bash
     python3 testes/conexao_host.py
     ```
6. **Para parar os containers**:
   ```bash
   docker compose down
   ```

## Funcionamento do Algoritmo de Estado de Enlace

- Cada roteador mantém uma base de dados com informações dos enlaces da rede.
- Os roteadores trocam mensagens periodicamente para atualizar o estado dos enlaces.
- O algoritmo de Dijkstra é usado para calcular o menor caminho até cada destino.
- As tabelas de roteamento são atualizadas automaticamente conforme a topologia muda.

## Exemplo de Configuração

Abaixo está um exemplo de como configurar as sub-redes e serviços no arquivo `docker-compose.yml` para este projeto.

### Redes

- Cada sub-rede é definida em `networks` usando o driver `bridge` do Docker. Esse modo permite o docker criar uma ponto na minha placa de rede.
- O bloco `ipam` define a configuração de IP para cada sub-rede, incluindo a sub-rede e o gateway.

```yaml
networks:
  subnet1:
    driver: bridge
    ipam:
      config:
      - subnet: 172.20.1.0/24
        gateway: 172.20.1.1
  subnet2:
    driver: bridge
    ipam:
      config:
      - subnet: 172.20.2.0/24
        gateway: 172.20.2.1
  subnet3:
    driver: bridge
    ipam:
      config:
      - subnet: 172.20.3.0/24
        gateway: 172.20.3.1
  subnet4:
    driver: bridge
    ipam:
      config:
      - subnet: 172.20.4.0/24
        gateway: 172.20.4.1
```

### Serviços (Roteadores e Hosts)

- Cada roteador conecta-se aos seus vizinhos de sub-rede e informa seus vizinhos via variável de ambiente.
- Os hosts se conectam à sua sub-rede e usam a interface do roteador local como gateway.
- O cap_add `NET_ADMIN` é adicionado para permitir que os containers modifiquem as configurações de rede.
- Os host dormem em um loop infinito após configurar a rota padrão para o roteador.

```yaml
services:
  router1:
    build:
      context: ./router
      dockerfile: Dockerfile
    volumes:
    - ./router:/app
    networks:
      subnet1:
        ipv4_address: 172.20.1.2
      subnet2:
        ipv4_address: 172.20.2.3
    environment:
    - vizin={"router2":["172.20.2.2",1]}
    - ip_do_roteador=172.20.1.2
    - my_name=router1
    cap_add:
    - NET_ADMIN

  host11:
    build:
      context: ./host
      dockerfile: Dockerfile
    networks:
      subnet1:
        ipv4_address: 172.20.1.11
    depends_on:
    - router1
    command: /bin/bash -c "ip route del default && ip route add default via 172.20.1.2 dev eth0 && sleep infinity"
    cap_add:
    - NET_ADMIN

  host12:
    build:
      context: ./host
      dockerfile: Dockerfile
    networks:
      subnet1:
        ipv4_address: 172.20.1.12
    depends_on:
    - router1
    command: /bin/bash -c "ip route del default && ip route add default via 172.20.1.2 dev eth0 && sleep infinity"
    cap_add:
    - NET_ADMIN

  router2:
    build:
      context: ./router
      dockerfile: Dockerfile
    volumes:
    - ./router:/app
    networks:
      subnet1:
        ipv4_address: 172.20.1.4
      subnet2:
        ipv4_address: 172.20.2.2
      subnet3:
        ipv4_address: 172.20.3.3
    environment:
    - vizin={"router1":["172.20.1.2",1],"router3":["172.20.3.2",1]}
    - ip_do_roteador=172.20.2.2
    - my_name=router2
    cap_add:
    - NET_ADMIN

  # ...demais hosts e roteadores seguem o mesmo padrão...
```

**Resumo:**  
- Cada roteador conecta-se a duas ou mais sub-redes e informa seus vizinhos via variável de ambiente.
- Cada host conecta-se à sua sub-rede e utiliza o roteador local como gateway.
- As redes são isoladas e configuradas para simular diferentes segmentos de uma rede real.

## Observações

- O protocolo UDP foi escolhido para comunicação entre roteadores por ser simples e rápido. e não requerer conexão que pode ser demorada.



