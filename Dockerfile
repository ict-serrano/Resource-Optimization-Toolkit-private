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
