#!/bin/sh
export PYTHONPATH=$(pwd)

if [ "$APP__DEV_MODE" = "true" ]; then
    echo "Bot starting in dev mode..."
    pymon app/__main__.py
else
    echo "Bot starting in prod mode..."
    python -m app
fi
