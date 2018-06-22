release: python manage.py migrate
web: gunicorn stock_site.wsgi
worker: celery worker --app=tasks.app
