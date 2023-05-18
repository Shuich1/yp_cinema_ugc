FROM python:3.10.9-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 8000

ENV UGC_API_PORT=8000
ENV UGC_API_GUNICORN_WORKERS=1

COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade pip -r /requirements.txt

COPY . /opt/app
WORKDIR /opt/app

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD gunicorn \
  main:app \
  --workers ${UGC_API_GUNICORN_WORKERS} \
  --bind 0.0.0.0:${UGC_API_PORT} \
  --worker-class core.workers.UvicornWorker
