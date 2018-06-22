release: python manage.py migrate --log-file -
web: gunicorn stock_site.wsgi
worker: celery -A stock_site worker
