#!/bin/sh
cd $(pwd) || exit
brew list python &>/dev/null || brew install python
brew list chrome-cli &>/dev/null || brew install chrome-cli
python -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip &>/dev/null
python -m pip install -r requirements.txt
venv/bin/python convert/bvh_to_glb.py
cd babylon_viewer
lsof -t -i:5500 | xargs kill -9 2>/dev/null || true
id=$(chrome-cli list links | grep 'localhost:5500' | awk -F'[:\\]]' '{print $2}' | awk '{print $1}')
python -m http.server 5500 &
sleep 1
chrome-cli close -t $id
open http://localhost:5500/
cd ..
