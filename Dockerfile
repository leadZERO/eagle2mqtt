FROM alpine:3
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apk add --no-cache python3 py3-pip
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip3 --no-cache install -r requirements.txt
COPY ./eagle2mqtt.py .

CMD ["python3", "eagle2mqtt.py"]
