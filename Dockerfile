FROM python:3.10

WORKDIR /code/
COPY . /code/

ENV PYTHONPATH="${PYTHONPATH}:/code/"

RUN pip install -r requirements.txt
