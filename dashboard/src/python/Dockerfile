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
RUN pip install --upgrade pip

COPY ./data /app/data
COPY ./models /app/models
COPY ./src /app/src
COPY ./requirements.txt /app/
COPY ./topic_search.py /app/

RUN pip install hdbscan
RUN pip install -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

#ENTRYPOINT ["python","-m", "streamlit", "run", "topic_search.py", "--server.port=8501", "--server.address=0.0.0.0", "--browser.serverAddress=geco.deib.polimi.it/cortoviz","--browser.serverPort=80", "--server.enableCORS=false"]
ENTRYPOINT ["python","-m", "streamlit", "run", "topic_search.py", "--server.enableCORS=false","--server.enableXsrfProtection=false","--server.enableWebsocketCompression=true"]
