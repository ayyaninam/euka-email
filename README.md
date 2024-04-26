# Euka Email

## Running locally

`python manage.py runserver`
`redis-server`
`celery -A euka_email worker --loglevel=INFO`
`celery -A euka_email beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler`