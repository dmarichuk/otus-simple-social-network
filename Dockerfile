FROM python:3.10.4-alpine3.16

WORKDIR /app

COPY ./*.py .
COPY ./.env .
COPY ./requirements.txt .
# Installing uvloop dependencies
RUN apk add --update --no-cache make gcc g++ python3-dev musl-dev 

RUN pip3 install -U --no-cache-dir setuptools pip
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]