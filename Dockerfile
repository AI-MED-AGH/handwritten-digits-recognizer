FROM python:3.13

WORKDIR /app

ENV PIP_DEFAULT_TIMEOUT=1000

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]
