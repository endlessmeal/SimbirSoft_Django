FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY ./requirements-celery.txt /code
RUN pip3 install -r requirements-celery.txt
COPY . /code/app/celery
COPY . /code/app/models
COPY . /code/app/views
COPY . /code/app/db

WORKDIR /code/app/celery
CMD celery -A app.celery.tasks worker -P celery_pool_asyncio:TaskPool --loglevel=info
COPY . /code/