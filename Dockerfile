#FROM pyhf/pyhf:latest-stable
FROM python:3.6-buster

RUN  apt-get update -y; apt-get install -y gcc python3-dev
COPY requirements.txt .
RUN pip install -r requirements.txt && pip install funcx-endpoint
