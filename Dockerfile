# pull official base image
FROM python:3.7-alpine

# set work directory
RUN mkdir /usr/src/app
WORKDIR /usr/src/app

# activate the environment
# RUN workon yerel

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
# RUN pip install pipenv
# COPY ./Pipfile /usr/src/app/Pipfile
# RUN pipenv install --skip-lock --system --dev
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/app/
COPY ../envFile /usr/src/app/.env
