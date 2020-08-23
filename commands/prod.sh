#!/bin/bash

gunicorn -w $NUM_WORKERS app.wsgi:application -b 0:$WSGI_PORT --log-level $LOG_LEVEL