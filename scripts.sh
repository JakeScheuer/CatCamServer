#!/bin/bash

createVenv(){
    python -m venv --system-site-packages ~/.venv/cat_cam
}

activate() {
    source ~/.venv/cat_cam/bin/activate
}

install() {
    pip install -r requirements.txt
}

run() {
    gunicorn -w 2 -b 0.0.0.0 app:app --timeout 90
}

"$@"
