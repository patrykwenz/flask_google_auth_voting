#!/bin/sh

# Script launches Flask application (through CherryPy) on production WSGI server for nginx reverse proxy
gunicorn --bind=unix:/tmp/gunicorn.sock --workers=1 cherry-app:app
