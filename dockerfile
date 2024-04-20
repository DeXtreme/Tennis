FROM python:3.10-slim-bullseye
WORKDIR /api
RUN pip install pipenv
COPY Pipfile.lock .
RUN pipenv sync
COPY src/ .
CMD pipenv run python manage.py migrate && pipenv run python manage.py collectstatic --no-input && pipenv run daphne -b 0.0.0.0 tennis.asgi:application