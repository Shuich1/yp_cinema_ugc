FROM python:3.10

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH '/opt/app'

COPY requirements.txt requirements.txt

RUN apt-get update -y \
	 &&	pip install --upgrade pip \
     && pip install -r requirements.txt 

COPY . .

EXPOSE 5000

ENTRYPOINT [ "bash", "/opt/app/docker_init/docker-entrypoint.sh" ]
