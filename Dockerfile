FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Athens 
WORKDIR /rot
COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install -y python3-pip libglib2.0-0
RUN pip3 install -r requirements.txt
COPY serrano_rot/ serrano_rot/
COPY setup.py .
RUN python3 setup.py install 
RUN mkdir -p ~/.rot
COPY serrano_rot/engine.json /root/.rot/engine.json
COPY serrano_rot/rot.json /root/.rot/config.json
COPY serrano_rot/rot.db /root/.rot/rot.db
