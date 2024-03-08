FROM python:3.10-slim-bullseye
WORKDIR /api
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ .
CMD python manage.py migrate && daphne -b 0.0.0.0 tennis.asgi:application