FROM python:3.8.1-slim

LABEL Author="ZequnZ"
LABEL Email="Zequn.zhou007@gmail.com"

WORKDIR  /app

COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# EXPOSE 5000