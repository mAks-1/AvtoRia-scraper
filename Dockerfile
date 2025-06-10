FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

COPY .pgpass /root/.pgpass
RUN chmod 600 /root/.pgpass

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y postgresql-client

COPY . .

CMD ["python", "-m", "app.scheduler"]
