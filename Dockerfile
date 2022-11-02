FROM ictserrano/serrano:ubuntu-v1.0
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