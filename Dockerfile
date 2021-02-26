FROM python:3.9-slim-buster

COPY main.py /main.py

ENTRYPOINT ["python", "/main.py"]