FROM mcr.microsoft.com/cbl-mariner/base/python:3.9

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/usr/src

WORKDIR /usr/src

COPY ./requirements.txt  ./

RUN pip install --upgrade pip \
    && pip install -r requirements.txt
