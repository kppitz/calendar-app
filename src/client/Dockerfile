ARG PYTHON_VERSION=3.10.2
FROM python:${PYTHON_VERSION}-slim as base

ENV AWS_SHARED_CREDENTIALS_FILE=~/.aws/credentials
ENV AWS_CONFIG_FILE=~/.aws/config

EXPOSE 8080

RUN mkdir -p /src/client
WORKDIR /src/client

COPY requirements.txt /src/client/
RUN pip install --no-cache-dir -U pip
RUN pip install --no-cache-dir -r requirements.txt


COPY . /src/client

CMD ["python3", "./client.py"]