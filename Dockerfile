FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Athens 
RUN apt-get update && apt-get install -y python3-pip libglib2.0-0
RUN useradd -m serrano
RUN mkdir -p /etc/serrano
USER serrano
WORKDIR /home/serrano
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY serrano_rot/ serrano_rot/
COPY setup.py .
RUN python3 setup.py install --user
RUN mkdir -p /home/serrano/.rot
COPY serrano_rot/rot.db /home/serrano/.rot/rot.db
COPY serrano_rot/engine.json /home/serrano/.rot/engine.json
COPY serrano_rot/controller.json /home/serrano/.rot/controller.json
USER root
COPY serrano_rot/controller.json /etc/serrano/controller.json
COPY serrano_rot/engine.json /etc/serrano/engine.json
RUN chmod 666 /etc/serrano/engine.json
RUN chmod 666 /etc/serrano/controller.json
RUN chmod 666 /home/serrano/.rot/rot.db
USER serrano