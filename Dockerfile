FROM python:3.9-slim-buster

COPY main.py /main.py

RUN pip install requests

ENTRYPOINT ["python", "/main.py"]