FROM python:3.9

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /code
COPY . /code/
RUN apt-get update && apt-get install -y \
    libgeos-dev

RUN  pip install pipenv  \
    && pipenv lock --keep-outdated --requirements > requirements.txt \
    && pip install -r requirements.txt

RUN chmod +x wait-for-it.sh

EXPOSE 8000  