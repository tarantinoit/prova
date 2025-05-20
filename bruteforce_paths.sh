#!/bin/bash

TARGET="192.168.51.47"
PORT="8080"

WORDLIST=(
  "" "console" "login" "admin" "dashboard" "ui" "api" "metrics"
  "health" "ready" "live" "version" "debug" "status"
  ".env" ".git" ".svn" ".DS_Store" ".well-known"
  "robots.txt" "config" "setup" "actuator"
)

echo "[*] Inizio bruteforce su http://$TARGET:$PORT/"
echo "[*] Testo ${#WORDLIST[@]} path comuni"
echo

for path in "${WORDLIST[@]}"; do
  url="http://$TARGET:$PORT/$path"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  if [[ "$code" != "404" ]]; then
    echo "[$code] /$path"
  fi
done
