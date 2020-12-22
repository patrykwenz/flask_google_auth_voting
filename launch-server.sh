# Script launches Flask application (through CherryPy) on production WSGI server for nginx reverse proxy
cd /var/www/evoting/
gunicorn3 --bind=unix:/tmp/gunicorn.sock --workers=1 cherry-app:app
