release: python manage.py makemigrations commons; python manage.py makemigrations customers; python manage.py makemigrations catalogs; python manage.py makemigrations carts; python manage.py makemigrations products; python manage.py makemigrations orders; python manage.py migrate;
web: gunicorn --env DJANGO_SETTINGS_MODULE=config.settings.base config.wsgi
# main_worker: celery -A config worker --beat -Q uw -l info --without-gossip --without-mingle --without-heartbeat
# main_worker: celery -A config worker --beat --scheduler django_celery_beat.schedulers:DatabaseScheduler -Q uw -l info --without-gossip --without-mingle --without-heartbeat
worker: celery -A config worker -c 1 --beat -l INFO
beat: celery -A config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler