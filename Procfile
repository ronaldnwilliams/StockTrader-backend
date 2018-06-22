web: gunicorn stock_site.wsgi
worker: python manage.py celery worker -B -l info
