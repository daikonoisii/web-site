FROM python:3.10.0
ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
RUN mkdir ./code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
