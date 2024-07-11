ARG PYTHON_VERSION=3.10.2
FROM python:${PYTHON_VERSION}-slim as base

ENV AWS_SHARED_CREDENTIALS_FILE=/root/.aws/credentials
ENV AWS_CONFIG_FILE=/root/.aws/config

EXPOSE 8080

RUN mkdir -p /src/appointment-handler
WORKDIR /src/appointment-handler

COPY requirements.txt /src/appointment-handler/
RUN pip install --no-cache-dir -U pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . /src/appointment-handler

CMD ["python3", "./appointment_handler.py"]