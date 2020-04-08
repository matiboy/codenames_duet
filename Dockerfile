FROM python:3.8-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apt update
RUN apt install git
ENV FLASK_ENV=development
ENV FLASK_APP=main
WORKDIR /code