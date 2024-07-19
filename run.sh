#!/bin/bash

cleanup() {
    lsof -t -i:5500 | xargs kill -9 2>/dev/null || true
    exit 0
}

trap cleanup INT

OS=$(uname)
echo "Detected OS: $OS"

if [[ "$OS" == "Darwin" ]]; then
    echo "Running on macOS"
    if ! command -v brew &>/dev/null; then
        echo "Homebrew not found, installing..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew list python &>/dev/null || brew install python
    brew list chrome-cli &>/dev/null || brew install chrome-cli
    python_bin="python3"
    chrome_cmd="chrome-cli"
elif [[ "$OS" == "Linux" ]]; then
    echo "Running on Linux"
    if ! command -v python3 &>/dev/null; then
        echo "Python3 not found, installing..."
        sudo apt-get update
        sudo apt-get install -y python3 python3-venv
    fi
    python_bin="python3"
    chrome_cmd="google-chrome"
elif [[ "$OS" == "MINGW"* || "$OS" == "CYGWIN"* || "$OS" == "MSYS"* ]]; then
    echo "Running on Windows"
    if ! command -v python &>/dev/null; then
        echo "Python not found, please install Python. https://www.python.org/downloads/"
        exit 1
    fi
    python_bin="python"
    chrome_cmd="chrome"
else
    echo "Unsupported OS"
    exit 1
fi

$python_bin -m venv venv
source venv/bin/activate || { echo "Failed to activate virtual environment"; exit 1; }
p="venv/bin/python"

$p -m pip install --upgrade pip &>/dev/null
$p -m pip install -r requirements.txt

bvh_dir="output_BVH_NBA"
output_dir="babylon_viewer"
players_csv="data/players 1_NBA.csv"
ball_csv="data/Ball_Track.csv"
field_obj="rendering/court.obj"
$p convert_scripts/bvh_to_glb.py $bvh_dir $output_dir $players_csv $ball_csv $field_obj 2>/dev/null

cd babylon_viewer
id=$(chrome-cli list links | grep 'localhost:5500' | awk -F'[:\\]]' '{print $2}' | awk '{print $1}')
echo "Starting HTTP server..."
p="../venv/bin/python"
$p -m http.server 5500 &
HTTP_SERVER_PID=$!
sleep 0.5

if [[ -z "$id" ]]; then
    if [[ "$OS" == "Darwin" ]]; then
        open http://localhost:5500/
    elif [[ "$OS" == "Linux" ]]; then
        xdg-open http://localhost:5500/
    elif [[ "$OS" == "MINGW"* || "$OS" == "CYGWIN"* || "$OS" == "MSYS"* ]]; then
        start http://localhost:5500/
    fi
else
    $chrome_cmd activate -t $id
    $chrome_cmd reload -t $id
fi

wait $HTTP_SERVER_PID
cd ..
