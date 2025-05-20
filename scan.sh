#!/bin/bash
echo "[*] Scansione rete in corso..." > risultati.txt

for ip in $(seq 1 254); do
  for port in 22 80 443 3000 5000 7001 8080 8443 10250 2379; do
    nc -zvw1 192.168.51.$ip $port 2>&1 | grep succeeded && echo "✅ 192.168.51.$ip:$port" | tee -a risultati.txt
  done
done

echo "[*] Fine scansione. Risultati in risultati.txt"
