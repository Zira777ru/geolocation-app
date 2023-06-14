# Dockerfile
FROM python:3.10

COPY requirements.txt .
RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7777

CMD ["uvicorn", "app:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "7777"]