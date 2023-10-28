#!/bin/bash
activate() {
    source ~/.venv/arthur_api/bin/activate
}

install() {
    pip install -r requirements.txt
}

run() {
    activate
    gunicorn -w 1 -b 0.0.0.0 app:app --timeout 90
}

createNew() {
    python -m venv ~/.venv/arthur_api
    activate
    install
    echo "To run use: ./scripts.sh run"
}

"$@"
