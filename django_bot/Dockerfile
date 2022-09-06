FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD ./django_bot/requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/

