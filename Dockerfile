FROM python:3.9-slim

WORKDIR /app
RUN useradd -m app
USER app

RUN pip install --upgrade pip
COPY ./requirements.txt /tmp/requirements.txt
RUN pip install --user -r /tmp/requirements.txt
