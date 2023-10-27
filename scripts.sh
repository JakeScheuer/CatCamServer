#!/bin/bash
activate() {
    source ~/.venv/arthur_api/bin/activate
}

install() {
    pip install -r requirements.txt
}

run() {
    sudo pigpiod
    gunicorn -w 4 -b 0.0.0.0 app:app
}

createNew() {
    python -m venv ~/.venv/arthur_api
    activate
    install
    echo "To run use: ./scripts.sh run"
}

"$@"
