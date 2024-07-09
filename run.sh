#!/bin/sh
cd $(pwd) || exit
python -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
venv/bin/python convert/bvh_to_glb.py
cd babylon_viewer
lsof -t -i:5500 | xargs kill -9 2>/dev/null || true
python -m http.server 5500 &
sleep 1
open http://localhost:5500/
cd ..
