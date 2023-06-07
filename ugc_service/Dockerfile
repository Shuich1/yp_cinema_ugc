FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV APP_HOME=/ugc_service
ENV APP_USER=web
ENV PYTHONPATH $APP_HOME

WORKDIR $APP_HOME

RUN groupadd -r $APP_USER && \
    useradd -r -g $APP_USER -d $APP_HOME -s /sbin/nologin -c "Docker image user" $APP_USER

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt

COPY . .

EXPOSE 8000

RUN chown -R $APP_USER:$APP_USER $APP_HOME
USER $APP_USER

ENTRYPOINT ["bash", "entrypoint.sh"]