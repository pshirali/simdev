FROM python:latest

RUN apt-get update -qq
RUN apt install -y net-tools httpie

RUN mkdir /simdev
WORKDIR /simdev

RUN pip install --upgrade pip
COPY . /simdev
RUN make install-all

ENTRYPOINT ["sleep", "infinity"]
