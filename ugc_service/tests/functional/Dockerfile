FROM python:3.10.9-slim-buster

COPY ./requirements.txt /requirements.txt

RUN pip install --no-cache-dir --upgrade pip -r /requirements.txt

COPY . /opt/app
WORKDIR /opt/app

CMD sh -c "pytest -v"
