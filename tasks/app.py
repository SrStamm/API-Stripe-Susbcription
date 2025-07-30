from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

redis_url = os.getenv("REDIS_URL")

celery_app = Celery("tasks", broker=redis_url)

# DEBUG: Forzar importación para ver si el módulo es accesible
try:
    import tasks.invoice
    import tasks.customer
    import tasks.subscriptions

    print("DEBUG: tasks.invoice and tasks.customer successfully imported directly.")
except ImportError as e:
    print(f"DEBUG: Failed to import task modules: {e}")

celery_app.autodiscover_tasks(["tasks"])
