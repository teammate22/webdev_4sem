import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webdev_4sem.settings')

app = Celery('webdev_4sem')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
