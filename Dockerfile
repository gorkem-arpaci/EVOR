FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY ./services ./services
COPY ./data ./data



ENV FLASK_APP=app/app.py
ENV PYTHONPATH=/app

CMD ["python", "app/app.py"]
