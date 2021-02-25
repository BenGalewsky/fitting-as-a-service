FROM python:3.8-buster

RUN apt-get update -y && \
    apt-get install -y \
        gcc \
        python3-dev && \
    apt-get -y autoclean && \
    apt-get -y autoremove && \
    rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt && \
    pip install "funcx-endpoint==0.0.3"
