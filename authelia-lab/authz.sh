#!/bin/bash
# usage: authz.sh <implementation> <target-url> [cookie-jar]
export no_proxy="$(cat ~/workspace/authelia-lab-work/run/no_proxy.txt)"
CA=~/workspace/authelia-lab-work/run/certs/ca.crt
IMPL=$1; URL=$2; JAR=$3
URI=$(echo $URL | sed 's|https://[^/]*||'); [ -z "$URI" ] && URI=/
ARGS=(-s --max-time 15 --cacert "$CA" --resolve auth.lab.local:9091:127.0.0.1
  -H "X-Original-URL: $URL" -H "X-Original-Method: GET"
  -H "X-Forwarded-Method: GET" -H "X-Forwarded-Proto: https" -H "X-Forwarded-Host: $(echo $URL | sed 's|https://||;s|/.*||')"
  -H "X-Forwarded-Uri: $URI" -H "Accept: text/html")
[ -n "$JAR" ] && ARGS+=(-b "$JAR")
curl "${ARGS[@]}" -D - -o /dev/null "https://auth.lab.local:9091/api/authz/$IMPL" \
  | grep -iE '^HTTP/|^remote-|^location:|^www-authenticate' | sed 's/\r$//'
