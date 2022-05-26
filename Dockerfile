FROM python:3.8.10

ADD . /src
WORKDIR /src

RUN apt-get update; apt-get install -y postgresql-client; rm -rf /var/cache/apt
