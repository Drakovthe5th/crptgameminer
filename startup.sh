#!/bin/bash

gunicorn --worker-tmp-dir /dev/shm --workers 2 --threads 4 --worker-class gthread flask_app:create_app