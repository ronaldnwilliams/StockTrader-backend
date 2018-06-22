release: python manage.py migrate
web: gunicorn stock_site.wsgi
worker: celery -A stock_site worker
