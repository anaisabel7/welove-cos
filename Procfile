web: sh -c 'cd ./welove_cos && exec gunicorn welove_cos.wsgi --preload --workers 1'
worker: sh -c 'cd ./welove_cos && exec celery -A welove_cos worker --beat --scheduler django_celery_beat.schedulers:DatabaseScheduler -l info'
