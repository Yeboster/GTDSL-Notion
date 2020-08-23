FROM python:3.8-slim-buster

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# App envs
ENV NOTION_TOKEN ""
ENV INBOX_URL ""
ENV TASKS_URL ""
ENV PROJECTS_URL ""
ENV ENVIRONMENT "production"

WORKDIR /app

# Install pipenv
RUN python -m pip install pipenv
COPY Pipfile* ./
COPY gtdsl/gcalendar gtdsl/gcalendar
RUN python -m pipenv install --system --deploy

COPY . /app

RUN useradd appuser && chown -R appuser /app 
RUN mkdir /home/appuser && chown -R appuser /home/appuser
USER appuser


CMD ["python", "app.py"]
