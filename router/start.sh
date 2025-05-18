#!/bin/sh
set -e

if [ -z "$ip_do_roteador" ]; then
    echo "A variável ip_do_roteador não está definida!"
    exit 1
fi

ip route del default && ip route add default via $ip_do_roteador && python main.py