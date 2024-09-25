# app/Dockerfile

FROM python:3.10.10-slim

WORKDIR /app

#RUN apt-get update && apt-get install -y \
#    build-essential \
#    curl \
#    software-properties-common \
#    git \
#    && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y build-essential
RUN apt-get install -y g++ wget vim
RUN pip install --upgrade pip
RUN pip install --no-cache-dir wheel
RUN pip install --no-cache-dir hdbscan
RUN apt-get clean \
    && apt-get autoclean \
    && apt-get autoremove --purge  -y

COPY ./ /app/
RUN chown -R root:root ./

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e ./
