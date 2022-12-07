FROM python:3.10.1-slim-buster
RUN apt-get update -y
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["app.py"]