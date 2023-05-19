FROM python:3.10.9-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONWARNINGS="ignore"

COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade pip -r /requirements.txt

COPY ./src /opt/app
WORKDIR /opt/app

CMD ["python", "main.py"]
