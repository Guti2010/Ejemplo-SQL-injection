FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir flask==3.0.3

COPY . /app
EXPOSE 5000
CMD ["python", "app.py"]
