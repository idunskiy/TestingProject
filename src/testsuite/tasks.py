from celery import shared_task

@shared_task
def run_slow():
    import time
    time.sleep(10)
    print('REALLY DONE!')