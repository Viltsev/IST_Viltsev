FROM python:latest
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install poetry
COPY pyproject.toml poetry.lock /app/

RUN poetry lock

RUN poetry install
COPY . /app/