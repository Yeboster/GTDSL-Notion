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

# Add custom user, coz pip is not happy without
RUN useradd appuser && chown -R appuser /app && mkdir /home/appuser && chown -R appuser /home/appuser 
USER appuser

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

COPY . /app


CMD ["python", "app.py"]
