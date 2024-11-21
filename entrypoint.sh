#!/bin/bash

# Uncomment the following line to run migrations at startup
# alembic --config app/alembic.ini upgrade head

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload