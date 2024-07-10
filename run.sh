#!/bin/bash
cleanup() {
    lsof -t -i:5500 | xargs kill -9 2>/dev/null || true
    exit 0
}

trap cleanup INT
cd $(pwd) || exit
brew list python &>/dev/null || brew install python
brew list chrome-cli &>/dev/null || brew install chrome-cli
python -m venv venv
source venv/bin/activate || { echo "Failed to activate virtual environment"; exit 1; }
p="venv/bin/python"
$p -m pip install --upgrade pip &>/dev/null
$p -m pip install -r requirements.txt
$p convert/bvh_to_glb.py
cd babylon_viewer
id=$(chrome-cli list links | grep 'localhost:5500' | awk -F'[:\\]]' '{print $2}' | awk '{print $1}')
p="../venv/bin/python"
echo "Starting HTTP server..."
$p -m http.server 5500 &
HTTP_SERVER_PID=$!
sleep 0.5
if [ -z "$id" ]; then
    open http://localhost:5500/
else
    chrome-cli activate -t $id
    chrome-cli reload -t $id
fi
wait $HTTP_SERVER_PID
cd ..
