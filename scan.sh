#!/bin/bash
for ip in $(seq 1 254); do
  for port in 22 80 443 8080 8443 30000 10250 2379; do
    nc -zvw1 192.168.51.$ip $port 2>&1 | grep -q succeeded && echo "✅ $ip:$port"
  done
done
