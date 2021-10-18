FROM python:3.9-slim

WORKDIR /worker

RUN  pip install --upgrade pip

RUN useradd -m worker
USER worker

COPY ./requirements.txt /tmp/requirements.txt

RUN pip install --user -r /tmp/requirements.txt
