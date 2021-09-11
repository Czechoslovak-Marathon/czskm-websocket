FROM python:3.9.7-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY czskm-ws.py czskm-ws.py

CMD [ "python3", "czskm-ws.py" ]
