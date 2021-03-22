FROM python:3.9-slim-buster
RUN pip install requests
COPY app/main.py /main.py
ENTRYPOINT ["python", "/main.py"]