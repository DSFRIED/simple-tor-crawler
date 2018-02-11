#!/bin/bash

docker run --name='tor-privoxy' -d \
      -p 9050:9050 \
      -p 8118:8118 \
    dockage/tor-privoxy:latest

sudo pip3 install -r requirements.txt

python3 ./simple_tor_crawler.py