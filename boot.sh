#!/bin/bash

gunicorn -b 0.0.0.0:5000 \
    --access-logfile - \
    --error-logfile - \
    --reload \
    --daemon \
    wsgi:server
