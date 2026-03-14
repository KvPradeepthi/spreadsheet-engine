FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY parser.py .
COPY graph_manager.py .
COPY evaluator.py .

EXPOSE ${API_PORT}

CMD ["python", "app.py"]
