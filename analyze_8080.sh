#!/bin/bash

IP_LIST=("192.168.51.7" "192.168.51.11" "192.168.51.15" "192.168.51.23" "192.168.51.44" "192.168.51.45" "192.168.51.47" "192.168.51.54")
PATHS=("/" "/console" "/login" "/admin" "/jenkins" "/dashboard" "/ui" "/api" "/metrics")

echo "[*] Inizio scansione 8080..." > scan_8080_risposte.txt

for ip in "${IP_LIST[@]}"; do
  echo -e "\n==============================" | tee -a scan_8080_risposte.txt
  echo "[+] Analizzo $ip:8080" | tee -a scan_8080_risposte.txt
  echo "------------------------------" | tee -a scan_8080_risposte.txt

  for path in "${PATHS[@]}"; do
    echo -e "\n🔍 Testing $ip$path" | tee -a scan_8080_risposte.txt
    curl -s -i --connect-timeout 3 "http://$ip:8080$path" | tee -a scan_8080_risposte.txt
    echo -e "\n" | tee -a scan_8080_risposte.txt
  done
done

echo -e "\n[*] Fine scansione. Vedi scan_8080_risposte.txt"
