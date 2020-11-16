#!/bin/sh

# Script launches Flask application on production WSGI server for nginx reverse proxy
gunicorn --bind=unix:/tmp/gunicorn.sock --workers=4 app:app
