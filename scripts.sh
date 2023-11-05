#!/bin/bash
activate() {
    source ~/.venv/cat_cam/bin/activate
}

install() {
    pip install -r requirements.txt
}

run() {
    activate
    gunicorn -w 1 -b 0.0.0.0 app:app --timeout 90
}

createNew() {
    python -m venv --system-site-packages ~/.venv/cat_cam
    activate
    install
    echo "To run use: ./scripts.sh run"
}

"$@"
